
import unittest
import sys
import os

# Fix path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.reorder import ReorderEngine

class TestConversion(unittest.TestCase):
    def setUp(self):
        self.engine = ReorderEngine()

    def test_simple_mapping(self):
        # 'Ka' -> 'd'
        self.assertEqual(self.engine.process("क"), "d")
        # 'Ma' -> 'e'
        self.assertEqual(self.engine.process("म"), "e")

    def test_matra_mapping(self):
        # 'Kaa' -> 'k' + 'a' -> 'dk'
        self.assertEqual(self.engine.process("का"), "dk")
        # 'Ki' (Badi) -> 'k' + 'ii' -> 'dh'
        self.assertEqual(self.engine.process("की"), "dh")

    def test_chhoti_ee_reordering(self):
        # 'Ki' (Chhoti) -> 'Ka' + 'i' -> 'i' + 'Ka' -> 'fd'
        # Unicode: 'क' 'ि'
        self.assertEqual(self.engine.process("कि"), "fd")
        
        # 'Sthiti' variant: 'T' + 'i' -> 'f' + 'T'
        # 'Ti' -> 'fr' (Ta=r)
        self.assertEqual(self.engine.process("ति"), "fr")

    def test_reph_reordering(self):
        # 'Dharm': 'Dha' + 'Ra' + 'Hal' + 'Ma'
        # Expect: 'Dha' + 'Ma' + 'Reph'
        # Dha = '/k', Ma = 'e', Reph = 'Z'
        # /keZ
        self.assertEqual(self.engine.process("धर्म"), "/keZ")
        
        # 'Karm': 'Ka' + 'Ra' + 'Hal' + 'Ma'
        # d + e + Z -> deZ
        self.assertEqual(self.engine.process("कर्म"), "deZ")

    def test_half_chars(self):
        # 'Kya': 'Ka' + 'Hal' + 'Ya' + 'Aa' (Matra)
        # Ka+Hal -> D (Half Ka)
        # Ya -> ;
        # Aa -> k
        # Res: D;k
        self.assertEqual(self.engine.process("क्या"), "D;k")

    def test_complex_word(self):
        # 'Nirman': 'Ni' + 'r' + 'ma' + 'n'
        # Ni -> f + u (u=Na) -> fu
        # r + ma -> ma + Z -> ekZ (Ma + Aa + Reph)
        # n -> u (.k actually for Baan/Retroflex Na)
        # Assuming input is 'निर्माण' (Retroflex N)
        # 'न' 'ि' 'र' '्' 'म' 'ा' 'ण'
        # Ni -> fu
        # r + maa -> ma + aa + Z -> ekZ
        # n (retro) -> .k
        # Res: fuekZ.k
        self.assertEqual(self.engine.process("निर्माण"), "fuekZ.k")

if __name__ == '__main__':
    unittest.main()
