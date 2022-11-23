from networkx import MultiGraph
from pyformlang.cfg import CFG

from project.cfpq import cfpq_matrix

cfgs = list(
    map(
        lambda x: CFG.from_text(x),
        [
            """
        S -> $
    """,
            """
        S -> a S b S | $
    """,
        ],
    )
)

not_empty_graph = MultiGraph()
not_empty_graph.add_edges_from([(0, 1, {"label": "a"}), (1, 2, {"label": "b"})])

graphs = [MultiGraph(), not_empty_graph]

results = [set(), {(0, 2), (0, 0), (1, 1), (2, 2)}]


def test_cfpq():
    for i in range(1, len(cfgs)):
        assert cfpq_matrix(graphs[i], cfgs[i]).__eq__(results[i])
