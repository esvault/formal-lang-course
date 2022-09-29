from networkx import MultiGraph
from pyformlang.finite_automaton import State

from project.rpq import request_path_query


def generate_graph():
    graph = MultiGraph()
    graph.add_edges_from(
        [
            (0, 1, {"label": "a"}),
            (0, 3, {"label": "b"}),
            (1, 2, {"label": "b"}),
            (3, 2, {"label": "a"}),
            (2, 2, {"label": "b"}),
        ]
    )

    return graph


def test_not_degenerated_case():
    graph = generate_graph()
    regex = "a.b.b*"

    assert request_path_query(regex, graph, {State(0)}, {State(2)}) == {(0, 2)}


def test_empty_regex():
    graph = generate_graph()
    regex = ""

    assert request_path_query(regex, graph) == set()
