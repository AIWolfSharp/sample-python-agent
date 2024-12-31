#
# seer.py
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


from collections import deque
from typing import Deque, List, Optional

from aiwolf import (Agent, ComingoutContentBuilder, Content,
                    DivinedResultContentBuilder, GameInfo, GameSetting, Judge,
                    Role, Species, VoteContentBuilder)
from aiwolf.constant import AGENT_NONE

from const import CONTENT_SKIP
from villager import SampleVillager


class SampleSeer(SampleVillager):
    """サンプル占い師エージェント."""

    co_date: int
    """カミングアウトを予定している日付."""
    has_co: bool
    """カミングアウト済みかどうか."""
    my_judge_queue: Deque[Judge]
    """占い結果のキュー."""
    not_divined_agents: List[Agent]
    """未占いのエージェントリスト."""
    werewolves: List[Agent]
    """発見された人狼リスト."""

    is_seer_roller: bool;
    """占い師のローラー"""

    def __init__(self) -> None:
        """SampleSeerのインスタンスを初期化."""
        super().__init__()
        self.co_date = 0  # カミングアウト日付を初期化
        self.has_co = False  # カミングアウト未実施を設定
        self.my_judge_queue = deque()  # 占い結果キューの初期化
        self.not_divined_agents = []  # 未占いエージェントリストの初期化
        self.werewolves = []  # 発見された人狼リストの初期化

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        """ゲーム開始時の初期化処理."""
        super().initialize(game_info, game_setting)
        self.co_date = 1  # カミングアウトを1日目に設定
        self.has_co = False
        self.my_judge_queue.clear()
        self.not_divined_agents = self.get_others(self.game_info.agent_list)  # 他のエージェントを取得
        self.werewolves.clear()

    def day_start(self) -> None:
        """新しい日の開始時の処理."""
        super().day_start()
        # 占い結果の処理
        judge: Optional[Judge] = self.game_info.divine_result
        if judge is not None:
            self.my_judge_queue.append(judge)  # 占い結果をキューに追加
            if judge.target in self.not_divined_agents:
                self.not_divined_agents.remove(judge.target)  # 占ったエージェントをリストから削除
            if judge.result == Species.WEREWOLF:
                self.werewolves.append(judge.target)  # 人狼ならリストに追加

    def talk(self) -> Content:
        """話す内容を決定."""
        # 予定日または人狼発見時にカミングアウト
        if not self.has_co and (self.game_info.day == self.co_date or self.werewolves):
            self.has_co = True
            return Content(ComingoutContentBuilder(self.me, Role.SEER))
        # カミングアウト後、占い結果を報告
        if self.has_co and self.my_judge_queue:
            judge: Judge = self.my_judge_queue.popleft()
            return Content(DivinedResultContentBuilder(judge.target, judge.result))
        # 生存している人狼を投票対象に設定
        candidates: List[Agent] = self.get_alive(self.werewolves)

        seer_co_count = sum(1 for agent, role in self.comingout_map.items() if role == Role.SEER)

        # 候補がいない場合、偽占い師を候補に追加
        if not candidates:
            candidates = self.get_alive([a for a in self.comingout_map
                                         if self.comingout_map[a] == Role.SEER])
        # さらに候補がいない場合、その他の生存者を対象に
        if not candidates:
            candidates = self.get_alive_others(self.game_info.agent_list)
        # 未宣言または候補が変わった場合、投票宣言
        if self.vote_candidate == AGENT_NONE or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate != AGENT_NONE:
                return Content(VoteContentBuilder(self.vote_candidate))
        return CONTENT_SKIP

    def divine(self) -> Agent:
        """占い対象を決定."""
        # 未占いのエージェントからランダムに選択
        target: Agent = self.random_select(self.not_divined_agents)
        return target if target != AGENT_NONE else self.me

