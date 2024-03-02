from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]


    def __init__(self, S: set[str], K: set[STATE], q0: STATE, d: dict[tuple[STATE, str], STATE], F: set[STATE]):
        self.S = S
        self.K = K
        self.q0 = q0
        self.d = d
        self.F = F

    def accept(self, word: str) -> bool:
        # simulate the dfa on the given word. return true if the dfa accepts the word, false otherwise
        this_state = self.q0

        for w in word:
            key = (this_state, w)
            if not key in self.d:
                return False
            this_state = self.d[(this_state, w)]
        return this_state in self.F


