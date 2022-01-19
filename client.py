import socket
import json
from typing import Optional, List
from gameinfo import GameInfo
from gamesetting import GameSetting
from player import Player
from packet import Packet
from utterance import Utterance


class TcpipClient:

    def __init__(self, player: Player, name: str, host: str, port: int, request_role: str) -> None:
        self.player = player
        self.name = name
        self.host = host
        self.port = port
        self.request_role = request_role
        self.game_info: Optional[GameInfo] = None
        self.last_game_info: Optional[GameInfo] = None
        self.sock: Optional[socket.socket] = None

    def send_response(self, response: Optional[str]) -> None:
        if  isinstance(self.sock, socket.socket) and isinstance(response, str):
            self.sock.send((response + "\n").encode("utf-8"))

    def get_response(self, packet: Packet) -> Optional[str]:
        request: str = packet["request"]
        if request == "NAME":
            return self.name
        elif request == "ROLE":
            return self.request_role

        self.game_info = packet["gameInfo"]
        if self.game_info is None:
            self.game_info = self.last_game_info
        else:
            self.last_game_info = self.game_info
        if self.game_info is None:
            return None

        talk_history: Optional[List[Utterance]] = packet["talkHistory"]
        if talk_history is not None:
            for talk in talk_history:
                talk_list: List[Utterance] = self.game_info["talkList"]
                if len(talk_list) == 0:
                    talk_list.append(talk)
                else:
                    last_talk: Utterance = talk_list[-1]
                    if talk["day"] > last_talk["day"] or (talk["day"] == last_talk["day"] and talk["idx"] > last_talk["idx"]):
                        talk_list.append(talk)
        whisper_history: Optional[List[Utterance]] = packet["whisperHistory"]
        if whisper_history is not None:
            for whisper in whisper_history:
                whisper_list: List[Utterance] = self.game_info["whisperList"]
                if len(whisper_list) == 0:
                    whisper_list.append(whisper)
                else:
                    last_whisper: Utterance = whisper_list[-1]
                    if whisper["day"] > last_whisper["day"] or (whisper["day"] == last_whisper["day"] and whisper["idx"] > last_whisper["idx"]):
                        whisper_list.append(whisper)

        if request == "INITIALIZE":
            gs : Optional[GameSetting] = packet["gameSetting"]
            if gs is not None:
                self.player.initialize(self.game_info, gs)
            return None
        else:
            self.player.update(self.game_info)
            if request == "DAILY_INITIALIZE":
                self.player.day_start()
                return None
            elif request == "DAILY_FINISH":
                return None
            elif request == "FINISH":
                self.player.finish()
                return None
            elif request == "VOTE":
                return json.dumps({"agentIdx": self.player.vote()}, separators=(",", ":"))
            elif request == "ATTACK":
                return json.dumps({"agentIdx": self.player.attack()}, separators=(",", ":"))
            elif request == "GUARD":
                return json.dumps({"agentIdx": self.player.guard()}, separators=(",", ":"))
            elif request == "DIVINE":
                return json.dumps({"agentIdx": self.player.divine()}, separators=(",", ":"))
            elif request == "TALK":
                return self.player.talk().get_text()
            elif request == "WHISPER":
                return self.player.whisper().get_text()
        return None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(0.001)
        self.sock.connect((self.host, self.port))
        line: str = ""

        while True:

            try:
                line += self.sock.recv(8192).decode("utf-8")
                if line == "":
                    break
            except socket.timeout:
                pass

            line_list: List[str] = line.split("\n", 1)

            for i in range(len(line_list) - 1):
                if len(line_list[i]) > 0:
                    self.send_response(self.get_response(json.loads(line_list[i])))
                line = line_list[-1]

            try:
                self.send_response(self.get_response(json.loads(line)))
                line = ""
            except ValueError:
                pass

        self.sock.close()
        return None
