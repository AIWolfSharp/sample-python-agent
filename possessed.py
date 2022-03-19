#
# possessed.py
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
from queue import Queue
from typing import List, Optional

from aiwolf import (Agent, ComingoutContentBuilder, Constant, Content,
                    DivinedResultContentBuilder, GameInfo, GameSetting,
                    IdentContentBuilder, Judge, Role, Species,
                    VoteContentBuilder)

from villager import SampleVillager


class SamplePossessed(SampleVillager):
    """Sample possessed agent."""

    def __init__(self) -> None:
        """Initialize a new instance of SamplePossessed."""
        super().__init__()
        self.fake_role: Role = Role.SEER  # Fake role.
        self.co_date: int = 1  # Scheduled comingout date.
        self.has_co: bool = False  # Whether or not comingout has done.
        self.my_judgee_queue: Queue[Judge] = Queue()  # Queue of fake judgements.
        self.not_judged_agents: List[Agent] = []  # Agents that have not been judged.
        self.num_wolves: int = 0  # The number of werewolves.
        self.werewolves: List[Agent] = []  # Fake werewolves.

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.fake_role = Role.SEER
        self.co_date = 1  # Do comingout on the first day.
        self.has_co = False
        self.my_judgee_queue = Queue()
        self.not_judged_agents = self.get_others(self.agent_list)
        self.num_wolves = game_setting.role_num_map[Role.WEREWOLF]
        self.werewolves = []

    def get_fake_judge(self) -> Optional[Judge]:
        """Generate a fake judgement."""
        if self.game_info is None:
            return None
        target: Agent = Constant.AGENT_NONE
        if self.fake_role is Role.SEER:  # Fake seer chooses a target randomly.
            if self.game_info.day != 0:
                target = self.random_select(self.get_alive(self.not_judged_agents))
        elif self.fake_role is Role.MEDIUM:
            target = self.game_info.executed_agent if self.game_info.executed_agent is not None else Constant.AGENT_NONE
        # Determine a fake result.
        result: Species = Species.HUMAN
        # If the number of werewolves found is less than the total number of werewolves,
        # judge as a werewolf with a probability of 0.5.
        if len(self.werewolves) < self.num_wolves and random.random() < 0.5:
            result = Species.WEREWOLF
        return None if target is Constant.AGENT_NONE else Judge(self.me, self.game_info.day, target, result)

    def day_start(self) -> None:
        super().day_start()
        # Process the fake judgement.
        judge: Optional[Judge] = self.get_fake_judge()
        if judge is not None:
            self.my_judgee_queue.put(judge)
            if judge.target in self.not_judged_agents:
                self.not_judged_agents.remove(judge.target)
            if judge.result is Species.WEREWOLF:
                self.werewolves.append(judge.target)

    def talk(self) -> Content:
        if self.game_info is None:
            return type(self).CONTENT_SKIP
        # Do comingout if it's on scheduled day or a werewolf is found.
        if self.fake_role is not Role.VILLAGER and not self.has_co and (self.game_info.day == self.co_date or self.werewolves):
            self.has_co = True
            return Content(ComingoutContentBuilder(self.me, self.fake_role))
        # Report the judgement after doing comingout.
        if self.has_co and not self.my_judgee_queue.empty():
            judge: Judge = self.my_judgee_queue.get()
            if self.fake_role is Role.SEER:
                return Content(DivinedResultContentBuilder(judge.target, judge.result))
            elif self.fake_role is Role.MEDIUM:
                return Content(IdentContentBuilder(judge.target, judge.result))
        # Vote for one of the alive fake werewolves.
        candidates: List[Agent] = self.get_alive(self.werewolves)
        # Vote for one of the alive agent that declared itself the same role of Possessed
        # if there are no candidates.
        if not candidates:
            candidates = self.get_alive([a for a in self.comingout_map.keys() if self.comingout_map[a] == self.fake_role])
        # Vite for one of the alive agents if there are no candidates.
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # Declare which to vote for if not declare yet or the candidate is changed.
        if self.vote_candidate is Constant.AGENT_NONE or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate is not Constant.AGENT_NONE:
                return Content(VoteContentBuilder(self.vote_candidate))
        return type(self).CONTENT_SKIP
