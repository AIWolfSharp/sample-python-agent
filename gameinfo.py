from typing import TypedDict, Dict, List
from judge import Judge
from utterance import Utterance

class GameInfo(TypedDict):
    agent: int
    attacVoteList: List[Dict[str, int]]
    attackedAgent: int
    cursedFox: int
    day: int
    divineResult: Judge
    executedAgent: int
    existingRoleList: List[str]
    guardedAgent: int
    lastDeadAgentList: List[int]
    latestAttackVoteList: List[Dict[str, int]]
    latestExecutedAgent: int
    latestVoteList: List[Dict[str, int]]
    mediumResult: Judge
    remainTalkMap: Dict[str, int]
    remainWhisperMap: Dict[str, int]
    roleMap: Dict[str, str]
    statusMap: Dict[str, str]
    talkList: List[Utterance]
    voteList: List[Dict[str, int]]
    whisperList: List[Utterance]
