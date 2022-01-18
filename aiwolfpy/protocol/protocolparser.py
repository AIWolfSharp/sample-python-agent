from aiwolfpy.util.singleton import Singleton
from aiwolfpy.protocol.contentfactory import ContentFactory


# parser
class ProtocolParser(metaclass=Singleton):
    
    @classmethod
    def parse_bracket_one_level(cls, sentence):
        sub_sentence_list = []
        i0 = 0
        level = 0
        for i in range(len(sentence)):
            if sentence[i] == '(':
                level += 1
                if level == 1:
                    i0 = i+1
            elif sentence[i] == ')':
                level -= 1
                if level == 0:
                    sub_sentence_list.append(sentence[i0:i])
        return sub_sentence_list

    @classmethod
    def parse(cls, sentence):
    
        word_list = sentence.split()
    
        # subject
        subject = 'UNSPEC'
        if word_list[0] == 'ANY':
            subject = word_list[0]
            word_list = word_list[1:]
        elif word_list[0][:5] == 'Agent':
            subject = word_list[0]
            assert str(subject)[6:8].isdigit()
            assert str(subject) == 'Agent[%s]' % str(subject)[6:8]
            subject = word_list[0]
            word_list = word_list[1:]
    
        # operator
        if word_list[0] in ['REQUEST', 'INQUIRE', 'BECAUSE', 'DAY', 'NOT', 'AND', 'OR', 'XOR']:
            operator = word_list[0]
            parsed_list = cls.parse_bracket_one_level(sentence)
            if operator == 'REQUEST':
                assert len(parsed_list) == 1
                c = ContentFactory.request(subject, word_list[1], cls.parse(parsed_list[0]))
            elif operator == 'INQUIRE':
                assert len(parsed_list) == 1
                c = ContentFactory.inquire(subject, word_list[1], cls.parse(parsed_list[0]))
            elif operator == 'BECAUSE':
                assert len(parsed_list) == 2
                c = ContentFactory.because(subject, cls.parse(parsed_list[0]), cls.parse(parsed_list[1]))
            elif operator == 'DAY':
                assert len(parsed_list) == 1
                c = ContentFactory.day(subject, word_list[1], cls.parse(parsed_list[0]))
            elif operator == 'NOT':
                assert len(parsed_list) == 1
                c = ContentFactory.not_(subject, cls.parse(parsed_list[0]))
            elif operator == 'AND':
                c = ContentFactory.and_(subject, [cls.parse(t) for t in parsed_list])
            elif operator == 'OR':
                c = ContentFactory.or_(subject, [cls.parse(t) for t in parsed_list])
            else:
                assert operator == 'XOR'
                assert len(parsed_list) == 2
                c = ContentFactory.xor_(subject, cls.parse(parsed_list[0]), cls.parse(parsed_list[1]))
            return c
    
        # verb
        assert word_list[0] in [
            'ESTIMATE', 'COMINGOUT', 'DIVINATION', 'GUARD', 'VOTE',
            'ATTACK', 'DIVINED', 'IDENTIFIED', 'GUARDED', 'VOTED',
            'ATTACKED', 'AGREE', 'DISAGREE', 'Skip', 'Over'
        ]
        verb = word_list[0]
        word_list[0] = subject
    
        if verb == "AGREE":
            c = ContentFactory.agree(word_list[0], (int(word_list[1][3:]), int(word_list[2][3:])))
        elif verb == "DISAGREE":
            c = ContentFactory.disagree(word_list[0], (int(word_list[1][3:]), int(word_list[2][3:])))
        else:
            c = ContentFactory.verb(verb, *word_list)
    
        return c


if __name__ == "__main__":

    con = ProtocolParser.parse("ANY ESTIMATE Agent[01] SEER")
    print(con)
    con = ProtocolParser.parse("Agent[04] AGREE day4 ID:7")
    print(con)
    con = ProtocolParser.parse("Over")
    print(con)
    con = ProtocolParser.parse("VOTE Agent[01]")
    print(con)
    con = ProtocolParser.parse("NOT (VOTE Agent[01])")
    print(con)
    con = ProtocolParser.parse("AND (NOT (VOTE Agent[01])) (VOTE Agent[02])")
    print(con)
