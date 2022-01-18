"""
bodyguard.py

(c) 2022 OTSUKI Takashi

"""

from villager import Villager
from gameinfo import GameInfo
from gamesetting import GameSetting


class Bodyguard(Villager):
    """ 狩人エージェント """

    def __init__(self) -> None:
        super().__init__()
        self.to_be_guarded: int = -1  # 護衛対象

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.to_be_guarded = -1

    def guard(self) -> int:
        # 非偽生存自称占い師を護衛
        candidates: list[int] = []
        for j in self.divination_reports:
            if j["result"] != "WEREWOLF" or j["target"] != self.me:
                candidates.append(j["agent"])
        # いなければ生存自称霊媒師を護衛
        if not candidates:
            for a in self.comingout_map:
                if self.is_alive(a) and self.comingout_map[a] == "MEDIUM":
                    candidates.append(a)
        # いなければ生存エージェントを護衛
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # 初回あるいは変更ありの場合，護衛先を更新
        if self.to_be_guarded == -1 or self.to_be_guarded not in candidates:
            self.to_be_guarded = self.random_select(list(set(candidates)))
        return self.to_be_guarded if self.to_be_guarded != -1 else self.me
