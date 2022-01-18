"""
villager.py

(c) 2022 OTSUKI Takashi

"""

import random
import re
from typing import Pattern
import aiwolfpy
from aiwolfpy.protocol.contentfactory import ContentFactory
from gameinfo import GameInfo
from gamesetting import GameSetting
from player import Player
from typing import Optional
from judge import Judge
from utterance import Utterance
from re import Match

class Villager(Player):
    """ 村人エージェント """

    cf: ContentFactory = aiwolfpy.ContentFactory()
    agent_pattern: Pattern[str] = re.compile("Agent\\[(..)\\]")

    def __init__(self) -> None:
        self.me: int = 0 # 自分
        self.vote_candidate: int = -1 # 投票先
        self.game_info: Optional[GameInfo] = None # ゲーム情報
        self.comingout_map: dict[int, str] = {} # カミングアウト状況
        self.divination_reports: list[Judge] = [] # 占い結果報告時系列
        self.identification_reports: list[Judge] = [] # 霊媒結果報告時系列
        self.talk_list_head: int = 0 # 未解析会話の先頭インデックス
        self.agent_list: list[int] = [] # 全エージェントのリスト

    def is_alive(self, agent: int) -> bool:
        """ エージェントが生きているかどうか """
        return self.game_info is not None and self.game_info["statusMap"][str(agent)] == "ALIVE"

    def get_others(self, agent_list: list[int]) -> list[int]:
        """ エージェントリストから自分を除いたリストを返す """
        return [a for a in agent_list if a != self.me]

    def get_alive(self, agent_list: list[int]) -> list[int]:
        """ エージェントリスト中の生存エージェントのリストを返す """
        return [a for a in agent_list if self.is_alive(a)]

    def get_alive_others(self, agent_list: list[int]) -> list[int]:
        """ エージェントリスト中の自分以外の生存エージェントのリストを返す """
        return self.get_alive(self.get_others(agent_list))

    def random_select(self, agent_list: list[int]) -> int:
        """ エージェントのリストからランダムに1エージェントを選んで返す """
        return random.choice(agent_list) if agent_list else -1

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        self.game_info = game_info
        self.me = game_info["agent"]
        self.agent_list = list(map(int, self.game_info["statusMap"].keys()))
        # 前のゲームを引きずらないようにフィールドをクリアしておく
        self.comingout_map = {}
        self.divination_reports = []
        self.identification_reports = []

    def day_start(self) -> None:
        self.talk_list_head = 0
        self.vote_candidate = -1

    def update(self, game_info: GameInfo) -> None:
        self.game_info = game_info # ゲーム状況更新
        talk_list: list[Utterance] = game_info["talkList"]
        for i in range(self.talk_list_head, len(talk_list)): # 未解析発話の解析
            talk: Utterance = talk_list[i] # 解析対象会話
            talker: int = talk["agent"] # 発言したエージェント
            if talker == self.me: # 自分の発言は解析しない
                continue
            sentence: list[str] = talk["text"].split()
            subject: int = talker
            offset: int = 0
            m0: Optional[Match[str]] = self.agent_pattern.match(sentence[0])
            if m0:
                offset = 1
                subject = int(m0.group(1))
            if sentence[offset] == "COMINGOUT":
                m1: Optional[Match[str]] = self.agent_pattern.match(sentence[offset+1])
                if m1:
                    self.comingout_map[int(m1.group(1))] = sentence[offset+2]
            elif sentence[offset] == "DIVINED":
                m1 = self.agent_pattern.match(sentence[offset+1])
                if m1:
                    self.divination_reports.append({"day": game_info["day"], "agent": subject, "target": int(m1.group(1)), "result": sentence[offset+2]})
            elif sentence[offset] == "IDENTIFIED":
                m1 = self.agent_pattern.match(sentence[offset+1])
                if m1:
                    self.identification_reports.append({"day": game_info["day"], "agent": subject, "target": int(m1.group(1)), "result": sentence[offset+2]})
        self.talk_list_head = len(talk_list) # すべてを解析済みとする

    def talk(self) -> str:
        # 会話をしながら投票先を決めていく

        # 村人である自分を人狼と判定した偽占い師のリスト
        fake_seers: set[int] = set()
        for j in self.divination_reports:
            if j["target"] == self.me and j["result"] == "WEREWOLF":
                fake_seers.add(j["agent"])
        # 偽でない自称占い師から人狼と判定された生存エージェントに投票
        reported_wolves: set[int] = set()
        for j in self.divination_reports:
            if j["agent"] not in fake_seers and j["result"] == "WEREWOLF":
                reported_wolves.add(j["target"])
        candidates: list[int] = self.get_alive_others(list(reported_wolves))
        # いなければ生存偽占い師に投票
        if not candidates:
            candidates = self.get_alive(list(fake_seers))
        # それでもいなければ生存エージェントに投票
        if not candidates:
            candidates = self.get_alive_others(self.agent_list)
        # 初めての投票先宣言あるいは変更ありの場合，投票先宣言
        if self.vote_candidate == -1 or self.vote_candidate not in candidates:
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate != -1:
                return self.cf.vote(self.vote_candidate) 
        return self.cf.skip()

    def vote(self) -> int:
        return self.vote_candidate if self.vote_candidate != -1 else self.me

    def attack(selt) -> int:
        raise Exception("Unexpected function call") # 誤使用の場合例外送出

    def divine(self) -> int:
        raise Exception("Unexpected function call") # 誤使用の場合例外送出

    def guard(self) -> int:
        raise Exception("Unexpected function call") # 誤使用の場合例外送出

    def whisper(self) -> str:
        raise Exception("Unexpected function call") # 誤使用の場合例外送出

    def finish(self) -> None:
        pass
