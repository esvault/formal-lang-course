from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, EpsilonNFA

from scipy import sparse


class BooleanDecomposition:
    """
    This class is representation of graph as set of boolean matrices.
    """

    def __init__(self, automata: EpsilonNFA = None):
        if automata is not None:
            self.states = automata.states
            self.start_states = automata.start_states
            self.final_states = automata.final_states
            self.num_of_states = len(automata.states)
            self.indexed_states = {
                state: index for index, state in enumerate(self.states)
            }
            self.boolean_matrices = self._get_boolean_matrices(automata)
        else:
            self.states = set()
            self.start_states = set()
            self.final_states = set()
            self.num_of_states = 0
            self.indexed_states = dict()
            self.boolean_matrices = dict()

    def _get_boolean_matrices(self, automata) -> dict:
        """
        Service function for building boolean matrices.

        :param automata: Origin automaton
        :return: Dict of boolean matrices
        """

        matrices = dict()

        for from_state, transitions in automata.to_dict().items():
            for symbol, to_states in transitions.items():
                if not isinstance(to_states, set):
                    to_states = {to_states}
                for to_state in to_states:
                    from_index = self.indexed_states[from_state]
                    to_index = self.indexed_states[to_state]
                    if symbol not in matrices:
                        matrices[symbol] = sparse.csr_matrix(
                            (self.num_of_states, self.num_of_states), dtype=bool
                        )
                    matrices[symbol][from_index, to_index] = True

        return matrices

    def to_nfa(self) -> NondeterministicFiniteAutomaton:
        """
        Convert dict of boolean matrices to nfa
        :return: Nfa
        """

        nfa = NondeterministicFiniteAutomaton()
        for symbol, bm in self.boolean_matrices.items():
            for first_state, second_state in zip(*bm.nonzero()):
                nfa.add_transition(first_state, symbol, second_state)

        for state in self.start_states:
            nfa.add_start_state(state)

        for state in self.final_states:
            nfa.add_final_state(state)

        return nfa

    def intersection(self, other):
        """
        Intersect two automaton using kronecker product.

        :param other: Right operand of kronecker product
        :return: Resulting automaton as BooleanDecomposition
        """

        result = BooleanDecomposition()

        symbols = self.boolean_matrices.keys() & other.boolean_matrices.keys()

        for symbol in symbols:
            result.boolean_matrices[symbol] = sparse.kron(
                self.boolean_matrices[symbol],
                other.boolean_matrices[symbol],
                format="csr",
            )

        result.num_of_states = self.num_of_states * other.num_of_states

        for left_state, left_index in self.indexed_states.items():
            for right_state, right_index in other.indexed_states.items():
                state = left_index * other.num_of_states + right_index
                result.indexed_states[state] = state

                if (
                    left_state in self.start_states
                    and right_state in other.start_states
                ):
                    result.start_states.add(state)

                if (
                    left_state in self.final_states
                    and right_state in other.final_states
                ):
                    result.final_states.add(state)

        return result

    def transitive_closure(self):
        """
        Get transitive closure of BooleanDecomposition
        :return: Transitive closure
        """

        if len(self.boolean_matrices) == 0:
            return sparse.csr_matrix((0, 0), dtype=bool)
        closure = sum(self.boolean_matrices.values())

        prev = closure.nnz
        curr = 0

        while prev != curr:
            closure += closure @ closure
            prev = curr
            curr = closure.nnz

        return closure
