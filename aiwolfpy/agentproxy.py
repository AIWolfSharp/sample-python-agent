import socket
import json
from aiwolfpy.gameinfoparser import GameInfoParser


# decorator / proxy
class AgentProxy(object):

    def __init__(self, agent, my_name, host_name, port, role, logger, parse="pandas"):
        self.agent = agent
        self.my_name = my_name
        self.host_name = host_name
        self.port = port
        self.role = role
        self.sock = None
        self.parser = GameInfoParser()
        self.base_info = dict()
        self.parse_choice = parse
        self.logger = logger
        self.len_whisper_list = 0

    # parse and run
    def initialize_agent(self, game_info, game_setting):
        if self.parse_choice == "pandas":
            self.parser.initialize(game_info, game_setting)
            self.base_info = dict()
            self.base_info['agentIdx'] = game_info['agent']
            self.base_info['myRole'] = game_info["roleMap"][str(game_info['agent'])]
            self.base_info["roleMap"] = game_info["roleMap"]
            diff_data = self.parser.get_game_df_diff()
            self.logger.debug("INITIALIZE")
            self.logger.debug(self.base_info)
            self.logger.debug(diff_data)
            self.agent.initialize(self.base_info,  diff_data, game_setting)
            return None
        else:
            self.agent.initialize(game_info, game_setting)

    # parse and run
    def update_agent(self, game_info, talk_history, whisper_history, request):
        if self.parse_choice == "pandas":
            for k in ["day", "remainTalkMap", "remainWhisperMap", "statusMap"]:
                if k in game_info.keys():
                    self.base_info[k] = game_info[k]
            self.parser.update(game_info, talk_history, whisper_history, request)
            diff_data = self.parser.get_game_df_diff()
            self.logger.debug(request)
            self.logger.debug(self.base_info)
            self.logger.debug(diff_data)
            self.agent.update(self.base_info, diff_data, request)
            return None
        else:
            self.agent.update(game_info, talk_history, whisper_history, request)

    def send_response(self, json_received):
        res_txt = self._get_json(json_received)
        if res_txt is None:
            pass
        else:
            self.sock.send((res_txt + '\n').encode('utf-8'))
        return None

    def _get_json(self, json_received):
        game_info = json_received['gameInfo']
        if game_info is None:
            game_info = dict()
        # talk_history and whisper_history
        talk_history = json_received['talkHistory']
        if talk_history is None:
            talk_history = []
        whisper_history = json_received['whisperHistory']
        if whisper_history is None:
            whisper_history = []

        # delete unnecessary talk and whisper
        if 'talkList' in game_info.keys():
            del game_info['talkList']
        if 'whisperList' in game_info.keys():
            whisper_history = game_info['whisperList'][self.len_whisper_list:]
            self.len_whisper_list = len(game_info['whisperList'])
            del game_info['whisperList']

        # request must exist
        request = json_received['request']
        self.logger.log(1, request)
        self.logger.log(1, game_info)
        self.logger.log(1, talk_history)
        self.logger.log(1, whisper_history)
        if request == 'INITIALIZE':
            game_setting = json_received['gameSetting']
            self.logger.log(1, game_setting)
        else:
            game_setting = None

        # run_request
        if request == 'NAME':
            return self.my_name
        elif request == 'ROLE':
            return self.role
        elif request == 'INITIALIZE':
            self.initialize_agent(game_info, game_setting)
            return None
        else:
            # UPDATE
            self.update_agent(game_info, talk_history, whisper_history, request)
            if request == 'DAILY_INITIALIZE':
                self.len_whisper_list = 0
                self.agent.dayStart()
                return None
            elif request == 'DAILY_FINISH':
                return None
            elif request == 'FINISH':
                self.agent.finish()
                return None
            elif request == 'VOTE':
                return json.dumps({'agentIdx': int(self.agent.vote())}, separators=(',', ':'))
            elif request == 'ATTACK':
                return json.dumps({'agentIdx': int(self.agent.attack())}, separators=(',', ':'))
            elif request == 'GUARD':
                return json.dumps({'agentIdx': int(self.agent.guard())}, separators=(',', ':'))
            elif request == 'DIVINE':
                return json.dumps({'agentIdx': int(self.agent.divine())}, separators=(',', ':'))
            elif request == 'TALK':
                return self.agent.talk().__str__()
            elif request == 'WHISPER':
                return self.agent.whisper().__str__()

    def connect_server(self):
        # socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(0.001)
        # connect
        self.sock.connect((self.host_name, self.port))
        line = ''

        while True:

            try:
                line += self.sock.recv(8192).decode('utf-8')
                if line == '':
                    break
            except socket.timeout:
                pass

            line_list = line.split("\n", 1)

            for i in range(len(line_list) - 1):
                if len(line_list[i]) > 0:
                    json_received = json.loads(line_list[i])
                    self.send_response(json_received)
                line = line_list[-1]

            try:
                # check if valid json
                json_received = json.loads(line)
                self.send_response(json_received)
                line = ''
            except ValueError:
                pass

        self.sock.close()
        return None
