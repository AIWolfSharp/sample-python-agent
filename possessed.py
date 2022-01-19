"""
possessed.py

(c) 2022 OTSUKI Takashi

"""

import random
from queue import Queue
from aiwolfpy import ContentFactory as cf
from aiwolfpy.protocol.abstractcontent import Content
from gameinfo import GameInfo
from gamesetting import GameSetting
from judge import Judge
from villager import Villager
from typing import Optional


class Possessed(Villager):
    """ 裏切り者エージェント """

    def __init__(self) -> None:
        super().__init__()
        self.fake_role: str = "SEER"  # 騙る役職
        self.co_date: int = 1  # CO予定日
        self.has_co: bool = False  # CO済ならtrue
        self.my_judgee_queue: Queue[Judge] = Queue()  # 偽判定結果の待ち行列
        self.not_judged_agents: list[int] = []  # 未判定エージェント
        self.num_wolves: int = 0  # 人狼の数
        self.werewolves: list[int] = []  # 偽人狼

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.fake_role = "SEER"
        self.co_date = 1  # いきなりCO
        self.has_co = False
        self.my_judgee_queue = Queue()
        self.not_judged_agents = self.get_others(self.agent_list)
        self.num_wolves = game_setting["roleNumMap"]["WEREWOLF"]
        self.werewolves.clear()

    def get_fake_judge(self) -> Optional[Judge]:
        """ 偽判定を生成 """
        if self.game_info is None:
            return None
        target: int = -1
        if self.fake_role == "SEER":  # 占い師騙りの場合ランダム
            if self.game_info["day"] != 0:
                target = self.random_select(self.get_alive(self.not_judged_agents))
        elif self.fake_role == "MEDIUM":
            target = self.game_info["executedAgent"]
        # 偽判定結果の決定
        result: str = "HUMAN"
        # 偽人狼に余裕があれば50%の確率で人狼と判定
        if len(self.werewolves) < self.num_wolves and random.random() < 0.5:
            result = "WEREWOLF"
        return None if target == -1 else {"day": self.game_info["day"], "agent": self.me, "target": target, "result": result}

    def day_start(self) -> None:
        super().day_start()
        # 偽判定結果の処理
        judge: Optional[Judge] = self.get_fake_judge()
        if judge is not None:
            self.my_judgee_queue.put(judge)
            target: int = judge["target"]
            if target in self.not_judged_agents:
                self.not_judged_agents.remove(target)
            if judge["result"] == "WEREWOLF":
                self.werewolves.append(judge["target"])

    def talk(self) -> Content:
        if self.game_info is None:
            return cf.skip()
        # 予定日あるいは人狼を発見したらCO
        if self.fake_role != "VILLAGER" and not self.has_co and (self.game_info["day"] == self.co_date or self.werewolves):
            self.has_co = True
            return cf.comingout(self.me, self.fake_role)
        # CO後は判定結果を報告
        if self.has_co and not self.my_judgee_queue.empty():
            judge: Judge = self.my_judgee_queue.get()
            if self.fake_role == "SEER":
                return cf.divined(judge["target"], judge["result"])
            elif self.fake_role == "MEDIUM":
                return cf.identified(judge["target"], judge["result"])
        # 生存人狼に投票
        candidates: list[int] = self.get_alive(self.werewolves)
        # いなければ生存対抗エージェントに投票
        if not candidates:
            candidates = [a for a in self.comingout_map.keys() if self.comingout_map[a] == self.fake_role]
        # それでもいなければ生存エージェントに投票
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # 初めての投票先宣言あるいは変更ありの場合，投票先宣言
        if self.vote_candidate == -1 or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate != -1:
                return cf.vote(self.vote_candidate)
        return cf.skip()
