from pyformlang.finite_automaton import (
    NondeterministicFiniteAutomaton,
    EpsilonNFA,
    State,
)

from scipy import sparse
from scipy.sparse import lil_matrix, lil_array, csr_matrix, vstack


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

    matrix_converter = lambda mat: mat.tocsr()

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
                        matrices[symbol] = BooleanDecomposition.matrix_converter(
                            sparse.csr_matrix(
                                (self.num_of_states, self.num_of_states), dtype=bool
                            )
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
            result.boolean_matrices[symbol] = BooleanDecomposition.matrix_converter(
                sparse.kron(
                    self.boolean_matrices[symbol], other.boolean_matrices[symbol]
                )
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
            return BooleanDecomposition.matrix_converter(
                sparse.csr_matrix((0, 0), dtype=bool)
            )
        closure = sum(self.boolean_matrices.values())

        prev = closure.nnz
        curr = 0

        while prev != curr:
            closure += closure @ closure
            prev = curr
            curr = closure.nnz

        return closure

    def _direct_matrix_sum(self, other: "BooleanDecomposition"):
        result = BooleanDecomposition()

        states = self.states.union(
            {State(state.value + self.num_of_states) for state in other.states}
        )

        boolean_matrices = {}

        common_symbols = set(self.boolean_matrices.keys()).intersection(
            other.boolean_matrices.keys()
        )

        for symbol in common_symbols:
            boolean_matrices[symbol] = sparse.bmat(
                [
                    [self.boolean_matrices[symbol], None],
                    [None, other.boolean_matrices[symbol]],
                ]
            )

        other_start_states = {
            State(state.value + self.num_of_states) for state in other.start_states
        }
        other_final_states = {
            State(state.value + self.num_of_states) for state in other.final_states
        }

        for left_state, left_index in self.indexed_states.items():
            for right_state, right_index in other.indexed_states.items():
                state = left_index * other.num_of_states + right_index
                result.indexed_states[state] = state

        result.states = states
        result.num_of_states = self.num_of_states + other.num_of_states
        result.start_states = {state for state in self.start_states}.union(
            other_start_states
        )
        result.final_states = {state for state in self.final_states}.union(
            other_final_states
        )
        result.boolean_matrices = boolean_matrices

        return result

    def constraint_bfs(self, constraint: "BooleanDecomposition", separated: bool):
        """
        Traverse presented graph via BFS with matrix operations and with constraint.
        :param constraint: constraint regular expression.
        :param separated: True if you want to get final vertices for every start vertex, False --- to get set of final
                vertices reachable from set of start vertices.
        :return: Reachable vertices.
        """
        k = constraint.num_of_states
        n = self.num_of_states

        start_states_indices = [
            i for i, st in enumerate(self.states) if st in self.start_states
        ]

        final_states_indices = [
            i for i, st in enumerate(self.states) if st in self.final_states
        ]

        constraint_final_state_indices = [
            i for i, st in enumerate(constraint.states) if st in constraint.final_states
        ]

        direct_sum = constraint._direct_matrix_sum(self)

        front = (
            _construct_front(self, constraint)
            if not separated
            else _construct_sep_front(self, constraint)
        )

        visited = BooleanDecomposition.matrix_converter(csr_matrix(front.shape))

        while True:
            old_visited = visited.copy()

            for _, matrix in direct_sum.boolean_matrices.items():
                if front is not None:
                    front2 = front @ matrix
                else:
                    front2 = visited @ matrix

                visited += _transform_rows(front2, k)

            front = None

            if visited.nnz == old_visited.nnz:
                break

        result = set()
        for i, j in zip(*visited.nonzero()):
            if j >= k and i % k in constraint_final_state_indices:
                if j - k in final_states_indices:
                    result.add(
                        j - k
                        if not separated
                        else (start_states_indices[i // n], j - k)
                    )

        return result


def _construct_front(graph: "BooleanDecomposition", constraint: "BooleanDecomposition"):
    n = graph.num_of_states
    k = constraint.num_of_states

    front = lil_matrix((k, n + k))

    right_part_front = lil_array(
        [[state in graph.start_states for state in graph.states]]
    )

    for _, i in constraint.indexed_states.items():
        front[i, i] = True
        front[i, k:] = right_part_front

    return BooleanDecomposition.matrix_converter(front)


def _construct_sep_front(
    graph: "BooleanDecomposition", constraint: "BooleanDecomposition"
):
    start_indexes = {
        i
        for i in range(graph.num_of_states)
        if graph.indexed_states[i] in graph.start_states
    }

    fronts = [_construct_front(graph, constraint) for i in start_indexes]

    if len(fronts) > 0:
        return BooleanDecomposition.matrix_converter(csr_matrix(vstack(fronts)))
    else:
        return BooleanDecomposition.matrix_converter(
            csr_matrix(
                (
                    constraint.num_of_states,
                    constraint.num_of_states + graph.num_of_states,
                )
            )
        )


def _transform_rows(front_part, constr_states_num: int):
    transformed_front_part = lil_array(front_part.shape)

    for i, j in zip(*front_part.nonzero()):
        if j < constr_states_num:
            non_zero_row_right = front_part.getrow(i).tolil()[[0], constr_states_num:]

            if non_zero_row_right.nnz > 0:
                row_shift = i // constr_states_num * constr_states_num
                transformed_front_part[row_shift + j, j] = 1
                transformed_front_part[
                    [row_shift + j], constr_states_num:
                ] += non_zero_row_right

    return BooleanDecomposition.matrix_converter(transformed_front_part)
