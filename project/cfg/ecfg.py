from pyformlang.cfg import Variable, Terminal, CFG
from pyformlang.regular_expression import Regex


class ECFG:
    """
    This class is representation of context free grammar as ECFG
    """

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
        """
        Transform context free grammar to ECFG
        """

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

    @classmethod
    def ecfg_from_file(cls, file: str, start_symbol=Variable("S")):
        """
        Read ECFG from file
        """
        with open(file) as f:
            text = f.read()
            return cls.ecfg_from_text(text, start_symbol)

    @classmethod
    def ecfg_from_text(cls, text: str, start_symbol=Variable("S")):
        """
        Read ECFG from string
        """
        variables = set()
        productions = dict()
        terminals = set()

        for line in text.strip().split("\n"):
            if not line:
                continue
            cls._read_line(line, productions, terminals, variables)

        return ECFG(variables, terminals, start_symbol, productions)

    @classmethod
    def _read_line(cls, line, productions, terminals, variables):
        [head, body] = line.strip().split("->")

        head = Variable(head.rstrip())

        variables.add(head)

        for sym in body:
            if sym.islower():
                terminals.add(Terminal(sym))

        productions[Variable(head)] = Regex(body)
