import unittest
import aiwolfpy
from aiwolfpy import agent as ag


cf = aiwolfpy.ContentFactory()
rl = aiwolfpy.Role()
sp = aiwolfpy.Species()


# unit test
class MyTestCase(unittest.TestCase):

    def test_case1(self):
        self.assertEqual(
            'ESTIMATE Agent[10] BODYGUARD',
            cf.estimate(ag(10), rl.bodyguard).get_text()
        )

    def test_case2(self):
        self.assertEqual(
            'Agent[01] COMINGOUT Agent[03] POSSESSED',
            cf.comingout(1, 3, 'POSSESSED').get_text()
        )

    def test_case3(self):
        self.assertEqual(
            'Agent[12] REQUEST Agent[07] (DIVINATION Agent[09])',
            cf.request('12', '07', cf.divination('09')).get_text()
        )

    def test_case4(self):
        self.assertEqual(
            'INQUIRE Agent[29] (GUARD ANY)',
            cf.inquire(ag(29), cf.guard('ANY')).get_text()
        )

    def test_case5(self):
        self.assertEqual(
            'AND (VOTE Agent[01]) (REQUEST ANY (VOTE Agent[01]))',
            cf.and_([cf.vote(1), cf.request('ANY', cf.vote(1))]).get_text()
        )

    def test_case6(self):
        self.assertEqual(
            'XOR (ATTACK Agent[01]) (ATTACK Agent[07])',
            cf.xor_(cf.attack('1'), cf.attack('7')).get_text()
        )

    def test_case7(self):
        self.assertEqual(
            'AND (COMINGOUT Agent[02] SEER) (DIVINED Agent[11] WEREWOLF)',
            cf.and_([cf.comingout(ag(2), rl.SEER), cf.divined(ag(11), sp.WEREWOLF)]).get_text()
        )

    def test_case8(self):
        self.assertEqual(
            'BECAUSE (Agent[09] IDENTIFIED Agent[01] HUMAN) (ATTACK Agent[09])',
            cf.because(cf.identified(9, 1, 'HUMAN'), cf.attack('Agent[09]')).get_text()
        )

    def test_case9(self):
        self.assertEqual(
            'OR (Agent[02] GUARDED ANY) (Agent[04] GUARDED ANY) (Agent[14] GUARDED ANY)',
            cf.or_([cf.guarded(2, 'ANY'), cf.guarded(4, 'ANY'), cf.guarded(14, 'ANY')]).get_text()
        )

    def test_case10(self):
        self.assertEqual(
            'DAY 1 (VOTED Agent[12])',
            cf.day(1, cf.voted(ag(12))).get_text()
        )

    def test_case11(self):
        self.assertEqual(
            'BECAUSE (NOT (ANY ATTACKED Agent[02])) (NOT (ESTIMATE Agent[02] BODYGUARD))',
            cf.because(cf.not_(cf.attacked('ANY', 'Agent[02]')), cf.not_(cf.estimate(2, rl.BODYGUARD))).get_text()
        )

    def test_case12(self):
        self.assertEqual(
            'AND (ESTIMATE Agent[02] VILLAGER) (AGREE day3 ID:28)',
            cf.and_([cf.estimate('2', 'VILLAGER'), cf.agree((3, 28))]).get_text()
        )

    def test_case13(self):
        self.assertEqual(
            'ANY XOR (DISAGREE day2 ID:34) (ESTIMATE Agent[03] SEER)',
            cf.xor_('ANY', cf.disagree(('2', '34')), cf.estimate(3, rl.seer)).get_text()
        )

    def test_case14(self):
        self.assertEqual(
            'Over',
            cf.over().get_text()
        )

    def test_case15(self):
        self.assertEqual(
            'Skip',
            cf.skip(23).get_text()
        )


if __name__ == '__main__':
    unittest.main()
