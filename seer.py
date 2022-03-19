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

from queue import Queue
from typing import List, Optional

from aiwolf import (Agent, ComingoutContentBuilder, Constant, Content,
                    DivinedResultContentBuilder, GameInfo, GameSetting, Judge,
                    Role, Species, VoteContentBuilder)

from villager import SampleVillager


class SampleSeer(SampleVillager):
    """Sample seer agent."""

    def __init__(self) -> None:
        """Initialize a new instance of SampleSeer."""
        super().__init__()
        self.co_date: int = 3  # Scheduled comingout date.
        self.has_co: bool = False  # Whether or not comingout has done.
        self.my_judge_queue: Queue[Judge] = Queue()  # Queue of divination results.
        self.not_divined_agents: List[Agent] = []  # Agents that have not been divined.
        self.werewolves: List[Agent] = []  # Found werewolves.

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.has_co = False
        self.my_judge_queue = Queue()
        self.not_divined_agents = self.get_others(self.agent_list)
        self.werewolves = []

    def day_start(self) -> None:
        super().day_start()
        # Process a divination result.
        judge: Optional[Judge] = None if self.game_info is None else self.game_info.divine_result
        if judge is not None:
            self.my_judge_queue.put(judge)
            if judge.target in self.not_divined_agents:
                self.not_divined_agents.remove(judge.target)
            if judge.result is Species.WEREWOLF:
                self.werewolves.append(judge.target)

    def talk(self) -> Content:
        if self.game_info is None:
            return type(self).CONTENT_SKIP
        # Do comingout if it's on scheduled day or a werewolf is found.
        if not self.has_co and (self.game_info.day == self.co_date or self.werewolves):
            self.has_co = True
            return Content(ComingoutContentBuilder(self.me, Role.SEER))
        # Report the divination result after doing comingout.
        if self.has_co and not self.my_judge_queue.empty():
            judge: Judge = self.my_judge_queue.get()
            return Content(DivinedResultContentBuilder(judge.target, judge.result))
        # Vote for one of the alive werewolves.
        candidates: List[Agent] = self.get_alive(self.werewolves)
        # Vote for one of the alive fake seers if there are no candidates.
        if not candidates:
            candidates = self.get_alive([a for a in self.comingout_map.keys() if self.comingout_map[a] is Role.SEER])
        # Vote for one of the alive agents if there are no candidates.
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # Declare which to vote for if not declare yet or the candidate is changed.
        if self.vote_candidate is Constant.AGENT_NONE or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate is not Constant.AGENT_NONE:
                return Content(VoteContentBuilder(self.vote_candidate))
        return type(self).CONTENT_SKIP

    def divine(self) -> Agent:
        # Divine a agent randomly chosen from undivined agents.
        target: Agent = self.random_select(self.not_divined_agents)
        return target if target is not Constant.AGENT_NONE else self.me
