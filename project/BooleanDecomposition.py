from pyformlang.finite_automaton import (
    FiniteAutomaton,
    DeterministicFiniteAutomaton,
    State,
    Symbol,
    NondeterministicFiniteAutomaton,
)

import scipy.sparse as ss
import numpy as np


class BooleanDecomposition:
    """ """

    def __init__(self, automata: FiniteAutomaton = None):
        if automata is not None:
            self.states = automata.states
            self.start_states = automata.start_states
            self.final_states = automata.final_states
            self.num_of_states = len(automata.states)
            self.indexed_states = {
                state: index for index, state in enumerate(self.states)
            }
            self.boolean_matrices = self.get_boolean_matrices(automata)
            print(automata.to_dict())

        else:
            self.states = set()
            self.start_states = set()
            self.final_states = set()
            self.num_of_states = 0
            self.indexed_states = dict()
            self.boolean_matrices = dict()

    def get_boolean_matrices(self, automata):
        automata_dict = automata.to_dict()
        matrices = {
            symbol: ss.lil_matrix((self.num_of_states, self.num_of_states), dtype=bool)
            for symbol in automata.symbols
        }
        for from_state, transitions in automata_dict.items():
            for symbol, to_states in transitions.items():
                for to_state in to_states:
                    from_index = self.indexed_states[from_state]
                    to_index = self.indexed_states[to_state]
                    matrices[symbol][from_index, to_index] = 1

        return matrices

    def intersection(self, other):
        result = BooleanDecomposition()

        symbols = self.boolean_matrices.keys() & other.boolean_matrices.keys()

        for symbol in symbols:
            result.boolean_matrices[symbol] = ss.kron(
                self.boolean_matrices[symbol],
                other.boolean_matrices[symbol],
                format="lil",
            )

        result.num_of_states = self.num_of_states * other.num_of_states

        for left_state, left_index in self.indexed_states.items():
            for right_state, right_index in other.indexed_states.items():
                state = left_state * other.num_of_states + right_state
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


if __name__ == "__main__":
    min_dfa = NondeterministicFiniteAutomaton({State(0), State(1), State(2)})

    min_dfa.add_start_state(State(0))
    min_dfa.add_final_state(State(1))

    min_dfa.add_transitions(
        [
            (State(0), Symbol("a"), State(1)),
            (State(1), Symbol("b"), State(1)),
            (State(0), Symbol("b"), State(1)),
            (State(0), Symbol("a"), State(2)),
        ]
    )

    dfa = NondeterministicFiniteAutomaton()
    dfa.add_transitions([(State(0), Symbol("a"), State(0))])

    bd = BooleanDecomposition(min_dfa)
    bd2 = BooleanDecomposition(dfa)

    bd.intersection(bd2)
    for symbol, matrix in bd.boolean_matrices.items():
        print(symbol, matrix.toarray())
    print("main")
