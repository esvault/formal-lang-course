from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.finite_automaton import EpsilonNFA
from networkx import MultiGraph


def regex_to_dfa(regex: str) -> DeterministicFiniteAutomaton:
    """
    Transform regular expression to minimized Deterministic finite automaton.

    :param regex: original regular expression
    :return: minimized dfa
    """

    re = Regex(regex)
    eps_nfa: EpsilonNFA = re.to_epsilon_nfa()
    return eps_nfa.minimize()


def graph_to_epsilon_nfa(
    graph: MultiGraph,
    start_states: set = None,
    finale_states: set = None,
) -> EpsilonNFA:
    """
    Transform the networkx graph to the Nondeterministic finite automation.

    :param graph: Original networkx graph
    :param start_states: Nodes of graph to be start in the result automation
    :param finale_states: Nodes of graph to be final in the result automation
    :return: nfa
    """

    nfa = NondeterministicFiniteAutomaton.from_networkx(graph)

    if start_states is not None:
        for s in start_states:
            nfa.add_start_state(s)
    else:
        for n in graph.nodes:
            nfa.add_start_state(n)

    if finale_states is not None:
        for s in finale_states:
            nfa.add_final_state(s)
    else:
        for n in graph.nodes:
            nfa.add_final_state(n)

    return nfa
