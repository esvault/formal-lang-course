import cfpq_data
import networkx as nx
from collections import namedtuple

from networkx import MultiGraph
from pydot import Dot
import csv


def get_graph_info_by_name(name: str):
    """Load a graph by name. Passes through it and add unique labels to set.
    :return: 3-tuple (number of nodes, number of edges, all unique edge labels)
    or None if file with passed name is not found
    """

    try:
        graph_path = cfpq_data.download(name)
        graph = cfpq_data.graph_from_csv(graph_path)
    except FileNotFoundError:
        print("File {name} not found".format(name=name))
        return

    return get_graph_info(graph)


def get_graph_info(graph: MultiGraph):
    s = set()
    for i in dict(graph.edges).values():
        for j in i.values():
            s.add(j)

    nt = namedtuple("graf_info", ["nodes", "edges", "labels"])

    return nt(graph.number_of_nodes(), graph.number_of_edges(), s)


def generate_two_cycles_graph(n1: int, n2: int, labels: tuple) -> Dot:
    """Generate two cycles graph and save it to dot file.
    :param n1: number of nodes in first cycle
    :param n2: number of nodes in second cycle
    :param labels: 2-tuple, where elements mark first and second cycles of graph according
    :return: None
    """
    g = cfpq_data.graphs.generators.labeled_two_cycles_graph(n1, n2, labels=labels)
    return nx.drawing.nx_pydot.to_pydot(g)


def save_graph_to_file(graph: Dot, filename: str):
    """
    Save DOT format graph to file.
    :param graph: Original graph
    :param filename: Name of the file
    :return: None
    """
    graph.write(filename)


def read_graph_from_csv(filename):
    graph = nx.MultiGraph()
    with open(filename) as csvfile:
        rows = csv.reader(csvfile, delimiter=" ")
        for row in rows:
            graph.add_edges_from([(int(row[0]), int(row[1]), {"label": row[2]})])

    return graph
