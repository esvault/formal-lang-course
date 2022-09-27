from typing import Optional, AbstractSet

from networkx import MultiGraph
from pyformlang.finite_automaton import State
from pyformlang.regular_expression import Regex

from project.boolean_decomposition import BooleanDecomposition
from project.fa_utils import graph_to_epsilon_nfa, regex_to_dfa


def request_path_query(
    regex: str,
    graph: MultiGraph,
    start_states: Optional[AbstractSet[State]] = None,
    finale_states: Optional[AbstractSet[State]] = None,
):
    graph_fa = graph_to_epsilon_nfa(graph, start_states, finale_states)
    regex_fa = regex_to_dfa(regex)

    graph_bd = BooleanDecomposition(graph_fa)
    regex_bd = BooleanDecomposition(regex_fa)

    intersection = graph_bd.intersection(regex_bd)

    start_states = graph_bd.start_states
    final_states = graph_bd.final_states

    closure = intersection.transitive_closure()

    result = set()
    for left, right in zip(*closure.nonzero()):
        if left in start_states and right in final_states:
            result.add(
                (
                    left // regex_bd.num_of_states,
                    right // regex_bd.num_of_states,
                )
            )

    return result
