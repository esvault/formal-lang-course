import numpy as np
from scipy import sparse
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State, Symbol

from project.reg_ex.boolean_decomposition import BooleanDecomposition


def dicts_equal(d1: dict, d2: dict):
    for k in d1.keys():
        if not np.array_equal(d1[k].todense(), d2[k].todense()):
            return False
    return True


def build_test_boolean_decomposition1():
    nfa = NondeterministicFiniteAutomaton()

    nfa.add_start_state(State(0))
    nfa.add_final_state(State(1))

    nfa.add_transitions(
        [
            (State(0), Symbol("a"), State(1)),
            (State(0), Symbol("b"), State(1)),
            (State(0), Symbol("a"), State(2)),
            (State(1), Symbol("b"), State(1)),
        ]
    )

    return BooleanDecomposition(nfa)


def build_test_boolean_decomposition2():
    nfa = NondeterministicFiniteAutomaton()

    nfa.add_start_state(State(0))
    nfa.add_final_state(State(2))

    nfa.add_transitions(
        [
            (State(0), Symbol("a"), State(1)),
            (State(1), Symbol("b"), State(2)),
        ]
    )

    return BooleanDecomposition(nfa)


def test_correct_bool_matrices():
    boolean_decomposition = build_test_boolean_decomposition1()

    a_matrix = np.array(
        [[False, True, True], [False, False, False], [False, False, False]]
    )

    b_matrix = np.array(
        [[False, True, False], [False, True, False], [False, False, False]]
    )

    expected_result = {
        "a": sparse.csr_matrix(a_matrix),
        "b": sparse.csr_matrix(b_matrix),
    }

    assert dicts_equal(boolean_decomposition.boolean_matrices, expected_result)


def test_expected_symbols_are_accepted():
    nfa = build_test_boolean_decomposition1().to_nfa()

    expected_strings = [
        [Symbol("a")],
        [Symbol("a"), Symbol("b")],
        [Symbol("a"), Symbol("b"), Symbol("b")],
    ]

    assert nfa.accepts(expected_strings[0])
    assert nfa.accepts(expected_strings[1])
    assert nfa.accepts(expected_strings[2])
    assert not nfa.accepts([Symbol("c")])


def test_intersection_accept_correct_strings():
    bool_dec1 = build_test_boolean_decomposition1()
    bool_dec2 = build_test_boolean_decomposition2()

    intersection = bool_dec1.intersection(bool_dec2)

    nfa = intersection.to_nfa()

    assert nfa.accepts([Symbol("a"), Symbol("b")])
