"""
werewolf.py

(c) 2022 OTSUKI Takashi

"""

import random
from gameinfo import GameInfo
from gamesetting import GameSetting
from possessed import Possessed
from typing import Optional
from judge import Judge

class Werewolf(Possessed):
    """ 人狼エージェント """

    def __init__(self) -> None:
        super().__init__()
        self.allies: list[int] = [] # 味方リスト
        self.humans: list[int] = [] # 人間リスト
        self.attack_vote_candidate: int = -1 # 襲撃投票先

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        if self.game_info is not None:
            self.allies = list(map(int, self.game_info["roleMap"].keys()))
        self.humans = [a for a in self.get_others(self.agent_list) if str(a) not in self.allies]
        # 1～3日目からランダムにカミングアウトする日付を決める
        self.co_date = random.randint(1, 3)
        # ランダムに騙る役職を決める
        self.fake_role = "VILLAGER"
        if self.game_info is not None:
            self.fake_role = random.choice([r for r in ["VILLAGER", "SEER", "MEDIUM"] if r in self.game_info["existingRoleList"]])

    def get_fake_judge(self) -> Optional[Judge]:
        ''' 偽判定を生成 '''
        if self.game_info is None:
            return None
        # 判定対象の決定
        target: int = -1
        if self.fake_role == "SEER": # 占い師騙りの場合ランダム
            if self.game_info["day"] != 0:
                target = self.random_select(self.get_alive(self.not_judged_agents))
        elif self.fake_role == "MEDIUM":
            target = self.game_info["executedAgent"]
        if target == -1:
            return None
        # 偽判定結果の決定
        result = "HUMAN"
        # 人間が偽占い対象の場合偽人狼に余裕があれば30%の確率で人狼と判定
        if target in self.humans:
            if len(self.werewolves) < self.num_wolves and random.random() < 0.3:
                result = "WEREWOLF"
        return { "day":self.game_info["day"], "agent":self.me, "target":target, "result":result}

    def day_start(self):
        super().day_start()
        self.attack_vote_candidate = -1

    def whisper(self):
        if self.game_info is None:
            return self.cf.skip()
        # 初日は騙る役職を宣言し以降は襲撃投票先を宣言
        if self.game_info["day"] == 0:
            return self.cf.comingout(self.me, self.fake_role)
        # 襲撃投票先を決定
        candidates: list[int] = []
        # まずカミングアウトした人間から
        candidates = [a for a in self.get_alive(self.humans) if a in self.comingout_map.keys()]
        # いなければ人間から
        if not candidates:
            candidates = self.get_alive(self.humans)
        # 初めての襲撃投票先宣言あるいは変更ありの場合，襲撃投票先宣言
        if self.attack_vote_candidate == -1 or self.attack_vote_candidate not in candidates:
            self.attack_vote_candidate = self.random_select(candidates)
            if self.attack_vote_candidate != -1:
                return self.cf.attack(self.attack_vote_candidate)
        return self.cf.skip()

    def attack(self):
        return self.attack_vote_candidate if self.attack_vote_candidate != -1 else self.me
