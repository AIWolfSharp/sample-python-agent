from typing import TypedDict
from judge import Judge
from utterance import Utterance

class GameInfo(TypedDict):
    agent: int
    attacVoteList: list[dict[str, int]]
    attackedAgent: int
    cursedFox: int
    day: int
    divineResult: Judge
    executedAgent: int
    existingRoleList: list[str]
    guardedAgent: int
    lastDeadAgentList: list[int]
    latestAttackVoteList: list[dict[str, int]]
    latestExecutedAgent: int
    latestVoteList: list[dict[str, int]]
    mediumResult: Judge
    remainTalkMap: dict[str, int]
    remainWhisperMap: dict[str, int]
    roleMap: dict[str, str]
    statusMap: dict[str, str]
    talkList: list[Utterance]
    voteList: list[dict[str, int]]
    whisperList: list[Utterance]
