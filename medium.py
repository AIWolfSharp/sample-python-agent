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

from queue import Queue
from typing import List, Optional

from aiwolf import (Agent, ComingoutContentBuilder, Constant, Content,
                    GameInfo, GameSetting, IdentContentBuilder, Judge, Role,
                    Species, VoteContentBuilder)

from villager import SampleVillager


class SampleMedium(SampleVillager):
    """ Sample medium agent. """

    def __init__(self) -> None:
        """Initialize a new instance of SampleMedium."""
        super().__init__()
        self.co_date: int = 3  # Scheduled comingout date.
        self.found_wolf: bool = False  # Whether or not a werewolf is found.
        self.has_co: bool = False  # Whether or not comingout has done.
        self.my_judge_queue: Queue[Judge] = Queue()  # Queue of medium results.

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.found_wolf = False
        self.has_co = False
        self.my_judge_queue = Queue()

    def day_start(self) -> None:
        super().day_start()
        # Queue the medium result.
        judge: Optional[Judge] = None if self.game_info is None else self.game_info.medium_result
        if judge is not None:
            self.my_judge_queue.put(judge)
            if judge.result is Species.WEREWOLF:
                self.found_wolf = True

    def talk(self) -> Content:
        if self.game_info is None:
            return type(self).CONTENT_SKIP
        # Do comingout if it's on scheduled day or a werewolf is found.
        if not self.has_co and (self.game_info.day == self.co_date or self.found_wolf):
            self.has_co = True
            return Content(ComingoutContentBuilder(self.me, Role.MEDIUM))
        # Report the medium result after doing comingout.
        if self.has_co and not self.my_judge_queue.empty():
            judge: Judge = self.my_judge_queue.get()
            return Content(IdentContentBuilder(judge.target, judge.result))
        # Fake seers.
        fake_seers: List[Agent] = [j.agent for j in self.divination_reports if j.target is self.me and j.result is Species.WEREWOLF]
        # Vote for one of the alive fake mediums.
        candidates: List[Agent] = [a for a in self.comingout_map.keys() if self.is_alive(a) and self.comingout_map[a] is Role.MEDIUM]
        # Vote for one of the alive agents that were judged as werewolves by non-fake seers if there are no candidates.
        reported_wolves: List[Agent] = [j.target for j in self.divination_reports if j.agent not in fake_seers and j.result is Species.WEREWOLF]
        candidates = self.get_alive_others(reported_wolves)
        # Vote for one of the alive fake seers if there are no candidates.
        if not candidates:
            candidates = self.get_alive(fake_seers)
        # Vote for one of the alive agents if there are no candidates.
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # Declare which to vote for if not declare yet or the candidate is changed.
        if self.vote_candidate is Constant.AGENT_NONE or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate is not Constant.AGENT_NONE:
                return Content(VoteContentBuilder(self.vote_candidate))
        return type(self).CONTENT_SKIP
