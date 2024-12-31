#
# bodyguard.py
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
from typing import List

from aiwolf import Agent, GameInfo, GameSetting, Role, Species
from aiwolf.constant import AGENT_NONE

from villager import SampleVillager

class SampleBodyguard(SampleVillager):
    """ボディーガードエージェントのサンプル."""

    to_be_guarded: Agent
    """護衛対象のエージェント。"""

    is_seer_roller: bool;
    """占い師のローラー"""

    def __init__(self) -> None:
        """SampleBodyguard の新しいインスタンスを初期化する。"""
        super().__init__()
        self.to_be_guarded = AGENT_NONE  # 初期値として護衛対象を設定しない（NONE にする）。


    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        """ゲーム開始時に呼び出される初期化処理。"""
        super().initialize(game_info, game_setting)
        self.to_be_guarded = AGENT_NONE  # 護衛対象を再度初期化。

    def guard(self) -> Agent:
        """護衛するエージェントを選択する。"""
        # 1. 生存しているエージェントの中から、人狼ではないと判定された占い師を候補とする。
        candidates: List[Agent] = self.get_alive([
            j.agent for j in self.divination_reports  # 占い結果の中から...
            if j.result != Species.WEREWOLF or j.target != self.me  # 自分が対象ではなく、かつ人狼でない結果。
        ])

        # 2. 候補が存在しない場合、生存している霊媒師を候補とする。
        if not candidates:
            candidates = [
                a for a in self.comingout_map  # カミングアウトマップに登録されているエージェントを...
                if self.is_alive(a) and self.comingout_map[a] == Role.MEDIUM  # 生存している霊媒師に絞り込む。
            ]

        # 3. 候補がまだ存在しない場合、生存している他の全エージェントを候補とする。
        if not candidates:
            candidates = self.get_alive_others(self.game_info.agent_list)  # 自分以外の生存者を取得。

        # 4. 現在の護衛対象が候補に含まれない場合、または護衛対象が未設定の場合は、新しい護衛対象をランダムに選ぶ。
        if self.to_be_guarded == AGENT_NONE or self.to_be_guarded not in candidates:
            self.to_be_guarded = self.random_select(candidates)  # 候補からランダムに選択。

        # 5. 最終的な護衛対象を返す。ただし、護衛対象が設定されていない場合は自分自身を護衛。
        return self.to_be_guarded if self.to_be_guarded != AGENT_NONE else self.me
