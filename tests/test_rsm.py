from tests.test_ecfg import actual_ecfgs, expected_ecfgs
from project.rsm import RSM

actual_rsms = list(map(lambda x: RSM.rsm_from_ecfg(x), actual_ecfgs))

expected_rsms = list(map(lambda x: RSM.rsm_from_ecfg(x), expected_ecfgs))


def rsm_eq(actual: RSM, expected: RSM):
    assert actual.start_symbol.__eq__(expected.start_symbol)

    for var, automata in actual.boxes.items():
        assert automata.is_equivalent_to(expected.boxes[var])


def test_rsm_eq():
    for i in range(len(actual_rsms)):
        rsm_eq(actual_rsms[i], expected_rsms[i])
