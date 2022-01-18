from aiwolfpy.protocol.abstractcontent import Content


# children of Content
class SVTRContent(Content):
    """Content class in the form [subject] [verb] [target] [role]
    ESTIMATE and COMINGOUT
    """

    def __init__(self, subject, verb, target, role):
        super().__init__(subject=subject, verb=verb, target=target, role=role)

    def _get_text(self):
        return '%s %s %s' % (str(self.verb), str(self.target), str(self.role))


class SVTContent(Content):
    """Content class in the form [subject] [verb] [target]
    DIVINATION, GUARD, VOTE, ATTACK, GUARDED, VOTED and ATTACKED
    """

    def __init__(self, subject, verb, target):
        super().__init__(subject=subject, verb=verb, target=target)

    def _get_text(self):
        return '%s %s' % (str(self.verb), str(self.target))


class SVTSContent(Content):
    """Content class in the form [subject] [verb] [target] [species]
    DIVINED and IDENTIFIED
    """

    def __init__(self, subject, verb, target, species):
        super().__init__(subject=subject, verb=verb, target=target, species=species)

    def _get_text(self):
        return '%s %s %s' % (str(self.verb), str(self.target), str(self.species))


class AgreeContent(Content):
    """Content class in the form [subject] [verb] [talk_number]
    AGREE and DISAGREE
    """

    def __init__(self, subject, verb, talk_number):
        super().__init__(subject=subject, verb=verb, talk_number=talk_number)

    def _get_text(self):
        return '%s day%s ID:%s' % (str(self.verb), str(self.talk_number[0]), str(self.talk_number[1]))


class ControlContent(Content):
    """Content class for Skip and Over"""

    def __init__(self, subject, verb):
        super().__init__(subject=subject, verb=verb)
        self.is_control = True

    def _get_text(self):
        return self.verb


class SOTSContent(Content):
    """Content class in the form [subject] [operator] [target] [sentence]
    REQUEST and INQUIRE
    """

    def __init__(self, subject, operator, target, content):
        super().__init__(subject=subject, operator=operator, target=target, children=[content])

    def _get_text(self):
        return '%s %s (%s)' % (self.operator, self.target, self.get_child().get_text())

    def get_child(self):
        return self.children[0]


class SOS1Content(Content):
    """Content class in the form [subject] [operator] [sentence]
    NOT
    """

    def __init__(self, subject, operator, content_list):
        super().__init__(subject=subject, operator=operator, children=content_list)

    def _get_text(self):
        return '%s ' % self.operator + " ".join(['(%s)' % c.get_text() for c in self.children])

    def get_child(self):
        return self.children[0]


class SOS2Content(Content):
    """Content class in the form [subject] [operator] [sentence_1] [sentence_2]
    BECAUSE, XOR
    """

    def __init__(self, subject, operator, content_list):
        super().__init__(subject=subject, operator=operator, children=content_list)

    def _get_text(self):
        return '%s ' % self.operator + " ".join(['(%s)' % c.get_text() for c in self.children])

    def get_child_1(self):
        return self.children[0]

    def get_child_2(self):
        return self.children[1]


class SOSSContent(Content):
    """Content class in the form [subject] [operator] [sentence_1] [sentence_2]
    AND, OR
    """

    def __init__(self, subject, operator, content_list):
        super().__init__(subject=subject, operator=operator, children=content_list)

    def _get_text(self):
        return '%s ' % self.operator + " ".join(['(%s)' % c.get_text() for c in self.children])


class DayContent(Content):
    """Content class for day"""

    def __init__(self, subject, operator, day, content):
        super().__init__(subject=subject, day=day, operator=operator, children=[content])

    def _get_text(self):
        return '%s %s (%s)' % (self.operator, str(self.day), self.get_child().get_text())

    def get_child(self):
        return self.children[0]
