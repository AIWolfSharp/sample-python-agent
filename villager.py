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
from typing import Dict, List, Optional

from aiwolf import (AbstractPlayer, Agent, Constant, Content, GameInfo,
                    GameSetting, Judge, Role, SkipContentBuilder, Species,
                    Status, Talk, Topic, VoteContentBuilder)


class SampleVillager(AbstractPlayer):
    """Sample villager agent."""

    CONTENT_SKIP = Content(SkipContentBuilder())

    def __init__(self) -> None:
        """Initialize a new instance of SampleVillager."""

        self.me: Agent = Constant.AGENT_NONE
        """Myself."""

        self.vote_candidate: Agent = Constant.AGENT_NONE
        """Candidate for voting."""

        self.game_info: Optional[GameInfo] = None
        """Information about current game."""

        self.comingout_map: Dict[Agent, Role] = {}
        """Mapping between an agent and the role it claims that it is."""

        self.divination_reports: List[Judge] = []
        """Time series of divination reports."""

        self.identification_reports: List[Judge] = []
        """Time series of identification reports."""

        self.talk_list_head: int = 0
        """Index of the talk to be analysed next."""

        self.agent_list: List[Agent] = []
        """List of existing agents."""

    def is_alive(self, agent: Agent) -> bool:
        """Return whether the agent is alive.

        Args:
            agent: The agent.

        Returns:
            True if the agent is alive, otherwise false.
        """
        return self.game_info is not None and self.game_info.status_map[agent] is Status.ALIVE

    def get_others(self, agent_list: List[Agent]) -> List[Agent]:
        """Return a list of agents excluding myself from the given list of agents.

        Args:
            agent_list: The list of agent.

        Returns:
            A list of agents excluding myself from agent_list.
        """
        return [a for a in agent_list if a is not self.me]

    def get_alive(self, agent_list: List[Agent]) -> List[Agent]:
        """Return a list of alive agents contained in the given list of agents.

        Args:
            agent_list: The list of agents.

        Returns:
            A list of alive agents contained in agent_list.
        """
        return [a for a in agent_list if self.is_alive(a)]

    def get_alive_others(self, agent_list: List[Agent]) -> List[Agent]:
        """Return a list of alive agents that is contained in the given list of agents
        and is not equal to myself.

        Args:
            agent_list: The list of agents.

        Returns:
            A list of alie agents that is contained in agent_list
            and is not equal to mysef.
        """
        return self.get_alive(self.get_others(agent_list))

    def random_select(self, agent_list: List[Agent]) -> Agent:
        """Return one agent randomly chosen from the given list of agents.

        Args:
            agent_list: The list of agents.

        Returns:
            A agent randomly chosen from agent_list.
        """
        return random.choice(agent_list) if agent_list else Constant.AGENT_NONE

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        self.game_info = game_info
        self.me = game_info.me
        self.agent_list = list(game_info.status_map.keys())
        # Clear fields not to bring in information from the last game.
        self.comingout_map = {}
        self.divination_reports = []
        self.identification_reports = []

    def day_start(self) -> None:
        self.talk_list_head = 0
        self.vote_candidate = Constant.AGENT_NONE

    def update(self, game_info: GameInfo) -> None:
        self.game_info = game_info  # Update game information.
        for i in range(self.talk_list_head, len(game_info.talk_list)):  # Analyze talks that have not been analyzed yet.
            tk: Talk = game_info.talk_list[i]  # The talk to be analyzed.
            talker: Agent = tk.agent
            if talker is self.me:  # Skip my talk.
                continue
            content: Content = Content.compile(tk.text)
            if content.topic is Topic.COMINGOUT:
                self.comingout_map[talker] = content.role
            elif content.topic is Topic.DIVINED:
                self.divination_reports.append(Judge(talker, game_info.day, content.target, content.result))
            elif content.topic is Topic.IDENTIFIED:
                self.identification_reports.append(Judge(talker, game_info.day, content.target, content.result))
        self.talk_list_head = len(game_info.talk_list)  # All done.

    def talk(self) -> Content:
        # Choose an agent to be voted for while talking.

        # The list of fake seers that reported me, the human, as a werewolf.
        fake_seers: List[Agent] = [j.agent for j in self.divination_reports if j.target is self.me and j.result is Species.WEREWOLF]
        # Vote for one of the alive agents that were judged as werewolves by non-fake seers.
        reported_wolves: List[Agent] = [j.target for j in self.divination_reports if j.agent not in fake_seers and j.result is Species.WEREWOLF]
        candidates: List[Agent] = self.get_alive_others(reported_wolves)
        # Vote for one of the alive fake seers if there are no candidates.
        if not candidates:
            candidates = self.get_alive(fake_seers)
        # Vote for one of the alive agents if there are no candidates.
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # Declare which to vote for if not declare yet or the candidate is changed.
        if self.vote_candidate is Constant.AGENT_NONE or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(list(set(candidates)))
            if self.vote_candidate is not Constant.AGENT_NONE:
                return Content(VoteContentBuilder(self.vote_candidate))
        return type(self).CONTENT_SKIP

    def vote(self) -> Agent:
        return self.vote_candidate if self.vote_candidate is not Constant.AGENT_NONE else self.me

    def attack(self) -> Agent:
        raise Exception("Unexpected function call")  # Raise an exception in case of misuse.

    def divine(self) -> Agent:
        raise Exception("Unexpected function call")  # Raise an exception in case of misuse.

    def guard(self) -> Agent:
        raise Exception("Unexpected function call")  # Raise an exception in case of misuse.

    def whisper(self) -> Content:
        raise Exception("Unexpected function call")  # Raise an exception in case of misuse.

    def finish(self) -> None:
        pass
