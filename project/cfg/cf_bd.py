from collections import defaultdict

from pyformlang.finite_automaton import State, EpsilonNFA
from scipy.sparse import dok_matrix, kron

from project.cfg.rsm import RSM


class BooleanDecomposition:
    def __init__(self, indexed_states, start_states, final_states, matrices):
        self.indexed_states = indexed_states
        self.start_states = start_states
        self.final_states = final_states
        self.matrices = matrices

    @classmethod
    def from_rsm(cls, rsm: RSM):
        states, start_states, final_states = set(), set(), set()

        for n, automata in rsm.boxes.items():
            for st in automata.states:
                state = State((n, st.value))
                states.add(state)

                if st in automata.start_states:
                    start_states.add(state)

                if st in automata.final_states:
                    final_states.add(state)

        indexed_states = {s: i for i, s in enumerate(states)}
        matrices = defaultdict(
            lambda: dok_matrix((len(states), len(states)), dtype=bool)
        )

        for non_term, automata in rsm.boxes.items():
            for state_from, transitions in automata.to_dict().items():
                for label, states_to in transitions.items():
                    states_to = states_to if isinstance(states_to, set) else {states_to}
                    for state_to in states_to:
                        matrices[label.value][
                            indexed_states[State((non_term, state_from.value))],
                            indexed_states[State((non_term, state_to.value))],
                        ] = True

        return cls(indexed_states, start_states, final_states, matrices)

    @classmethod
    def from_automata(cls, automata: EpsilonNFA):
        indexed_states = {state: index for index, state in enumerate(automata.states)}

        matrices = defaultdict(
            lambda: dok_matrix((len(automata.states), len(automata.states)), dtype=bool)
        )

        for label in automata.symbols:
            dok_mtx = dok_matrix(
                (len(automata.states), len(automata.states)), dtype=bool
            )
            for state_from, transitions in automata.to_dict().items():
                states_to = transitions.get(label, set())
                if not isinstance(states_to, set):
                    states_to = {states_to}
                for state_to in states_to:
                    dok_mtx[indexed_states[state_from], indexed_states[state_to]] = True

            matrices[label] = dok_mtx

        return cls(
            indexed_states,
            automata.start_states.copy(),
            automata.final_states.copy(),
            matrices,
        )

    def intersect(self, other: "BooleanDecomposition"):
        n_matrices = {
            label: kron(self.matrices[label], other.matrices[label])
            for label in (self.matrices.keys() & other.matrices.keys())
        }

        n_indexed_states = dict()
        n_start_states = set()
        n_final_states = set()

        for self_state, self_idx in self.indexed_states.items():
            for other_state, other_idx in other.indexed_states.items():
                state = State((self_state.value, other_state.value))
                idx = self_idx * len(other.indexed_states) + other_idx
                n_indexed_states[state] = idx
                if (
                    self_state in self.start_states
                    and other_state in other.start_states
                ):
                    n_start_states.add(state)
                if (
                    self_state in self.final_states
                    and other_state in other.final_states
                ):
                    n_final_states.add(state)

        return BooleanDecomposition(
            n_indexed_states, n_start_states, n_final_states, n_matrices
        )

    def transitive_closure(self):
        transitive_closure = sum(
            self.matrices.values(),
            start=dok_matrix((len(self.indexed_states), len(self.indexed_states))),
        )

        prev_nnz, cur_nnz = None, transitive_closure.nnz
        if not cur_nnz:
            return transitive_closure

        while prev_nnz != cur_nnz:
            transitive_closure += transitive_closure @ transitive_closure
            prev_nnz, cur_nnz = cur_nnz, transitive_closure.nnz

        return transitive_closure
