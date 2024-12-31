#
# werewolf.py
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
from typing import List

# 必要なクラスと定数をインポート
from aiwolf import (Agent, AttackContentBuilder, ComingoutContentBuilder,
                    Content, GameInfo, GameSetting, Judge, Role, Species)
from aiwolf.constant import AGENT_NONE  # AGENT_NONEは無効なエージェントを表す定数

from const import CONTENT_SKIP, JUDGE_EMPTY  # 他のモジュールから共通の定数をインポート
from possessed import SamplePossessed  # 人狼役の基底クラスとして狂人を継承


class SampleWerewolf(SamplePossessed):
    """
    サンプル人狼エージェントのクラス。
    狂人エージェント (SamplePossessed) を継承しており、人狼特有の行動を実装しています。
    """

    # クラス属性の定義
    allies: List[Agent]  # 仲間の人狼エージェント
    humans: List[Agent]  # 人間プレイヤーのリスト
    attack_vote_candidate: Agent  # 襲撃投票の候補者

    def __init__(self) -> None:
        """
        SampleWerewolfの新しいインスタンスを初期化します。
        このメソッドでは、属性の初期値を設定します。
        """
        super().__init__()  # 基底クラス (SamplePossessed) の初期化を呼び出す
        self.allies = []  # 仲間の人狼リストを空に初期化
        self.humans = []  # 人間プレイヤーリストを空に初期化
        self.attack_vote_candidate = AGENT_NONE  # 襲撃投票の候補を無効値に初期化

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        """
        ゲーム開始時の初期化を行います。
        ゲームの情報と設定を受け取り、初期状態を設定します。
        
        Args:
            game_info (GameInfo): ゲームの現在の情報。
            game_setting (GameSetting): ゲームの設定情報。
        """
        super().initialize(game_info, game_setting)  # 基底クラスの初期化を実行
        self.allies = list(self.game_info.role_map.keys())  # 自分と仲間の人狼をリスト化
        self.humans = [a for a in self.game_info.agent_list if a not in self.allies]  # 人狼以外のプレイヤーを抽出
        # 1日目から3日目のどこかで役職カミングアウトを行うため、その日をランダムに決定
        self.co_date = random.randint(1, 3)
        # 偽役職をランダムに選択（存在する役職の中から選ぶ）
        self.fake_role = random.choice([r for r in [Role.VILLAGER, Role.SEER, Role.MEDIUM]
                                        if r in self.game_info.existing_role_list])

    def get_fake_judge(self) -> Judge:
        """
        偽の判定（占いまたは霊能結果）を生成します。

        Returns:
            Judge: 偽の判定を表すJudgeオブジェクト。
        """
        # 初期値として無効なエージェントを設定
        target: Agent = AGENT_NONE

        # 偽占い師の場合、未判定のエージェントからランダムに選択
        if self.fake_role == Role.SEER:  
            if self.game_info.day != 0:  # 初日以外で実行
                target = self.random_select(self.get_alive(self.not_judged_agents))
        
        # 偽霊能者の場合、直前に処刑されたエージェントを対象にする
        elif self.fake_role == Role.MEDIUM:
            target = self.game_info.executed_agent if self.game_info.executed_agent is not None else AGENT_NONE
        
        # 判定対象が無効の場合、空の判定を返す
        if target == AGENT_NONE:
            return JUDGE_EMPTY

        # 偽判定結果を決定
        # 人間プレイヤーを人狼と判定する確率を30%とする
        result: Species = Species.WEREWOLF if target in self.humans \
            and len(self.werewolves) < self.num_wolves and random.random() < 0.3 \
            else Species.HUMAN

        # 判定を作成して返す
        return Judge(self.me, self.game_info.day, target, result)

    def day_start(self) -> None:
        """
        新しい日の開始時に呼び出されるメソッド。
        毎日のリセット処理を行います。
        """
        super().day_start()  # 基底クラスの処理を実行
        self.attack_vote_candidate = AGENT_NONE  # 襲撃投票候補をリセット

    def whisper(self) -> Content:
        """
        人狼同士のささやきで発言を生成します。

        Returns:
            Content: 発言の内容を表すContentオブジェクト。
        """
        if self.game_info.day == 0:
            # 初日は偽役職をカミングアウトする
            return Content(ComingoutContentBuilder(self.me, self.fake_role))
        
        # それ以降は襲撃投票のターゲットを選択して発言
        # カミングアウトしている人間を優先的に候補にする
        candidates = [a for a in self.get_alive(self.humans) if a in self.comingout_map]

        # カミングアウトしている人間がいない場合、全人間プレイヤーから選択
        if not candidates:
            candidates = self.get_alive(self.humans)
        
        # 新たな候補を選択し、変更があれば発言
        if self.attack_vote_candidate == AGENT_NONE or self.attack_vote_candidate not in candidates:
            self.attack_vote_candidate = self.random_select(candidates)
            if self.attack_vote_candidate != AGENT_NONE:
                return Content(AttackContentBuilder(self.attack_vote_candidate))
        
        # 発言しない場合はスキップ
        return CONTENT_SKIP

    def attack(self) -> Agent:
        """
        襲撃対象を決定します。

        Returns:
            Agent: 襲撃対象のエージェント。
        """
        # 襲撃候補が設定されていればそれを返し、未設定なら自身を返す（不整合防止のため）
        return self.attack_vote_candidate if self.attack_vote_candidate != AGENT_NONE else self.me

