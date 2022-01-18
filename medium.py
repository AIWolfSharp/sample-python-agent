"""
medium.py

(c) 2022 OTSUKI Takashi

"""

from gameinfo import GameInfo
from gamesetting import GameSetting
from villager import Villager
from judge import Judge
from queue import Queue
from typing import Optional

class Medium(Villager):
    """ 霊媒師エージェント """

    def __init__(self) -> None:
        super().__init__()
        self.co_date: int = 3 # CO予定日
        self.found_wolf: bool = False # 人狼を発見したか
        self.has_co: bool = False # CO済ならTrue
        self.my_judge_queue: Queue[Judge] = Queue() # 霊媒結果の待ち行列

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.found_wolf = False
        self.has_co = False
        self.my_judge_queue = Queue()

    def day_start(self) -> None:
        super().day_start()
        # 霊媒結果を待ち行列に入れる
        judge: Optional[Judge] = None if self.game_info is None else self.game_info["mediumResult"]
        if judge is not None:
            self.my_judge_queue.put(judge)
            if judge["result"]  == "WEREWOLF":
                self.found_wolf = True

    def talk(self) -> str:
        if self.game_info is None:
            return self.cf.skip()
        # 予定日あるいは人狼を発見したらCO
        if not self.has_co and (self.game_info["day"] == self.co_date or self.found_wolf):
            self.has_co = True
            return self.cf.comingout(self.me, "MEDIUM")
        # CO後は霊能行使結果を報告
        if self.has_co and not self.my_judge_queue.empty():
            judge: Judge = self.my_judge_queue.get()
            return self.cf.identified(judge["agent"], judge["target"], judge["result"])
        # 偽占い師
        fake_seers: set[int] = set()
        for j in self.divination_reports:
            if j["target"] == self.me and j["result"] == "WEREWOLF":
                fake_seers.add(j["agent"])
        # 生存偽霊媒師に投票
        candidates: list[int] = []
        for a in self.comingout_map:
            if self.is_alive(a) and self.comingout_map[a] == "MEDIUM":
                candidates.append(a)
        # いなければ非偽自称占い師から人狼と判定された生存エージェントに投票
        reported_wolves: set[int] = set()
        for j in self.divination_reports:
            if j["agent"] not in fake_seers and j["result"] == "WEREWOLF":
                reported_wolves.add(j["target"])
        candidates = self.get_alive_others(list(reported_wolves))
        # いなければ生存偽占い師に投票
        if not candidates:
            candidates = self.get_alive(list(fake_seers))
        # それでもいなければ生存エージェントに投票
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # 初めての投票先宣言あるいは変更ありの場合，投票先宣言
        if self.vote_candidate == -1 or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate != -1:
                return self.cf.vote(self.vote_candidate) 
        return self.cf.skip()
