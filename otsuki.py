from aiwolfpy.protocol.abstractcontent import Content
from gameinfo import GameInfo
from gamesetting import GameSetting
from player import Player
from villager import Villager
from bodyguard import Bodyguard
from medium import Medium
from seer import Seer
from possessed import Possessed
from werewolf import Werewolf


class OtsukiAgent(Player):

    def __init__(self) -> None:
        self.player: Player = Player()
        self.villager: Player = Villager()
        self.bodyguard: Player = Bodyguard()
        self.medium: Player = Medium()
        self.seer: Player = Seer()
        self.possessed: Player = Possessed()
        self.werewolf: Player = Werewolf()

    def attack(self) -> int:
        return self.player.attack()

    def day_start(self) -> None:
        self.player.day_start()

    def divine(self) -> int:
        return self.player.divine()

    def finish(self) -> None:
        self.player.finish()
        
    def get_name(self) -> str:
        return "otsuki"
    
    def guard(self) -> int:
        return self.player.guard()

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        role = game_info["roleMap"][str(game_info["agent"])]
        if role == "VILLAGER":
            self.player = self.villager
        elif role == "BODYGUARD":
            self.player = self.bodyguard
        elif role == "MEDIUM":
            self.player = self.medium
        elif role == "SEER":
            self.player = self.seer
        elif role == "POSSESSED":
            self.player = self.possessed
        elif role == "WEREWOLF":
            self.player = self.werewolf
        self.player.initialize(game_info, game_setting)
        
    def talk(self) -> Content:
        return self.player.talk()
        
    def update(self, game_info: GameInfo) -> None:
        self.player.update(game_info)
        
    def vote(self) -> int:
        return self.player.vote()

    def whisper(self) -> Content:
        return self.player.whisper()
