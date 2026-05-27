# -*- coding: utf-8 -*-
import sys
import urllib.request, urllib.parse, json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QTabWidget, QTextEdit, QMessageBox)

MAPA_UFS = {
    '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA', '16': 'AP', '17': 'TO',
    '21': 'MA', '22': 'PI', '23': 'CE', '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL', 
    '28': 'SE', '29': 'BA', '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP', '41': 'PR', 
    '42': 'SC', '43': 'RS', '50': 'MS', '51': 'MT', '52': 'GO', '53': 'DF'
}

# --- PADRÃO FACADE ---
class APIFacade:
    def call(self, op, **p):
        op_api = op.lower()
        # Mapeia a busca de 'informacoes' para o endpoint 'duplicadas' do servidor backend
        if op_api == 'informacoes':
            op_api = 'duplicadas'
            
        url = f"http://127.0.0.1:5555/{op_api}?{urllib.parse.urlencode(p)}"
        try:
            with urllib.request.urlopen(url) as r: 
                return json.loads(r.read())
        except Exception as e:
            return {"erro": str(e)}

# --- INTERFACE GRÁFICA ---
class BuscadorCidadesGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.facade = APIFacade()
        self.setWindowTitle("Buscador de Cidades")
        self.resize(600, 500)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        self.tab_distancia = QWidget()
        self.tab_informacoes = QWidget() # Alterado de tab_duplicadas para tab_informacoes
        self.tab_proximas = QWidget()

        self.tabs.addTab(self.tab_distancia, "Distância")
        self.tabs.addTab(self.tab_informacoes, "Informações") # Nome da aba alterado
        self.tabs.addTab(self.tab_proximas, "Próximas")

        main_layout.addWidget(self.tabs)

        self.setup_tab_distancia()
        self.setup_tab_informacoes()
        self.setup_tab_proximas()

    def setup_tab_distancia(self):
        layout = QVBoxLayout()
        self.origem_input = QLineEdit()
        self.origem_input.setPlaceholderText("Cidade Origem (ex: Bauru)")
        layout.addWidget(self.origem_input)

        self.destino_input = QLineEdit()
        self.destino_input.setPlaceholderText("Cidade Destino (ex: Campinas)")
        layout.addWidget(self.destino_input)

        btn_calc = QPushButton("Calcular Distância")
        btn_calc.clicked.connect(self.calcular_distancia)
        layout.addWidget(btn_calc)
        
        self.origem_input.returnPressed.connect(self.calcular_distancia)
        self.destino_input.returnPressed.connect(self.calcular_distancia)

        self.result_distancia = QTextEdit()
        self.result_distancia.setReadOnly(True)
        layout.addWidget(self.result_distancia)
        self.tab_distancia.setLayout(layout)

    def calcular_distancia(self):
        a = self.origem_input.text().strip()
        b = self.destino_input.text().strip()
        if not a or not b:
            QMessageBox.warning(self, "Aviso", "Preencha origem e destino.")
            return
        res = self.facade.call('distancia', a=a, b=b)
        if "erro" in res:
            self.result_distancia.setText(f"⚠️ Erro: {res['erro']}")
        else:
            txt = f"📍 Origem: {res.get('origem')}\n📍 Destino: {res.get('destino')}\n🚗 Distância: {res.get('distancia_km')} km"
            self.result_distancia.setText(txt)

    def setup_tab_informacoes(self):
        layout = QVBoxLayout()
        self.alvo_input = QLineEdit()
        self.alvo_input.setPlaceholderText("Nome do município (ex: São Pedro)")
        layout.addWidget(self.alvo_input)

        btn_buscar = QPushButton("Buscar Informações") # Nome do botão alterado
        btn_buscar.clicked.connect(self.buscar_informacoes)
        layout.addWidget(btn_buscar)
        
        self.alvo_input.returnPressed.connect(self.buscar_informacoes)

        self.result_informacoes = QTextEdit()
        self.result_informacoes.setReadOnly(True)
        layout.addWidget(self.result_informacoes)
        self.tab_informacoes.setLayout(layout)

    def buscar_informacoes(self):
        alvo = self.alvo_input.text().strip()
        if not alvo:
            QMessageBox.warning(self, "Aviso", "Preencha o nome do município.")
            return

        res = self.facade.call('informacoes', nome=alvo)
        if "erro" in res:
            self.result_informacoes.setText(f"⚠️ Erro: {res['erro']}")
            return
            
        qtd = res.get('quantidade', 0)
        txt = f"📊 O município '{alvo.title()}' aparece {qtd} vez(es) no Brasil.\n"
        
        if qtd > 0:
            txt += "\n📍 Detalhes da(s) ocorrência(s) encontrada(s):\n"
            for c in res.get('ocorrencias', []):
                cod_uf = str(c.get('codigo_uf', ''))
                sigla = MAPA_UFS.get(cod_uf, f"UF: {cod_uf}")
                
                txt += f"\n🏙️ {c['nome']} - {sigla}\n"
                
                for chave, valor in sorted(c.items()):
                    # Filtra e ignora o 'siafi_id' além dos campos padrões de controle
                    if chave.lower() not in ['nome', 'lat', 'lon', 'latitude', 'longitude', 'siafi_id']:
                        label = chave.replace('_', ' ').capitalize()
                        
                        # Converte 1 para Sim e 0 para Não no campo Capital
                        if chave.lower() == 'capital':
                            valor_formatado = "Sim" if str(valor) == "1" else "Não"
                            txt += f"    ↳ {label}: {valor_formatado}\n"
                        else:
                            txt += f"    ↳ {label}: {valor}\n"
                            
                txt += f"    ↳ Latitude: {c['lat']}\n"
                txt += f"    ↳ Longitude: {c['lon']}\n"
                
        self.result_informacoes.setText(txt)

    def setup_tab_proximas(self):
        layout = QVBoxLayout()
        row_layout = QHBoxLayout()
        self.lat_input = QLineEdit()
        self.lat_input.setPlaceholderText("Latitude (ex: -22.32)")
        self.lon_input = QLineEdit()
        self.lon_input.setPlaceholderText("Longitude (ex: -49.08)")
        self.raio_input = QLineEdit()
        self.raio_input.setPlaceholderText("Raio km (ex: 50)")
        
        row_layout.addWidget(self.lat_input)
        row_layout.addWidget(self.lon_input)
        row_layout.addWidget(self.raio_input)
        layout.addLayout(row_layout)

        btn_proximas = QPushButton("Buscar Próximas")
        btn_proximas.clicked.connect(self.buscar_proximas)
        layout.addWidget(btn_proximas)
        
        self.lat_input.returnPressed.connect(self.buscar_proximas)
        self.lon_input.returnPressed.connect(self.buscar_proximas)
        self.raio_input.returnPressed.connect(self.buscar_proximas)

        self.result_proximas = QTextEdit()
        self.result_proximas.setReadOnly(True)
        layout.addWidget(self.result_proximas)
        self.tab_proximas.setLayout(layout)

    def buscar_proximas(self):
        lat = self.lat_input.text().strip()
        lon = self.lon_input.text().strip()
        raio = self.raio_input.text().strip()

        if not lat or not lon or not raio:
            QMessageBox.warning(self, "Aviso", "Preencha latitude, longitude e raio.")
            return

        res = self.facade.call('proximas', lat=lat, lon=lon, raio=raio)
        if not res:
            self.result_proximas.setText("⚠️ Nenhuma cidade encontrada neste raio.")
        elif isinstance(res, dict) and "erro" in res:
            self.result_proximas.setText(f"⚠️ Erro: {res['erro']}")
        else:
            txt = f"Cidades num raio de {raio} km:\n\n"
            for c in res[:15]: 
                txt += f"🛣️ {c.get('dist')} km | {c.get('nome')}\n"
            self.result_proximas.setText(txt)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BuscadorCidadesGUI()
    window.show()
    sys.exit(app.exec_())
