from typing import Optional, AbstractSet

from networkx import MultiGraph
from pyformlang.finite_automaton import State
from pyformlang.regular_expression import Regex

from project.boolean_decomposition import BooleanDecomposition
from project.fa_utils import graph_to_epsilon_nfa, regex_to_dfa


def request_path_query(
    regex: str,
    graph: MultiGraph,
    start_nodes: set = None,
    final_nodes: set = None,
):
    graph_fa = graph_to_epsilon_nfa(graph, start_nodes, final_nodes)
    regex_fa = regex_to_dfa(regex)

    graph_bd = BooleanDecomposition(graph_fa)
    regex_bd = BooleanDecomposition(regex_fa)

    intersection = graph_bd.intersection(regex_bd)

    start_states = intersection.start_states
    final_states = intersection.final_states

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


def rpq_bfs(
    regex: str,
    graph: MultiGraph,
    start_nodes: set,
    final_nodes: set,
    is_separated: bool,
):
    """
    The function of performing regular queries to graph.
    :param regex: constraint regular expression
    :param graph: origin graph
    :param start_nodes: set of start nodes
    :param final_nodes: set of final nodes
    :param is_separated: separated: True if you want to get final vertices for every start vertex,
            False --- to get set of final vertices reachable from set of start vertices.
    :return: Reachable vertices.
    """
    graph_fa = graph_to_epsilon_nfa(graph, start_nodes, final_nodes)
    regex_fa = regex_to_dfa(regex)

    graph_bd = BooleanDecomposition(graph_fa)
    regex_bd = BooleanDecomposition(regex_fa)

    result = graph_bd.constraint_bfs(regex_bd, is_separated)

    return result
