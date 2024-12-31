#
# medium.py
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
# http://www.apache.org/licenses/LICENSE-2.0

from collections import deque
from typing import Deque, List, Optional

# 必要なクラスと定数をインポート
from aiwolf import (Agent, ComingoutContentBuilder, Content, GameInfo,
                    GameSetting, IdentContentBuilder, Judge, Role, Species,
                    VoteContentBuilder)
from aiwolf.constant import AGENT_NONE  # 無効なエージェントを表す定数

from const import CONTENT_SKIP  # 発言をスキップするための定数
from villager import SampleVillager  # 村人役のサンプルエージェント


class SampleMedium(SampleVillager):
    """
    サンプル霊能者エージェントのクラス。
    村人エージェント (SampleVillager) を継承しており、霊能者特有の行動を実装しています。
    """

    co_date: int
    """予定されている役職カミングアウト日。"""
    found_wolf: bool
    """人狼が見つかったかどうかを示すフラグ。"""
    has_co: bool
    """役職カミングアウトを行ったかどうかを示すフラグ。"""
    my_judge_queue: Deque[Judge]
    """霊能結果のキュー。"""

    def __init__(self) -> None:
        """
        SampleMediumの新しいインスタンスを初期化します。
        霊能者特有の属性を設定します。
        """
        super().__init__()  # 基底クラスの初期化
        self.co_date = 0  # カミングアウト日を初期化
        self.found_wolf = False  # 人狼発見フラグを初期化
        self.has_co = False  # カミングアウトフラグを初期化
        self.my_judge_queue = deque()  # 判定結果のキューを初期化

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        """
        ゲーム開始時にエージェントを初期化します。

        Args:
            game_info (GameInfo): ゲームの初期情報。
            game_setting (GameSetting): ゲームの設定。
        """
        super().initialize(game_info, game_setting)  # 基底クラスの初期化を実行
        self.co_date = 3  # カミングアウトする予定の日を3日目に設定
        self.found_wolf = False  # 人狼発見フラグをリセット
        self.has_co = False  # カミングアウトフラグをリセット
        self.my_judge_queue.clear()  # 霊能結果のキューをクリア

    def day_start(self) -> None:
        """
        新しい日が始まったときに呼び出されるメソッド。
        毎日初期化すべき情報を設定します。
        """
        super().day_start()  # 基底クラスの処理を実行
        # 前日に処刑されたエージェントの霊能結果をキューに追加
        judge: Optional[Judge] = self.game_info.medium_result
        if judge is not None:
            self.my_judge_queue.append(judge)
            # 結果が人狼であればフラグを更新
            if judge.result == Species.WEREWOLF:
                self.found_wolf = True

    def talk(self) -> Content:
        """
        会話の発言内容を生成します。

        Returns:
            Content: 発言の内容を表すContentオブジェクト。
        """
        # 指定された日、または人狼を発見した場合にカミングアウトを実行
        if not self.has_co and (self.game_info.day == self.co_date or self.found_wolf):
            self.has_co = True  # カミングアウトフラグを更新
            return Content(ComingoutContentBuilder(self.me, Role.MEDIUM))

        # カミングアウト後、霊能結果を報告
        if self.has_co and self.my_judge_queue:
            judge: Judge = self.my_judge_queue.popleft()
            return Content(IdentContentBuilder(judge.target, judge.result))

        # 偽占い師の判定を収集
        fake_seers: List[Agent] = [j.agent for j in self.divination_reports
                                   if j.target == self.me and j.result == Species.WEREWOLF]

        # 偽霊能者のリストを作成（生存者のみ）
        candidates: List[Agent] = [a for a in self.comingout_map
                                   if self.is_alive(a) and self.comingout_map[a] == Role.MEDIUM]

        # 偽霊能者がいない場合、非偽占い師による人狼判定結果を候補にする
        if not candidates:
            reported_wolves: List[Agent] = [j.target for j in self.divination_reports
                                            if j.agent not in fake_seers and j.result == Species.WEREWOLF]
            candidates = self.get_alive_others(reported_wolves)

        # さらに候補がいない場合、偽占い師を候補に追加
        if not candidates:
            candidates = self.get_alive(fake_seers)

        # それでも候補がいない場合、ランダムに生存者を候補に追加
        if not candidates:
            candidates = self.get_alive_others(self.game_info.agent_list)

        # 投票対象を宣言（初回または候補が変更された場合）
        if self.vote_candidate == AGENT_NONE or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate != AGENT_NONE:
                return Content(VoteContentBuilder(self.vote_candidate))

        # 特に発言がない場合はスキップ
        return CONTENT_SKIP

