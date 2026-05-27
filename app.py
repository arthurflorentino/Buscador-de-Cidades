# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import math
import csv
import unicodedata

app = Flask(__name__)

# --- FUNÇÃO AUXILIAR PARA REMOVER ACENTOS ---
def remover_acentos(texto):
    if not texto:
        return ""
    # Remove os acentos e converte tudo para minúsculas
    texto_limpo = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto_limpo.lower()

# --- CARREGANDO A BASE DE DADOS REAL ---
CIDADES = []
try:
    with open('municipios.csv', mode='r', encoding='utf-8-sig') as f:
        primeira_linha = f.readline()
        separador = ';' if ';' in primeira_linha else ','
        f.seek(0)
        
        leitor = csv.DictReader(f, delimiter=separador)
        chaves = leitor.fieldnames
        
        chave_nome, chave_lat, chave_lon = "nome", "lat", "lon"
        
        for c in chaves:
            c_lower = c.lower()
            if 'nome' in c_lower or 'munic' in c_lower: chave_nome = c
            if 'lat' in c_lower: chave_lat = c
            if 'lon' in c_lower or 'lng' in c_lower: chave_lon = c

        for linha in leitor:
            try:
                # Transforma a linha do CSV num dicionário guardando TODAS as colunas
                cidade = dict(linha)
                
                # Garante os campos obrigatórios com os nomes padrão para não quebrar a matemática
                cidade["nome"] = linha[chave_nome]
                cidade["lat"] = float(linha[chave_lat])
                cidade["lon"] = float(linha[chave_lon])
                
                CIDADES.append(cidade)
            except:
                pass
except Exception as e:
    print(f"Erro ao carregar o CSV: {e}")

# --- FUNÇÃO MATEMÁTICA (HAVERSINE) ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Raio da Terra em km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- PADRÃO COMMAND ---
class CmdBase:
    def __init__(self, repo, **k):
        self.repo = repo
        self.k = k
    def execute(self): pass

class DistanciaCmd(CmdBase):
    def execute(self):
        nome_a = remover_acentos(self.k.get('a', ''))
        nome_b = remover_acentos(self.k.get('b', ''))
        
        # Busca exata, mas ignorando acentos e maiúsculas/minúsculas
        cidade_a = next((c for c in self.repo.todas() if remover_acentos(c['nome']) == nome_a), None)
        cidade_b = next((c for c in self.repo.todas() if remover_acentos(c['nome']) == nome_b), None)
        
        if not cidade_a or not cidade_b:
            return {"erro": "Uma ou ambas as cidades não foram encontradas."}
            
        d = haversine(cidade_a['lat'], cidade_a['lon'], cidade_b['lat'], cidade_b['lon'])
        return {"origem": cidade_a['nome'], "destino": cidade_b['nome'], "distancia_km": round(d, 2)}

class CoordCmd(CmdBase):
    def execute(self):
        nome = remover_acentos(self.k.get('nome', ''))
        return [c for c in self.repo.todas() if remover_acentos(c['nome']) == nome]

class DupCmd(CmdBase):
    def execute(self):
        alvo = self.k.get('nome', '')
        # Se o utilizador enviou um nome específico, faz a busca
        if alvo:
            alvo_limpo = remover_acentos(alvo)
            # Busca parcial (usa 'in') e ignora acentos/maiúsculas
            exatas = [c for c in self.repo.todas() if alvo_limpo in remover_acentos(c['nome'])]
            return {"alvo": alvo, "quantidade": len(exatas), "ocorrencias": exatas}
            
        # Comportamento fallback (se não enviar nome, lista todas as repetidas)
        n = [c['nome'] for c in self.repo.todas()]
        duplicadas = list(set([x for x in n if n.count(x)>1]))
        return {"total_municipios": len(n), "qtd_duplicados": len(duplicadas), "nomes_duplicados": duplicadas}

class ProxCmd(CmdBase):
    def execute(self):
        try:
            r = float(self.k.get('raio', 50))
            lat = float(self.k.get('lat', 0))
            lon = float(self.k.get('lon', 0))
        except ValueError:
            return {"erro": "Coordenadas ou raio inválidos."}
            
        res = [{**c, "dist": round(haversine(lat, lon, c['lat'], c['lon']), 2)} for c in self.repo.todas()]
        return sorted([c for c in res if c['dist'] <= r], key=lambda x: x['dist'])

# --- PADRÃO FACTORY ---
class Factory:
    @staticmethod
    def criar(tipo, repo, **k):
        mapa = {'distancia': DistanciaCmd, 'coordenadas': CoordCmd, 'duplicadas': DupCmd, 'proximas': ProxCmd}
        classe = mapa.get(tipo)
        if classe:
            return classe(repo, **k)
        return None

# --- PADRÃO PROXY ---
class CidadesProxy:
    def todas(self):
        # O Proxy intercepta a chamada, regista no terminal e repassa a lista original
        buscas = []
        if request.args.get('nome'): buscas.append(request.args.get('nome'))
        if request.args.get('a'): buscas.append(request.args.get('a'))
        if request.args.get('b'): buscas.append(request.args.get('b'))
        
        for b in buscas:
            print(f"[LOG PROXY] Intercetando busca na base de dados por: {b}")
            
        return CIDADES

# --- ROTAS DA API ---
@app.route('/<comando>', methods=['GET'])
def api(comando):
    # A Factory fabrica o comando certo e o Proxy é injetado como repositório
    cmd = Factory.criar(comando, CidadesProxy(), **request.args)
    if not cmd:
        return jsonify({"erro": "Comando inválido."}), 400
    return jsonify(cmd.execute())

if __name__ == '__main__':
    print(f"✅ SUCESSO: {len(CIDADES)} municípios carregados na memória com dados completos!")
    app.run(host='0.0.0.0', port=5555, debug=False)
