from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]
    def __init__(self, S: set[str], K: set[STATE], q0: STATE, d: dict[tuple[STATE, str], set[STATE]], F: set[STATE]):
        self.S = S
        self.K = K
        self.q0 = q0
        self.d = d
        self.F = F

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        # compute the epsilon closure of a state (you will need this for subset construction)
        epsilon_closure = []
        list = [state]              # starile care trb procesate

        for element in list:
            epsilon_closure.append(element)
            key = (element, EPSILON)
            if key in self.d:
                transition = self.d[key]
                for state in transition:
                    if not state in epsilon_closure:
                        list.append(state)

        return set(epsilon_closure)

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        # convert this nfa to a DFA_ using the subset construction algorithm

        DFA_initial_state = frozenset(self.epsilon_closure(self.q0))
        all_states = [frozenset(self.epsilon_closure(self.q0))]
        DFA_transitions = {}
        DFA_final_states = set()
        symbols = list(self.S)

        for state in all_states:

            if state.intersection(self.F):                      # daca state contine orice st finala din NFA => se adauga in starile finale DFA
                DFA_final_states.add(frozenset(state))

            for i in range(len(symbols)):
                symbol = str(symbols[i])
                new_state = set()
                for current_state in state:
                    current_key = (current_state, symbol)
                    if current_key in self.d:
                        new_state = new_state.union(self.d[current_key])

                epsilon_closure = set()
                epsilon_closure_frozen = frozenset(set())

                for current_state in new_state:
                    epsilon_closure = epsilon_closure.union(self.epsilon_closure(current_state))
                    epsilon_closure_frozen = frozenset(epsilon_closure)

                DFA_transitions[(frozenset(state), str(symbol))] = epsilon_closure_frozen

                if not epsilon_closure_frozen in all_states:
                    all_states.append(epsilon_closure_frozen)

        return DFA(self.S, set(all_states), DFA_initial_state, DFA_transitions, DFA_final_states)


