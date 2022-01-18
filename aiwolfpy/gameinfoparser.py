import pandas as pd


class GameInfoParser(object):
    
    def __init__(self):
        self.pd_dict = {"day": [], "type": [], "idx": [], "turn": [], "agent": [], "text": []}
        self.agent_idx = 1
        self.finish_cnt = 0
        self.night_info = 0
        self.rows_returned = 0

    # pandas
    def initialize(self, game_info, game_setting):
        # me
        self.agent_idx = game_info['agent']
        # ROLE MAP on INITIAL
        self.pd_dict = {"day": [], "type": [], "idx": [], "turn": [], "agent": [], "text": []}
        self.finish_cnt = 0 
        self.night_info = 0
        
        # for diff
        self.rows_returned = 0
        
        for k in game_info["roleMap"].keys():
            self.pd_dict["day"].append(game_info["day"])
            self.pd_dict["type"].append('initialize')
            self.pd_dict["idx"].append(int(k))
            self.pd_dict["turn"].append(0)
            self.pd_dict["agent"].append(int(k))
            self.pd_dict["text"].append('COMINGOUT Agent[' + "{0:02d}".format(int(k)) + '] ' + game_info["roleMap"][k])

    def get_game_df(self):
        return pd.DataFrame(self.pd_dict)
        
    def get_game_df_diff(self):
        ret_df = pd.DataFrame({
            "day":self.pd_dict["day"][self.rows_returned:], 
            "type":self.pd_dict["type"][self.rows_returned:], 
            "idx":self.pd_dict["idx"][self.rows_returned:], 
            "turn":self.pd_dict["turn"][self.rows_returned:], 
            "agent":self.pd_dict["agent"][self.rows_returned:], 
            "text":self.pd_dict["text"][self.rows_returned:]
        })
        self.rows_returned = len(self.pd_dict["day"])
        return ret_df

    def update(self, game_info, talk_history, whisper_history, request):

        # talk
        for t in talk_history:
            self.pd_dict["day"].append(t["day"])
            self.pd_dict["type"].append("talk")
            self.pd_dict["idx"].append(t["idx"])
            self.pd_dict["turn"].append(t["turn"])
            self.pd_dict["agent"].append(t["agent"])
            self.pd_dict["text"].append(t["text"])
            
        # whisper
        for w in whisper_history:
            self.pd_dict["day"].append(w["day"])
            self.pd_dict["type"].append("whisper")
            self.pd_dict["idx"].append(w["idx"])
            self.pd_dict["turn"].append(w["turn"])
            self.pd_dict["agent"].append(w["agent"])
            self.pd_dict["text"].append(w["text"])
        
        if request == 'DAILY_INITIALIZE':
            
            # VOTE
            if self.night_info == 0:
                # valid vote
                for v in game_info['voteList']:
                    self.pd_dict["day"].append(v["day"])
                    self.pd_dict["type"].append("vote")
                    self.pd_dict["idx"].append(v["agent"])
                    self.pd_dict["turn"].append(0)
                    self.pd_dict["agent"].append(v["target"])
                    self.pd_dict["text"].append('VOTE Agent[' + "{0:02d}".format(v["target"]) + ']')
                    
            # EXECUTE
            if game_info['executedAgent'] != -1 and self.night_info == 0:
                self.pd_dict["day"].append(game_info['day'] - 1)
                self.pd_dict["type"].append("execute")
                self.pd_dict["idx"].append(0)
                self.pd_dict["turn"].append(0)
                self.pd_dict["agent"].append(game_info['executedAgent'])
                self.pd_dict["text"].append('Over')
                
            # IDENTIFY
            if game_info['mediumResult'] is not None:
                m = game_info['mediumResult']
                self.pd_dict["day"].append(m['day'])
                self.pd_dict["type"].append("identify")
                self.pd_dict["idx"].append(m['agent'])
                self.pd_dict["turn"].append(0)
                self.pd_dict["agent"].append(game_info['executedAgent'])
                self.pd_dict["text"].append('IDENTIFIED Agent[' + "{0:02d}".format(m['target']) + '] ' + m['result'])
                
            # DIVINE
            if game_info['divineResult'] is not None:
                d = game_info['divineResult']
                self.pd_dict["day"].append(d['day'] - 1)
                self.pd_dict["type"].append("divine")
                self.pd_dict["idx"].append(d['agent'])
                self.pd_dict["turn"].append(0)
                self.pd_dict["agent"].append(d['target'])
                self.pd_dict["text"].append('DIVINED Agent[' + "{0:02d}".format(d['target']) + '] ' + d['result'])
                
            # GUARD
            if game_info['guardedAgent'] != -1:
                self.pd_dict["day"].append(game_info['day'] - 1)
                self.pd_dict["type"].append("guard")
                self.pd_dict["idx"].append(self.agent_idx)
                self.pd_dict["turn"].append(0)
                self.pd_dict["agent"].append(game_info['guardedAgent'])
                self.pd_dict["text"].append('GUARDED Agent[' + "{0:02d}".format(game_info['guardedAgent']) + ']')
                
            # ATTACK_VOTE
            # valid attack_vote
            for v in game_info['attackVoteList']:
                self.pd_dict["day"].append(v["day"])
                self.pd_dict["type"].append("attack_vote")
                self.pd_dict["idx"].append(v["agent"])
                self.pd_dict["turn"].append(0)
                self.pd_dict["agent"].append(v["target"])
                self.pd_dict["text"].append('ATTACK Agent[' + "{0:02d}".format(v["target"]) + ']')
                                
            # ATTACK
            if game_info['attackedAgent'] != -1:
                self.pd_dict["day"].append(game_info['day'] - 1)
                self.pd_dict["type"].append("attack")
                self.pd_dict["idx"].append(0)
                self.pd_dict["turn"].append(0)
                self.pd_dict["agent"].append(game_info['attackedAgent'])
                self.pd_dict["text"].append('ATTACK Agent[' + "{0:02d}".format(game_info['attackedAgent']) + ']')
                
            # DEAD
            for i in range(len(game_info['lastDeadAgentList'])):
                self.pd_dict["day"].append(game_info['day'])
                self.pd_dict["type"].append("dead")
                self.pd_dict["idx"].append(i)
                self.pd_dict["turn"].append(0)
                self.pd_dict["agent"].append(game_info['lastDeadAgentList'][i])
                self.pd_dict["text"].append('Over')
                
            self.night_info = 0
                
        # VOTE/EXECUTE before action
        elif request in ['DIVINE', 'GUARD', 'ATTACK', 'WHISPER'] and self.night_info == 0:
            # VOTE
            if 'latestVoteList' in game_info.keys():
                # valid vote
                for v in game_info['latestVoteList']:
                    self.pd_dict["day"].append(v["day"])
                    self.pd_dict["type"].append("vote")
                    self.pd_dict["idx"].append(v["agent"])
                    self.pd_dict["turn"].append(0)
                    self.pd_dict["agent"].append(v["target"])
                    self.pd_dict["text"].append('VOTE Agent[' + "{0:02d}".format(v["target"]) + ']')
                    
            # EXECUTE
            if 'latestExecutedAgent' in game_info.keys():
                if game_info['latestExecutedAgent'] != -1:
                    self.pd_dict["day"].append(game_info['day'])
                    self.pd_dict["type"].append("execute")
                    self.pd_dict["idx"].append(0)
                    self.pd_dict["turn"].append(0)
                    self.pd_dict["agent"].append(game_info['latestExecutedAgent'])
                    self.pd_dict["text"].append('Over')
            
            self.night_info = 1

        # RE_VOTE
        elif request == 'VOTE':
            # VOTE
            if 'latestVoteList' in game_info.keys():
                # valid vote
                for v in game_info['latestVoteList']:
                    self.pd_dict["day"].append(v["day"])
                    self.pd_dict["type"].append("vote")
                    self.pd_dict["idx"].append(v["agent"])
                    self.pd_dict["turn"].append(-1)
                    self.pd_dict["agent"].append(v["target"])
                    self.pd_dict["text"].append('VOTE Agent[' + "{0:02d}".format(v["target"]) + ']')
                    
        # RE_ATTACK_VOTE
        elif request == 'ATTACK':
            # ATTACK_VOTE 
            if 'latestAttackVoteList' in game_info.keys():
                for v in game_info['latestAttackVoteList']:
                    self.pd_dict["day"].append(v["day"])
                    self.pd_dict["type"].append("attack_vote")
                    self.pd_dict["idx"].append(v["agent"])
                    self.pd_dict["turn"].append(-1)
                    self.pd_dict["agent"].append(v["target"])
                    self.pd_dict["text"].append('ATTACK Agent[' + "{0:02d}".format(v["target"]) + ']')
        
        # FINISH
        elif request == 'FINISH' and self.finish_cnt == 0:
            # get full roleMap
            for k in game_info["roleMap"].keys():
                self.pd_dict["day"].append(game_info["day"])
                self.pd_dict["type"].append('finish')
                self.pd_dict["idx"].append(int(k))
                self.pd_dict["turn"].append(0)
                self.pd_dict["agent"].append(int(k))
                self.pd_dict["text"].append('COMINGOUT Agent[' + "{0:02d}".format(int(k)) + '] ' + game_info["roleMap"][k])
            self.finish_cnt += 1
