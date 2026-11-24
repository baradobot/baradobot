import unittest
from comparador import Comparador
class TestComparador(unittest.TestCase):
    def test_veto(self):
        c=Comparador(); s=dict(stop=98,objetivo=104,estrategia='ruptura')
        self.assertTrue(c.procesar('BTC',1,s,100,{'BTC':100},False,'noticia'))
        self.assertIn('BTC',c.control.posiciones)
        self.assertNotIn('BTC',c.filtrada.posiciones)
        self.assertFalse(c.procesar('BTC',1,s,100,{'BTC':100},True,'duplicado'))
        c.control.actualizar('BTC',dict(open=100,low=97,high=105))
        self.assertLess(c.control.operaciones[0]['resultado'],0)
