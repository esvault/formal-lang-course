from pyformlang.cfg import CFG, Terminal, Variable
from project.cfg_util import cfg_to_weak_normal_form, get_cfg_from_file

import os


def is_weak_form(cfg: CFG) -> bool:
    try:
        for prod in cfg.productions:
            match len(prod.body):
                case 0:
                    assert True
                case 1:
                    assert isinstance(prod.body[0], Terminal)
                case 2:
                    assert isinstance(prod.body[0], Variable) and isinstance(
                        prod.body[1], Variable
                    )
                case _:
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
    path = os.path.join("assets", "test_cfg.txt")
    cfg = get_cfg_from_file(path)

    cfg_normal_form = cfg_to_weak_normal_form(cfg)

    assert is_weak_form(cfg_normal_form)
