import enum
from collections import defaultdict, deque

from networkx import MultiGraph
from pyformlang.cfg import Terminal, CFG
from pyformlang.finite_automaton import EpsilonNFA
from scipy.sparse import csr_matrix, dok_matrix, eye

from project.cfg.cfg_util import cfg_to_weak_normal_form
from project.cfg.cf_bd import BooleanDecomposition
from project.cfg.ecfg import ECFG
from project.cfg.rsm import RSM


def _hellings(cfg: CFG, graph: MultiGraph):
    """
    Solves the reachability problem via the Hellings algorithm
    """

    weak_nfh = cfg_to_weak_normal_form(cfg)
    # N -> eps
    eps_non_terms = set()
    # A -> a
    term_prods = defaultdict(set)
    # C -> AB
    non_term_prods = defaultdict(set)

    for prod in weak_nfh.productions:
        if len(prod.body) == 0:
            eps_non_terms.add(prod.head)
        elif len(prod.body) == 1:
            term_prods[prod.head].add(prod.body[0])
        else:
            non_term_prods[prod.head].add((prod.body[0], prod.body[1]))

    first_set = {(i, v, i) for v in eps_non_terms for i in graph.nodes}
    second_set = {
        (i, v, j)
        for v, terms in term_prods.items()
        for i, j, label in graph.edges(data="label")
        if Terminal(label) in terms
    }

    r = first_set.union(second_set)
    m = deque(r.copy())

    while m:
        i, v, j = m.popleft()
        temp = set()
        for l, v2, k in r:
            if i == k:
                for head, body in non_term_prods.items():
                    if (v2, v) in body and (l, head, j) not in r:
                        m.append((l, head, j))
                        temp.add((l, head, j))

            if j == l:
                for head, body in non_term_prods.items():
                    if (v, v2) in body and (i, head, k) not in r:
                        m.append((i, head, k))
                        temp.add((i, head, k))

        r = r.union(temp)

    return r


def _cf_closure(cfg: CFG, graph: MultiGraph):
    """
    Solves the reachability problem via the matrix algorithm
    """
    cfg = cfg_to_weak_normal_form(cfg)

    n = graph.number_of_nodes()
    edges = graph.edges(data="label")

    eps_terms = set()
    term_prods = defaultdict(set)
    non_term_prods = defaultdict(set)

    for p in cfg.productions:
        head, body = p.head, p.body
        body_len = len(body)
        if body_len == 0:
            eps_terms.add(head)
        elif body_len == 1:
            term_prods[head].add(body[0])
        elif body_len == 2:
            non_term_prods[head].add((body[0], body[1]))

    matrices = {non_term: csr_matrix((n, n), dtype=bool) for non_term in cfg.variables}

    for i in range(n):
        for t in eps_terms:
            matrices[t][i, i] = True

    for i, j, lab in edges:
        for N, t in term_prods.items():
            if Terminal(lab) in t:
                matrices[N][i, j] = True

    while True:
        changed = False
        for nonterm, non_terms in non_term_prods.items():
            old_nnz = matrices[nonterm].nnz
            matrices[nonterm] += sum(
                matrices[n1] @ matrices[n2] for n1, n2 in non_terms
            )
            changed |= old_nnz != matrices[nonterm].nnz

        if not changed:
            break

    return set(
        (i, non_term, j)
        for non_term, mtx in matrices.items()
        for i, j in zip(*mtx.nonzero())
    )


def _tensor_prod(cfg: CFG, graph: MultiGraph):
    """
    Solves the reachability problem via the tensor algorithm
    """

    cfg_matrices = BooleanDecomposition.from_rsm(
        RSM.rsm_from_ecfg(ECFG.ecfg_from_cfg(cfg))
    )
    cfg_indexed_states = {i: s for s, i in cfg_matrices.indexed_states.items()}

    graph_matrices = BooleanDecomposition.from_automata(EpsilonNFA.from_networkx(graph))
    graph_indexed_states = {i: s for s, i in graph_matrices.indexed_states.items()}
    graph_states_num = len(graph_matrices.indexed_states)

    for non_term in cfg.get_nullable_symbols():
        for j in range(len(graph_matrices.indexed_states)):
            graph_matrices.matrices[non_term.value][j, j] = True

    tc_shape = len(cfg_indexed_states) * len(graph_indexed_states)
    prev_tc = dok_matrix((tc_shape, tc_shape), dtype=bool)
    while True:
        intersection = cfg_matrices.intersect(graph_matrices)
        tc = intersection.transitive_closure()

        if prev_tc.nnz == tc.nnz:
            break

        prev_tc = tc
        for i, j in list(zip(*tc.nonzero())):
            cfg_i, cfg_j = i // graph_states_num, j // graph_states_num
            graph_i, graph_j = (
                i % graph_states_num,
                j % graph_states_num,
            )

            state_from, state_to = cfg_indexed_states[cfg_i], cfg_indexed_states[cfg_j]
            non_term, _ = state_from.value
            if (
                state_from in cfg_matrices.start_states
                and state_to in cfg_matrices.final_states
            ):
                graph_matrices.matrices[non_term][graph_i, graph_j] = True

    return {
        (graph_indexed_states[graph_i], non_term, graph_indexed_states[graph_j])
        for non_term, matrix in graph_matrices.matrices.items()
        for graph_i, graph_j in zip(*matrix.nonzero())
    }


class Algo(enum.Enum):

    hellings = _hellings
    matrix_prod = _cf_closure
    tensor_prod = _tensor_prod
