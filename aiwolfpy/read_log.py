import csv
import pandas as pd

def read_log(log_path):
    
    with open(log_path, newline='') as csvfile:
        log_reader = csv.reader(csvfile, delimiter=',')
        agent_ = []
        day_ = []
        type_ = []
        idx_ = []
        turn_ = []
        text_ = []

        # for medium result
        medium = 0
        for row in log_reader:
            if row[1] == "status" and int(row[0]) == 0:
                agent_.append(int(row[2])), 
                day_.append(int(row[0])), 
                type_.append('initialize'), 
                idx_.append(int(row[2])), 
                turn_.append(0), 
                text_.append('COMINGOUT Agent[' + "{0:02d}".format(int(row[2])) + '] ' + row[3])
                # medium
                if row[3] == "MEDIUM":
                    medium = row[2]
            elif row[1] == "status":
                pass
            elif row[1] == "talk":
                agent_.append(int(row[4])), 
                day_.append(int(row[0])), 
                type_.append('talk'), 
                idx_.append(int(row[2])), 
                turn_.append(int(row[3])), 
                text_.append(row[5])
            elif row[1] == "whisper":
                agent_.append(int(row[4])), 
                day_.append(int(row[0])), 
                type_.append('whisper'), 
                idx_.append(int(row[2])), 
                turn_.append(int(row[3])), 
                text_.append(row[5])
            elif row[1] == "vote":
                agent_.append(int(row[3])), 
                day_.append(int(row[0])), 
                type_.append('vote'), 
                idx_.append(int(row[2])), 
                turn_.append(0), 
                text_.append('VOTE Agent[' + "{0:02d}".format(int(row[3])) + ']')
            elif row[1] == "attackVote":
                agent_.append(int(row[3])), 
                day_.append(int(row[0])), 
                type_.append('attack_vote'), 
                idx_.append(int(row[2])), 
                turn_.append(0), 
                text_.append('ATTACK Agent[' + "{0:02d}".format(int(row[3])) + ']')
            elif row[1] == "divine":
                agent_.append(int(row[3])), 
                day_.append(int(row[0])), 
                type_.append('divine'), 
                idx_.append(int(row[2])), 
                turn_.append(0), 
                text_.append('DIVINED Agent[' + "{0:02d}".format(int(row[3])) + '] ' + row[4])
            elif row[1] == "execute":
                # for all
                agent_.append(int(row[2])), 
                day_.append(int(row[0])), 
                type_.append('execute'), 
                idx_.append(0), 
                turn_.append(0), 
                text_.append('Over')
                # for medium
                res = 'HUMAN'
                if row[3] == 'WEREWOLF':
                    res = 'WEREWOLF'
                agent_.append(int(row[2])), 
                day_.append(int(row[0])), 
                type_.append('identify'), 
                idx_.append(medium), 
                turn_.append(0), 
                text_.append('IDENTIFIED Agent[' + "{0:02d}".format(int(row[2])) + '] ' + res)
            elif row[1] == "guard":
                agent_.append(int(row[3])), 
                day_.append(int(row[0])), 
                type_.append('guard'), 
                idx_.append(int(row[2])), 
                turn_.append(0), 
                text_.append('GUARDED Agent[' + "{0:02d}".format(int(row[3])) + ']')
            elif row[1] == "attack":
                agent_.append(int(row[2])), 
                day_.append(int(row[0])), 
                type_.append('attack'), 
                idx_.append(0), 
                turn_.append(0), 
                text_.append('ATTACK Agent[' + "{0:02d}".format(int(row[2])) + ']')
                if row[3] == 'true':
                    # dead
                    agent_.append(int(row[2])), 
                    day_.append(int(row[0])), 
                    type_.append('dead'), 
                    idx_.append(0), 
                    turn_.append(0), 
                    text_.append('Over')
            elif row[1] == "result":
                pass
            else:
                pass


    return pd.DataFrame({"day":day_, "type":type_, "idx":idx_, "turn":turn_, "agent":agent_, "text":text_})
    