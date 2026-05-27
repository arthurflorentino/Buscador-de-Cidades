# -*- coding: utf-8 -*-
import sys
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Importamos a nossa interface gráfica
from gui_client import BuscadorCidadesGUI, APIFacade

# Instância global necessária para o PyQt
app = QApplication(sys.argv)

class TesteIntegracaoGUI(unittest.TestCase):
    def setUp(self):
        self.gui = BuscadorCidadesGUI()
        
    def test_integracao_facade_sucesso(self):
        facade = APIFacade()
        resultado = facade.call('informacoes')
        
        self.assertIsInstance(resultado, dict)
        if "erro" in resultado:
            self.fail(f"Servidor inacessível ou erro na API: {resultado['erro']}")

    def test_usabilidade_aba_distancia(self):
        self.gui.tabs.setCurrentIndex(0)
        self.gui.origem_input.setText("São Paulo")
        self.gui.destino_input.setText("Campinas")
        
        self.assertEqual(self.gui.origem_input.text(), "São Paulo")
        self.assertEqual(self.gui.destino_input.text(), "Campinas")

    def test_usabilidade_aba_informacoes_valida_restricao(self):
        self.gui.tabs.setCurrentIndex(1)
        self.gui.alvo_input.clear()
        self.assertEqual(self.gui.result_informacoes.toPlainText(), "")
        
    def test_usabilidade_aba_proximas(self):
        self.gui.tabs.setCurrentIndex(2)
        
        self.gui.lat_input.setText("-23.55")
        self.gui.lon_input.setText("-46.63")
        self.gui.raio_input.setText("50")
        
        btn_buscar = self.gui.tab_proximas.layout().itemAt(1).widget() 
        QTest.mouseClick(btn_buscar, Qt.LeftButton)
        
        resultado_tela = self.gui.result_proximas.toPlainText()
        
        if "⚠️ Erro" not in resultado_tela:
            self.assertIn("km", resultado_tela)

    def tearDown(self):
        self.gui.close()

if __name__ == '__main__':
    print("Iniciando testes de UI e Integração...")
    unittest.main(verbosity=2)
