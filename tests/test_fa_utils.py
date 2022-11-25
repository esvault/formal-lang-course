import os

import networkx as nx
import pydot
from pyformlang.finite_automaton import Symbol, State

from project.re.fa_utils import *


def test_equivalence_dfa_and_regex():
    pattern = "abc|d"
    test_automata = Regex(pattern).to_epsilon_nfa()
    dfa = regex_to_dfa(pattern)

    assert dfa.is_equivalent_to(test_automata)


def util(pattern, right, wrong):
    automata = regex_to_dfa(pattern)
    return automata.accepts(right), automata.accepts(wrong)


def test_concat():
    result = util("a.b", [Symbol("a"), Symbol("b")], [Symbol("ab")])

    assert result[0]
    assert not result[1]


def test_union():
    result = util("a|b", [Symbol("a")], [Symbol("aa")])

    assert result[0]
    assert not result[1]


def test_kleene_star():
    result = util(
        "ab*", [Symbol("ab"), Symbol("ab")], [Symbol("a"), Symbol("b"), Symbol("b")]
    )

    assert result[0]
    assert not result[1]


def test_correct_converting():
    # filename = "correct.dot"
    directory = os.path.join("tests", "assets")
    filename = os.path.join(directory, "correct.dot")
    dot = pydot.graph_from_dot_file(filename)[0]
    g = nx.drawing.nx_pydot.from_pydot(dot)
    automata = graph_to_epsilon_nfa(g)

    assert len(automata.final_states) == 7


def test_two_automata_equivalence():
    test_graph = nx.MultiGraph([(0, 1, {"label": "a"}), (1, 1, {"label": "b"})])

    test_automata = graph_to_epsilon_nfa(test_graph, {State(0)}, {State(1)})

    automata = DeterministicFiniteAutomaton()
    automata.add_transitions(
        [(State(0), Symbol("a"), State(1)), (State(1), Symbol("b"), State(1))]
    )

    automata.add_start_state(State(0))
    automata.add_final_state(State(1))

    words = [
        [Symbol("a")],
        [Symbol("a"), Symbol("b"), Symbol("b")],
        [Symbol("b"), Symbol("a")],
    ]

    for word in words:
        assert test_automata.accepts(word) == automata.accepts(word)


def test_is_minimal():
    automata = regex_to_dfa("a.b*")

    min_dfa = DeterministicFiniteAutomaton({State(0), State(1)})

    min_dfa.add_start_state(State(0))
    min_dfa.add_final_state(State(1))

    min_dfa.add_transitions(
        [(State(0), Symbol("a"), State(1)), (State(1), Symbol("b"), State(1))]
    )

    assert min_dfa.is_equivalent_to(automata)
