from pyformlang.cfg import CFG

from project.cyk import cyk

cfgs = list(
    map(
        lambda x: CFG.from_text(x),
        [
            """
        S -> A S B S | $
        A -> (
        B -> )
    """,
            """
        S -> A B
        A -> a A | $
        B -> A b
    """,
        ],
    )
)

wright_strings = [
    ["", "()", "()()", "(((((())))))((()))(())()(())"],
    ["b", "ab", "aab", "aaaaaab"],
]

wrong_strings = [[")(", "(()", "())", "()("], ["abb", "", "aa", "aabbb"]]


def test_cfg_contains_write_string():
    for i, string_list in enumerate(wright_strings):
        for string in string_list:
            assert cyk(cfgs[i], string)


def test_cfg_not_contains_wrong_string():
    for i, string_list in enumerate(wrong_strings):
        for string in string_list:
            assert not cyk(cfgs[i], string)
