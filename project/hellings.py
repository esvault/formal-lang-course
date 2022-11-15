from networkx import MultiGraph
from pyformlang.cfg import CFG, Terminal
from collections import deque, defaultdict

from project.cfg_util import cfg_to_weak_normal_form


def hellings(cfg: CFG, graph: MultiGraph):
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

    first_set = {(v, i, i) for v in eps_non_terms for i in graph.nodes}
    second_set = {
        (v, i, j)
        for v, terms in term_prods.items()
        for i, j, label in graph.edges(data="label")
        if Terminal(label) in terms
    }

    r = first_set.union(second_set)
    m = deque(r.copy())

    while m:
        v, i, j = m.popleft()
        temp = set()
        for v2, l, k in r:
            if i == k:
                for head, body in non_term_prods.items():
                    if (v2, v) in body and (head, l, j) not in r:
                        m.append((head, l, j))
                        temp.add((head, l, j))

            if j == l:
                for head, body in non_term_prods.items():
                    if (v, v2) in body and (head, i, k) not in r:
                        m.append((head, i, k))
                        temp.add((head, i, k))

        r = r.union(temp)

    return r
