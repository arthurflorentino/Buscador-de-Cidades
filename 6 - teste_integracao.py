# -*- coding: utf-8 -*-
import unittest
import json
# Importamos o app e a lista de CIDADES do seu servidor
from app import app, CIDADES

class TestIntegracaoServidor(unittest.TestCase):
    def setUp(self):
        # Configura o cliente de teste do Flask
        self.app = app.test_client()
        self.app.testing = True
         
        # Injetamos dados controlados na memória para o teste ser previsível
        # Isso garante que o teste passe mesmo se o arquivo .csv não estiver presente
        CIDADES.clear()
        CIDADES.extend([
            {"nome": "Bauru", "lat": -22.3145, "lon": -49.0587},
            {"nome": "São Paulo", "lat": -23.5505, "lon": -46.6333},
            {"nome": "Bauru", "lat": -22.0, "lon": -49.0} # Duplicada proposital para o teste
        ])

    def test_rota_coordenadas(self):
        """Testa se a busca por coordenadas retorna a cidade correta"""
        resposta = self.app.get('/coordenadas?nome=São Paulo')
        dados = json.loads(resposta.data)
        
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(dados), 1)
        self.assertEqual(dados[0]['nome'], 'São Paulo')
        self.assertEqual(dados[0]['lat'], -23.5505)

    def test_rota_distancia(self):
        """Testa o cálculo de distância entre duas cidades"""
        resposta = self.app.get('/distancia?a=Bauru&b=São Paulo')
        dados = json.loads(resposta.data)
        
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('distancia_km', dados)
        self.assertEqual(dados['origem'], 'Bauru')
        self.assertEqual(dados['destino'], 'São Paulo')
        self.assertTrue(dados['distancia_km'] > 0) # A distância deve ser maior que zero

    def test_rota_duplicadas(self):
        """Testa se a rota identifica cidades com o mesmo nome"""
        resposta = self.app.get('/duplicadas')
        dados = json.loads(resposta.data)
        
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('Bauru', dados['nomes_duplicados'])
        self.assertEqual(dados['qtd_duplicados'], 1)

    def test_rota_proximas(self):
        """Testa a busca de cidades por raio de proximidade"""
        # Busca em um raio de 50km da coordenada exata de São Paulo
        resposta = self.app.get('/proximas?lat=-23.55&lon=-46.63&raio=50')
        dados = json.loads(resposta.data)
        
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(len(dados) > 0)
        self.assertEqual(dados[0]['nome'], 'São Paulo')

    def test_comando_invalido(self):
        """Testa o comportamento do Factory ao receber uma rota que não existe"""
        resposta = self.app.get('/rota_maluca_que_nao_existe')
        dados = json.loads(resposta.data)
        
        # O Flask retorna 200 porque a sua rota captura /<comando> dinamicamente,
        # mas o JSON retornado deve conter a chave de erro.
        self.assertEqual(resposta.status_code, 200) 
        self.assertIn('erro', dados)
        self.assertEqual(dados['erro'], 'Comando inválido')

if __name__ == '__main__':
    unittest.main(verbosity=2)
