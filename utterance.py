from typing import TypedDict

class Utterance(TypedDict):
    agent: int
    day: int
    idx: int
    text: str
    turn: int
