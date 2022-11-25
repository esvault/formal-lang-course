import enum
from collections import defaultdict, deque

from networkx import MultiGraph
from pyformlang.cfg import CFG, Variable, Terminal

from project.cfg.cfpq_algo import Algo


def cfpq(
    graph: MultiGraph,
    cfg: CFG,
    start_nodes: set = None,
    final_nodes: set = None,
    start_symbol: Variable = Variable("S"),
    algo=Algo.hellings
):

    cfg._start_symbol = start_symbol

    if not start_nodes:
        start_nodes = graph.nodes

    if not final_nodes:
        final_nodes = graph.nodes


    result = set()
    for i, v, j in algo(cfg, graph):
        if v == start_symbol and i in start_nodes and j in final_nodes:
            result.add((i, j))

    return result
