from collections import defaultdict

from networkx import MultiGraph
from pyformlang.cfg import CFG, Terminal
from scipy.sparse import csr_matrix

from project.cfg_util import cfg_to_weak_normal_form


def cf_closure(graph: MultiGraph, cfg: CFG, matrix_type="csr"):
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
