from pyformlang.cfg import CFG


def cyk(cfg: CFG, query: str):

    if not query:
        return cfg.generate_epsilon()

    nfh = cfg.to_normal_form()

    prods_terminal = set()  # Productions like: A -> a, B -> b
    prods_non_terminals = set()  # Productions like: S -> AB, C -> VM

    for p in nfh.productions:
        if (len(p.body)) == 1:
            prods_terminal.add(p)
        else:
            prods_non_terminals.add(p)

    n = len(query)
    M = {v: [[False for _ in range(n)] for _ in range(n)] for v in nfh.variables}

    for i, s in enumerate(query):
        prods = [p for p in prods_terminal if p.body[0].value == s]
        for p in prods:
            M[p.head][i][i] = True

    for m in range(1, n):
        for i in range(n - m):
            j = i + m

            for k in range(i, j):

                for p in prods_non_terminals:
                    M[p.head][i][j] = M[p.head][i][j] or (
                        M[p.body[0]][i][k] and M[p.body[1]][k + 1][j]
                    )

    return M[nfh.start_symbol][0][n - 1]
