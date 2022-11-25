import os

from pyformlang.cfg import Variable, Terminal, CFG
from pyformlang.regular_expression import Regex

from project.cfg.ecfg import ECFG

cfgs = list(
    map(
        lambda x: CFG.from_text(x),
        [
            """
        S -> a C b
        C -> $
    """,
            """
        S -> A b C
        A -> a
        C -> c
    """,
            """
        S -> a B
        B -> C
        C -> D
        D -> a
    """,
        ],
    )
)

actual_ecfgs = list(map(lambda x: ECFG.ecfg_from_cfg(x), cfgs))

expected_ecfgs = [
    ECFG(
        {Variable("S"), Variable("C")},
        {Terminal("a"), Terminal("b")},
        Variable("S"),
        {Variable("S"): Regex("a.C.b"), Variable("C"): Regex("$")},
    ),
    ECFG(
        {Variable("S"), Variable("A"), Variable("C")},
        {Terminal("a"), Terminal("b"), Terminal("c")},
        Variable("S"),
        {
            Variable("S"): Regex("A.b.C"),
            Variable("A"): Regex("a"),
            Variable("C"): Regex("c"),
        },
    ),
    ECFG(
        {Variable("S"), Variable("B"), Variable("C"), Variable("D")},
        {Terminal("a")},
        Variable("S"),
        {
            Variable("S"): Regex("a.B"),
            Variable("B"): Regex("C"),
            Variable("C"): Regex("D"),
            Variable("D"): Regex("a"),
        },
    ),
]


def ecfg_eq(actual: ECFG, expected: ECFG):
    assert actual.variables.__eq__(expected.variables)
    assert actual.terminals.__eq__(expected.terminals)
    assert actual.start_symbol.__eq__(expected.start_symbol)

    for head, body in actual.productions.items():
        actual_nfa = body.to_epsilon_nfa()
        expected_nfa = expected.productions[head].to_epsilon_nfa()

        assert actual_nfa.is_equivalent_to(expected_nfa)


def test_get_from_cfg():
    for i in range(len(cfgs)):
        ecfg_eq(actual_ecfgs[i], expected_ecfgs[i])


def test_read_from_file():
    directory = os.path.join("tests", "assets")
    file = os.path.join(directory, "test_ecfg.txt")

    ecfg_expected = ECFG(
        {Variable("S"), Variable("V"), Variable("M")},
        {Terminal("a"), Terminal("b"), Terminal("c"), Terminal("d"), Terminal("m")},
        Variable("S"),
        {
            Variable("S"): Regex("a.b.V | $"),
            Variable("V"): Regex("$ | a.c.d | M"),
            Variable("M"): Regex("m"),
        },
    )

    ecfg_actual = ECFG.ecfg_from_file(file)

    ecfg_eq(ecfg_actual, ecfg_expected)
