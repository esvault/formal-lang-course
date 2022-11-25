from pyformlang.cfg import Variable
from pyformlang.finite_automaton import EpsilonNFA

from project.cfg.ecfg import ECFG


class RSM:
    def __init__(self, start_symbol: Variable, boxes: dict[Variable, EpsilonNFA]):
        self.start_symbol = start_symbol
        self.boxes = boxes

    @classmethod
    def rsm_from_ecfg(cls, ecfg: ECFG) -> "RSM":
        return RSM(
            ecfg.start_symbol,
            {head: body.to_epsilon_nfa() for head, body in ecfg.productions.items()},
        )

    def minimize(self) -> "RSM":
        for var, nfa in self.boxes.items():
            self.boxes[var] = nfa.minimize()
        return self
