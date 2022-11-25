import enum
from collections import defaultdict, deque

from networkx import MultiGraph
from pyformlang.cfg import Terminal, CFG
from scipy.sparse import csr_matrix

from project.cfg.cfg_util import cfg_to_weak_normal_form


def _hellings(cfg: CFG, graph: MultiGraph):
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


class Algo(enum.Enum):

    hellings = _hellings
    matrix_prod = _cf_closure
