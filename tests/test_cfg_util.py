from pyformlang.cfg import CFG, Terminal, Variable
from project.cfg.cfg_util import cfg_to_weak_normal_form, get_cfg_from_file

import os


def is_weak_form(cfg: CFG) -> bool:
    try:
        for prod in cfg.productions:
            length = len(prod.body)
            if length == 0:
                assert True
            elif length == 1:
                assert isinstance(prod.body[0], Terminal)
            elif length == 2:
                assert isinstance(prod.body[0], Variable) and isinstance(
                    prod.body[1], Variable
                )
            else:
                assert False
    except AssertionError:
        return False

    return True


def test_cfg_in_weak_normal_form():
    cfg = CFG.from_text(
        """
        S -> a S b | epsilon"""
    )

    cfg_normal_form = cfg_to_weak_normal_form(cfg)

    assert is_weak_form(cfg_normal_form)


def test_cfg_from_file_in_weak_normal_form():
    directory = os.path.join("tests", "assets")
    path = os.path.join(directory, "test_cfg.txt")
    cfg = get_cfg_from_file(path)

    cfg_normal_form = cfg_to_weak_normal_form(cfg)

    assert is_weak_form(cfg_normal_form)


def test_cfg_contains_same_words():
    word0 = [""]
    word1 = ["a", "b"]
    word2 = ["a", "a", "b"]

    cfg = CFG.from_text(
        """
        S -> a S b | epsilon"""
    )

    cfg_normal_form = cfg_to_weak_normal_form(cfg)

    assert cfg.contains(word0) == cfg_normal_form.contains(word0)
    assert cfg.contains(word1) == cfg_normal_form.contains(word1)
    assert cfg.contains(word2) == cfg_normal_form.contains(word2)
