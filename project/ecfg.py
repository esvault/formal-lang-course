from pyformlang.cfg import Variable, Terminal, CFG
from pyformlang.regular_expression import Regex


class ECFG:
    def __init__(
        self,
        variables: set[Variable],
        terminals: set[Terminal],
        start_symbol: Variable,
        productions: dict[Variable, Regex],
    ):
        self.variables = variables
        self.terminals = terminals
        self.start_symbol = start_symbol
        self.productions = productions

    @classmethod
    def ecfg_from_cfg(cls, cfg: CFG):
        productions = {}
        for p in cfg.productions:
            body = Regex(
                ".".join(tok.value for tok in p.body) if len(p.body) > 0 else "$"
            )

            if p.head in productions.keys():
                productions[p.head] = productions[p.head].union(body)
            else:
                productions[p.head] = body

        return ECFG(
            set(cfg.variables), set(cfg.terminals), cfg.start_symbol, productions
        )