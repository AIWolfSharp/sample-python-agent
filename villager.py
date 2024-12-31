#
# villager.py
#
# Copyright 2022 OTSUKI Takashi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import random
from typing import Dict, List

from aiwolf import (AbstractPlayer, Agent, Content, GameInfo, GameSetting,
                    Judge, Role, Species, Status, Talk, Topic,
                    VoteContentBuilder)
from aiwolf.constant import AGENT_NONE

from const import CONTENT_SKIP


class SampleVillager(AbstractPlayer):
    """サンプル村人エージェントのクラス。"""

    me: Agent
    """自分自身のエージェント。"""

    vote_candidate: Agent
    """投票候補のエージェント。"""

    game_info: GameInfo
    """現在のゲームに関する情報。"""

    game_setting: GameSetting
    """現在のゲームの設定。"""

    comingout_map: Dict[Agent, Role]
    """エージェントが主張した役職のマッピング。"""

    divination_reports: List[Judge]
    """占い結果のタイムシリーズ。"""

    identification_reports: List[Judge]
    """霊能結果のタイムシリーズ。"""

    talk_list_head: int
    """未解析の発言リストのインデックス。"""

    def __init__(self) -> None:
        """SampleVillagerの新しいインスタンスを初期化します。"""
        self.me = AGENT_NONE
        self.vote_candidate = AGENT_NONE
        self.game_info = None  # type: ignore
        self.comingout_map = {}
        self.divination_reports = []
        self.identification_reports = []
        self.talk_list_head = 0

    def is_alive(self, agent: Agent) -> bool:
        """エージェントが生存しているかどうかを返します。

        Args:
            agent: 対象のエージェント。

        Returns:
            エージェントが生存している場合はTrue、それ以外はFalse。
        """
        return self.game_info.status_map[agent] == Status.ALIVE

    def get_others(self, agent_list: List[Agent]) -> List[Agent]:
        """自分以外のエージェントのリストを返します。

        Args:
            agent_list: エージェントのリスト。

        Returns:
            自分以外のエージェントのリスト。
        """
        return [a for a in agent_list if a != self.me]

    def get_alive(self, agent_list: List[Agent]) -> List[Agent]:
        """指定されたリスト内の生存しているエージェントのリストを返します。

        Args:
            agent_list: エージェントのリスト。

        Returns:
            生存しているエージェントのリスト。
        """
        return [a for a in agent_list if self.is_alive(a)]

    def get_alive_others(self, agent_list: List[Agent]) -> List[Agent]:
        """自分以外の生存しているエージェントのリストを返します。

        Args:
            agent_list: エージェントのリスト。

        Returns:
            自分以外の生存しているエージェントのリスト。
        """
        return self.get_alive(self.get_others(agent_list))

    def random_select(self, agent_list: List[Agent]) -> Agent:
        """指定されたリストからランダムにエージェントを選びます。

        Args:
            agent_list: エージェントのリスト。

        Returns:
            リストからランダムに選ばれたエージェント。
        """
        return random.choice(agent_list) if agent_list else AGENT_NONE

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        """ゲーム開始時の初期化を行います。"""
        self.game_info = game_info
        self.game_setting = game_setting
        self.me = game_info.me
        # 前回ゲームの情報をクリアします。
        self.comingout_map.clear()
        self.divination_reports.clear()
        self.identification_reports.clear()

    def day_start(self) -> None:
        """新しい日の開始時の処理を行います。"""
        self.talk_list_head = 0
        self.vote_candidate = AGENT_NONE

    def update(self, game_info: GameInfo) -> None:
        """ゲーム情報を更新します。"""
        self.game_info = game_info
        for i in range(self.talk_list_head, len(game_info.talk_list)):
            tk: Talk = game_info.talk_list[i]
            talker: Agent = tk.agent
            if talker == self.me:
                continue
            content: Content = Content.compile(tk.text)
            if content.topic == Topic.COMINGOUT:
                self.comingout_map[talker] = content.role
            elif content.topic == Topic.DIVINED:
                self.divination_reports.append(Judge(talker, game_info.day, content.target, content.result))
            elif content.topic == Topic.IDENTIFIED:
                self.identification_reports.append(Judge(talker, game_info.day, content.target, content.result))
        self.talk_list_head = len(game_info.talk_list)

    def talk(self) -> Content:
        """発言内容を生成します。"""
        fake_seers = [j.agent for j in self.divination_reports
                      if j.target == self.me and j.result == Species.WEREWOLF]
        reported_wolves = [j.target for j in self.divination_reports
                           if j.agent not in fake_seers and j.result == Species.WEREWOLF]
        candidates = self.get_alive_others(reported_wolves)
        if not candidates:
            candidates = self.get_alive(fake_seers)
        if not candidates:
            candidates = self.get_alive_others(self.game_info.agent_list)
        if self.vote_candidate == AGENT_NONE or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate != AGENT_NONE:
                return Content(VoteContentBuilder(self.vote_candidate))
        return CONTENT_SKIP

    def vote(self) -> Agent:
        """投票対象を決定します。"""
        return self.vote_candidate if self.vote_candidate != AGENT_NONE else self.me

