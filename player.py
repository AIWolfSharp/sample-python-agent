from aiwolfpy import ContentFactory as cf
from aiwolfpy.protocol.contents import Content
from gameinfo import GameInfo
from gamesetting import GameSetting


class Player:

    def __init__(self) -> None:
        self.me: int = 0

    def attack(self) -> int:
        return self.me

    def day_start(self) -> None:
        pass

    def divine(self) -> int:
        return self.me

    def finish(self) -> None:
        pass

    def get_name(self) -> str:
        return "player"

    def guard(self) -> int:
        return self.me

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        self.me = game_info["agent"]

    def talk(self) -> Content:
        return cf.over()

    def update(self, game_info: GameInfo) -> None:
        pass

    def vote(self) -> int:
        return self.me

    def whisper(self) -> Content:
        return cf.over()
