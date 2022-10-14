from networkx import MultiGraph
from pyformlang.cfg import CFG, Variable

from project.hellings import hellings


def cfpq(
    graph: MultiGraph,
    cfg: CFG,
    start_nodes: set = None,
    final_nodes: set = None,
    start_symbol: Variable = Variable("S"),
):

    cfg._start_symbol = start_symbol

    if not start_nodes:
        start_nodes = graph.nodes

    if not final_nodes:
        final_nodes = graph.nodes

    result = set()
    for v, i, j in hellings(cfg, graph):
        if v == start_symbol and i in start_nodes and j in final_nodes:
            result.add((i, j))

    return result