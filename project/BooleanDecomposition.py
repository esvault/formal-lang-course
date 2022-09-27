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
            self.states = {}
            self.start_states = {}
            self.final_states = {}
            self.num_of_states = 0
            self.indexed_states = {}
            self.boolean_matrices = {}

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
                    matrices[symbol][from_index, to_index] = True

        return matrices


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
    bd = BooleanDecomposition(min_dfa)
    # for symbol, matrix in bd.boolean_matrices.items():
    #     print(symbol, np.array(matrix))
    print("main")
