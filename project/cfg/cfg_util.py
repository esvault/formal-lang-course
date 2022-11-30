from pyformlang.cfg import CFG


def get_cfg_from_file(file: str) -> CFG:
    """
    Read context free grammar from file
    """

    with open(file) as file:
        return CFG.from_text(file.read())


def cfg_to_weak_normal_form(cfg: CFG) -> CFG:
    """
    Transform context free grammar to weak normal form
    """

    new_cfg = cfg.eliminate_unit_productions().remove_useless_symbols()
    prods = new_cfg._get_productions_with_only_single_terminals()
    prods = new_cfg._decompose_productions(prods)
    return CFG(start_symbol=new_cfg.start_symbol, productions=set(prods))
