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

from aiwolf import (Agent, AttackContentBuilder, ComingoutContentBuilder,
                    Content, GameInfo, GameSetting, Judge, Role, Species)
from aiwolf.constant import AGENT_NONE

from const import CONTENT_SKIP, JUDGE_EMPTY
from possessed import SamplePossessed


class SampleWerewolf(SamplePossessed):
    """Sample werewolf agent."""

    allies: List[Agent]
    """Allies."""
    humans: List[Agent]
    """Humans."""
    attack_vote_candidate: Agent
    """The candidate for the attack voting."""

    def __init__(self) -> None:
        """Initialize a new instance of SampleWerewolf."""
        super().__init__()
        self.allies = []
        self.humans = []
        self.attack_vote_candidate = AGENT_NONE

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.allies = list(self.game_info.role_map.keys())
        self.humans = [a for a in self.game_info.agent_list if a not in self.allies]
        # Do comingout on the day that randomly selected from the 1st, 2nd and 3rd day.
        self.co_date = random.randint(1, 3)
        # Choose fake role randomly.
        self.fake_role = random.choice([r for r in [Role.VILLAGER, Role.SEER, Role.MEDIUM]
                                        if r in self.game_info.existing_role_list])

    def get_fake_judge(self) -> Judge:
        """Generate a fake judgement."""
        # Determine the target of the fake judgement.
        target: Agent = AGENT_NONE
        if self.fake_role == Role.SEER:  # Fake seer chooses a target randomly.
            if self.game_info.day != 0:
                target = self.random_select(self.get_alive(self.not_judged_agents))
        elif self.fake_role == Role.MEDIUM:
            target = self.game_info.executed_agent if self.game_info.executed_agent is not None \
                else AGENT_NONE
        if target == AGENT_NONE:
            return JUDGE_EMPTY
        # Determine a fake result.
        # If the target is a human
        # and the number of werewolves found is less than the total number of werewolves,
        # judge as a werewolf with a probability of 0.3.
        result: Species = Species.WEREWOLF if target in self.humans \
            and len(self.werewolves) < self.num_wolves and random.random() < 0.3 \
            else Species.HUMAN
        return Judge(self.me, self.game_info.day, target, result)

    def day_start(self) -> None:
        super().day_start()
        self.attack_vote_candidate = AGENT_NONE

    def whisper(self) -> Content:
        # Declare the fake role on the 1st day,
        # and declare the target of attack vote after that.
        if self.game_info.day == 0:
            return Content(ComingoutContentBuilder(self.me, self.fake_role))
        # Choose the target of attack vote.
        # Vote for one of the agent that did comingout.
        candidates = [a for a in self.get_alive(self.humans) if a in self.comingout_map]
        # Vote for one of the alive human agents if there are no candidates.
        if not candidates:
            candidates = self.get_alive(self.humans)
        # Declare which to vote for if not declare yet or the candidate is changed.
        if self.attack_vote_candidate == AGENT_NONE or self.attack_vote_candidate not in candidates:
            self.attack_vote_candidate = self.random_select(candidates)
            if self.attack_vote_candidate != AGENT_NONE:
                return Content(AttackContentBuilder(self.attack_vote_candidate))
        return CONTENT_SKIP

    def attack(self) -> Agent:
        return self.attack_vote_candidate if self.attack_vote_candidate != AGENT_NONE else self.me
