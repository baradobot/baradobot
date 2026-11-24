import unittest
from orion import Paper
class Tests(unittest.TestCase):
    def test_cycle(self):
        p=Paper(':memory:'); self.assertEqual(p.execute('BTC',1,'BUY',100,'test'),'BUY'); self.assertEqual(p.cash(),9500); self.assertEqual(p.execute('BTC',1,'BUY',100,'test'),'DUPLICATE'); self.assertEqual(p.execute('BTC',2,'BUY',101,'test'),'HOLD'); self.assertEqual(p.execute('BTC',3,'HOLD',97,'test'),'SELL'); self.assertIsNone(p.position('BTC')); self.assertLess(p.cash(),10000)
    def test_no_short(self):
        p=Paper(':memory:'); self.assertEqual(p.execute('ETH',1,'SELL',100,'test'),'HOLD'); self.assertEqual(p.cash(),10000)
if __name__=='__main__': unittest.main()
