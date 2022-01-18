"""
seer.py

(c) 2022 OTSUKI Takashi

"""

from queue import Queue
from gameinfo import GameInfo
from gamesetting import GameSetting
from judge import Judge
from villager import Villager
from typing import Optional


class Seer(Villager):
    """ 占い師エージェント """

    def __init__(self) -> None:
        super().__init__()
        self.co_date: int = 3 # CO予定日
        self.has_co: bool = False # CO済ならTrue
        self.my_judge_queue: Queue[Judge] = Queue() # 占い結果の待ち行列
        self.not_divined_agents: list[int] = [] # 未占いエージェント
        self.werewolves: list[int] = [] # 見つけた人狼

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.has_co = False
        self.my_judge_queue = Queue()
        self.not_divined_agents = self.get_others(self.agent_list)
        self.werewolves.clear()

    def day_start(self) -> None:
        super().day_start()
        # 占い結果の処理
        judge: Optional[Judge] = None if self.game_info is None else self.game_info["divineResult"]
        if judge is not None:
            self.my_judge_queue.put(judge)
            target: int = judge["target"]
            if target in self.not_divined_agents:
                self.not_divined_agents.remove(judge["target"])
            if judge["result"]  == "WEREWOLF":
                self.werewolves.append(judge["target"])

    def talk(self) -> str:
        if self.game_info is None:
            return self.cf.skip()
        # 予定日あるいは人狼を発見したらCO
        if not self.has_co and (self.game_info["day"] == self.co_date or self.werewolves):
            self.has_co = True
            return self.cf.comingout(self.me, "SEER")
        # CO後は占い結果を報告
        if self.has_co and not self.my_judge_queue.empty():
            judge: Judge = self.my_judge_queue.get()
            return self.cf.divined(self.me, judge["target"], judge["result"])
        # 生存人狼に投票
        candidates: list[int] = self.get_alive(self.werewolves)
        # いなければ生存偽占い師に投票
        if not candidates:
            candidates = [a for a in self.comingout_map.keys() if self.comingout_map[a] == "SEER"]
        # それでもいなければ生存エージェントに投票
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # 初めての投票先宣言あるいは変更ありの場合，投票先宣言
        if self.vote_candidate == -1 or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate != -1:
                return self.cf.vote(self.vote_candidate) 
        return self.cf.skip()

    def divine(self) -> int:
        # まだ占っていないエージェントからランダムに占う
        target: int = self.random_select(self.not_divined_agents)
        return target if target != -1 else self.me
