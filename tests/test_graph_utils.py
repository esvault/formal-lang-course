import filecmp
import os

import pydot
import pytest
from project.graph import *  # on import will print something from __init__ filez


def setup_module(module):
    print("basic setup module")


def teardown_module(module):
    print("basic teardown module")


# def test_get_graph_info():
#     (n, e, lab) = get_graph_info("bzip")
#     assert n == 632 and e == 556 and lab == {"A", "D"}


def test_two_cycles_graph_to_file1():
    """Check that after saving graph isn't changed"""
    filename = os.path.join("assets", "test.dot")

    save_graph_to_file(generate_two_cycles_graph(10, 14, ("H", "M")), filename)

    g = pydot.graph_from_dot_file(filename)[0]

    os.remove(filename)

    assert len(list(g.get_nodes())) == 26


def test_two_cycles_graph_to_file2():
    filename = os.path.join("assets", "test.dot")

    save_graph_to_file(generate_two_cycles_graph(3, 2, ("A", "C")), filename)

    try:
        assert filecmp.cmp(filename, os.path.join("assets", "correct.dot"))
    except AssertionError:
        return
    finally:
        os.remove(filename)
