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
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').lower()

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
                cidade = dict(linha)
                cidade["nome"] = linha[chave_nome]
                cidade["lat"] = float(linha[chave_lat])
                cidade["lon"] = float(linha[chave_lon])
                CIDADES.append(cidade)
            except:
                pass
    print(f"✅ SUCESSO: {len(CIDADES)} municípios carregados!")
except Exception as e:
    print(f"❌ ERRO FATAL AO LER O CSV: {e}")

def haversine(l1, ln1, l2, ln2):
    a = math.sin(math.radians(l2-l1)/2)**2 + math.cos(math.radians(l1))*math.cos(math.radians(l2))*math.sin(math.radians(ln2-ln1)/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- PADRÃO PROXY E REPO ---
class Repo:
    def todas(self): return CIDADES
    def buscar(self, n): 
        n_limpo = remover_acentos(n)
        return [c for c in CIDADES if n_limpo in remover_acentos(c['nome'])]

class Proxy(Repo):
    def buscar(self, n):
        print(f"[LOG PROXY] Interceptando busca no banco por: {n}")
        return super().buscar(n)

# --- PADRÃO COMMAND ---
class CmdBase: 
    def __init__(self, repo, **k): self.repo, self.k = repo, k

class DistanciaCmd(CmdBase):
    def execute(self):
        a_limpo = remover_acentos(self.k.get('a',''))
        b_limpo = remover_acentos(self.k.get('b',''))
        
        c1 = [c for c in self.repo.todas() if remover_acentos(c['nome']) == a_limpo]
        c2 = [c for c in self.repo.todas() if remover_acentos(c['nome']) == b_limpo]
        
        if c1 and c2: 
            return {"distancia_km": round(haversine(c1[0]['lat'], c1[0]['lon'], c2[0]['lat'], c2[0]['lon']), 2), "origem": c1[0]['nome'], "destino": c2[0]['nome']}
        return {"erro": "Uma ou ambas as cidades não foram encontradas."}

class CoordCmd(CmdBase):
    def execute(self): return self.repo.buscar(self.k.get('nome',''))

class DupCmd(CmdBase):
    def execute(self):
        alvo = self.k.get('nome', '').strip()
        if alvo:
            alvo_limpo = remover_acentos(alvo)
            exatas = [c for c in self.repo.todas() if alvo_limpo in remover_acentos(c['nome'])]
            return {"alvo": alvo, "quantidade": len(exatas), "ocorrencias": exatas}
            
        n = [c['nome'] for c in self.repo.todas()]
        duplicadas = list(set([x for x in n if n.count(x)>1]))
        return {"total_municipios": len(n), "qtd_duplicados": len(duplicadas), "nomes_duplicados": duplicadas}

class ProxCmd(CmdBase):
    def execute(self):
        r = float(self.k.get('raio', 50))
        res = [{**c, "dist": round(haversine(float(self.k.get('lat',0)), float(self.k.get('lon',0)), c['lat'], c['lon']),2)} for c in self.repo.todas()]
        return sorted([c for c in res if c['dist'] <= r], key=lambda x: x['dist'])

# --- PADRÃO FACTORY ---
class Factory:
    @staticmethod
    def criar(tipo, repo, **k):
        mapa = {'distancia': DistanciaCmd, 'coordenadas': CoordCmd, 'duplicadas': DupCmd, 'proximas': ProxCmd}
        return mapa.get(tipo, CmdBase)(repo, **k)

# --- ROTAS FLASK ---
px = Proxy()
@app.route('/<comando>')
def api(comando):
    cmd = Factory.criar(comando, px, **request.args)
    return jsonify(cmd.execute() if hasattr(cmd, 'execute') else {"erro": "Comando inválido"})

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5555)
