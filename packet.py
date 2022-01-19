from typing import List, TypedDict, Optional
from gameinfo import GameInfo
from gamesetting import GameSetting
from utterance import Utterance

class Packet(TypedDict):
    gameInfo: Optional[GameInfo]
    gameSetting: Optional[GameSetting]
    request: str
    talkHistory: Optional[List[Utterance]]
    whisperHistory: Optional[List[Utterance]]
