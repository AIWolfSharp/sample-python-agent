from abc import ABCMeta, abstractmethod


class Content(metaclass=ABCMeta):
    """Abstract content class : ver.3.6(2019)"""

    def __init__(
            self, subject='UNSPEC', target=None, role=None, species=None, verb=None, talk_number=(None, None),
            operator=None, day=None, children=[]
    ):
        # subject
        if str(subject) in ['UNSPEC', 'ANY']:
            self.subject = subject
        elif str(subject).isdigit():
            assert 0 <= int(subject) <= 99
            self.subject = 'Agent[%s]' % "{0:02d}".format(int(subject))
        else:
            assert str(subject)[6:8].isdigit()
            assert str(subject) == 'Agent[%s]' % str(subject)[6:8]
            self.subject = subject

        # target
        if target is None:
            self.target = None
        elif str(target) in ['ANY']:
            self.target = target
        elif str(target).isdigit():
            assert 0 <= int(target) <= 99
            self.target = 'Agent[%s]' % "{0:02d}".format(int(target))
        else:
            assert str(target)[6:8].isdigit()
            assert str(target) == 'Agent[%s]' % str(target)[6:8]
            self.target = target

        # role
        # add FOX and FREEMASON if necessary
        if role is None:
            self.role = None
        else:
            assert str(role) in ['VILLAGER', 'SEER', 'MEDIUM', 'BODYGUARD', 'WEREWOLF', 'POSSESSED', 'ANY']
            self.role = role

        # species
        # add something if necessary
        if species is None:
            self.species = None
        else:
            assert str(species) in ['HUMAN', 'WEREWOLF', 'ANY']
            self.species = species

        # verb
        if verb is None:
            self.verb = None
        else:
            assert str(verb) in [
                'ESTIMATE', 'COMINGOUT', 'DIVINATION', 'GUARD', 'VOTE',
                'ATTACK', 'DIVINED', 'IDENTIFIED', 'GUARDED', 'VOTED',
                'ATTACKED', 'AGREE', 'DISAGREE', 'Skip', 'Over'
            ]
            self.verb = verb

        # TODO : maybe talktype necessary
        # talk number
        assert len(talk_number) == 2
        if talk_number[0] is None:
            self.talk_number = (None, None)
        else:
            assert str(talk_number[0]).isdigit()
            assert str(talk_number[1]).isdigit()
            self.talk_number = talk_number

        # day
        self.day = day

        # operator
        if operator is None:
            self.operator = None
        else:
            assert str(operator) in [
                'REQUEST', 'INQUIRE', 'BECAUSE', 'DAY',
                'NOT', 'AND', 'OR', 'XOR'
            ]
            self.operator = str(operator)
        if operator is None:
            self.is_operator = False
        else:
            self.is_operator = True
        self.is_control = False
        self.children = children

    @abstractmethod
    def _get_text(self):
        return ''

    def get_text(self):
        res = self._get_text()

        if 'Skip' in res:
            assert res == 'Skip'
            return res
        elif 'Over' in res:
            assert res == 'Over'
            return res
        elif str(self.subject) == 'UNSPEC':
            return res
        else:
            return str(self.subject) + ' ' + res

    def __str__(self):
        return self.get_text()

    def get_children(self):
        return self.children
