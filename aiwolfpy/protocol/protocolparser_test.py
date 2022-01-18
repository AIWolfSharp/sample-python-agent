import unittest
import aiwolfpy

pr = aiwolfpy.ProtocolParser()


# unit test
class MyTestCase(unittest.TestCase):

    def test_case1(self):
        sentence = 'ESTIMATE Agent[10] BODYGUARD'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case2(self):
        sentence = 'Agent[01] COMINGOUT Agent[03] POSSESSED'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case3(self):
        sentence = 'Agent[12] REQUEST Agent[07] (DIVINATION Agent[09])'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case4(self):
        sentence = 'INQUIRE Agent[29] (GUARD ANY)'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case5(self):
        sentence = 'AND (VOTE Agent[01]) (REQUEST ANY (VOTE Agent[01]))'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case6(self):
        sentence = 'XOR (ATTACK Agent[01]) (ATTACK Agent[07])'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case7(self):
        sentence = 'AND (COMINGOUT Agent[02] SEER) (DIVINED Agent[11] WEREWOLF)'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case8(self):
        sentence = 'BECAUSE (Agent[09] IDENTIFIED Agent[01] HUMAN) (ATTACK Agent[09])'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case9(self):
        sentence = 'OR (Agent[02] GUARDED ANY) (Agent[04] GUARDED ANY) (Agent[14] GUARDED ANY)'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case10(self):
        sentence = 'DAY 1 (VOTED Agent[12])'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case11(self):
        sentence = 'BECAUSE (NOT (ANY ATTACKED Agent[02])) (NOT (ESTIMATE Agent[02] BODYGUARD))'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case12(self):
        sentence = 'AND (ESTIMATE Agent[02] VILLAGER) (AGREE day3 ID:28)'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case13(self):
        sentence = 'ANY XOR (DISAGREE day2 ID:34) (ESTIMATE Agent[03] SEER)'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case14(self):
        sentence = 'Over'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )

    def test_case15(self):
        sentence = 'Skip'
        self.assertEqual(
            sentence,
            pr.parse(sentence).get_text()
        )


if __name__ == '__main__':
    unittest.main()
