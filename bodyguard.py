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
    """Sample bodyguard agent."""

    to_be_guarded: Agent
    """Target of guard."""

    def __init__(self) -> None:
        """Initialize a new instance of SampleBodyguard."""
        super().__init__()
        self.to_be_guarded = AGENT_NONE

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.to_be_guarded = AGENT_NONE

    def guard(self) -> Agent:
        # Guard one of the alive non-fake seers.
        candidates: List[Agent] = self.get_alive([j.agent for j in self.divination_reports
                                                  if j.result != Species.WEREWOLF or j.target != self.me])
        # Guard one of the alive mediums if there are no candidates.
        if not candidates:
            candidates = [a for a in self.comingout_map if self.is_alive(a)
                          and self.comingout_map[a] == Role.MEDIUM]
        # Guard one of the alive sagents if there are no candidates.
        if not candidates:
            candidates = self.get_alive_others(self.game_info.agent_list)
        # Update a guard candidate if the candidate is changed.
        if self.to_be_guarded == AGENT_NONE or self.to_be_guarded not in candidates:
            self.to_be_guarded = self.random_select(candidates)
        return self.to_be_guarded if self.to_be_guarded != AGENT_NONE else self.me
