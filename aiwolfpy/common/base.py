from aiwolfpy.util.singleton import Singleton


class Species(metaclass=Singleton):

    HUMAN = 'HUMAN'
    WEREWOLF = 'WEREWOLF'
    ANY = 'ANY'

    # Alias
    human = HUMAN
    werewolf = WEREWOLF
    any = ANY


class Role(metaclass=Singleton):

    VILLAGER = 'VILLAGER'
    SEER = 'SEER'
    MEDIUM = 'MEDIUM'
    BODYGUARD = 'BODYGUARD'
    WEREWOLF = 'WEREWOLF'
    POSSESSED = 'POSSESSED'
    ANY = 'ANY'

    # Alias
    villager = VILLAGER
    seer = SEER
    medium = MEDIUM
    bodyguard = BODYGUARD
    werewolf = WEREWOLF
    possessed = POSSESSED
    any = ANY


def agent(i: int):
    assert 0 <= i <= 99
    return 'Agent[%s]' % "{0:02d}".format(i)


# test
if __name__ == "__main__":

    assert Species.human == "HUMAN"
    assert Species.WEREWOLF == "WEREWOLF"
    assert Species.ANY == "ANY"
    sp = Species()
    assert sp.HUMAN == "HUMAN"
    assert sp.werewolf == "WEREWOLF"
    assert sp.any == "ANY"

    assert Role.villager == "VILLAGER"
    assert Role.SEER == "SEER"
    assert Role.medium == "MEDIUM"
    assert Role.ANY == "ANY"
    rl = Role()
    assert rl.BODYGUARD == "BODYGUARD"
    assert rl.werewolf == "WEREWOLF"
    assert rl.POSSESSED == "POSSESSED"
    assert rl.any == "ANY"

    assert agent(0) == "Agent[00]"
    assert agent(1) == "Agent[01]"
    assert agent(71) == "Agent[71]"

    print("OK")
