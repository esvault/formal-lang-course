import os

import networkx
import pydot
import pytest
from pyformlang.regular_expression import Regex

from project import fa_utils


def test_equivalence_dfa_and_regex():
    pattern = "abc|d"
    test_automata = Regex(pattern).to_epsilon_nfa()
    dfa = fa_utils.regex_to_dfa(pattern)

    assert dfa.is_equivalent_to(test_automata)


def test_correct_converting():
    # filename = "correct.dot"
    filename = os.path.join("tests", "correct.dot")
    dot = pydot.graph_from_dot_file(filename)[0]
    g = networkx.drawing.nx_pydot.from_pydot(dot)
    automata = fa_utils.graph_to_epsilon_nfa(g)

    assert len(automata.final_states) == 7
