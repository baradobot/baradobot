import unittest
from estrategias import señal, tamaño
class EstrategiasTest(unittest.TestCase):
    def test_historial_insuficiente(self):
        self.assertIsNone(señal([], 'ruptura'))
    def test_riesgo(self):
        q=tamaño(10000,100,98,10000)
        self.assertLessEqual(q*2,5)
        self.assertLessEqual(q*100,500)
    def test_sin_efectivo(self):
        self.assertEqual(tamaño(10000,100,98,0),0)
