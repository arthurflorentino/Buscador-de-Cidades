# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import math

app = Flask(__name__)

# Base de dados mockada (em memória)
CIDADES = [
    {"nome": "São Caetano", "lat": -23.62, "lon": -46.55},
    {"nome": "Salvador", "lat": -12.97, "lon": -38.50},
    {"nome": "Bom Jesus", "lat": -9.07, "lon": -44.35},
    {"nome": "Bom Jesus", "lat": -5.98, "lon": -35.58} # Duplicada para testar a busca
]

# Fórmula matemática pura para distância
def haversine(l1, ln1, l2, ln2):
    a = math.sin(math.radians(l2-l1)/2)**2 + math.cos(math.radians(l1))*math.cos(math.radians(l2))*math.sin(math.radians(ln2-ln1)/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- PADRÃO PROXY ---
class Repo:
    def todas(self): return CIDADES
    def buscar(self, n): return [c for c in CIDADES if n.lower() in c['nome'].lower()]

class Proxy(Repo):
    def buscar(self, n):
        print(f"[LOG PROXY] Interceptando busca no banco por: {n}")
        return super().buscar(n)

# --- PADRÃO COMMAND ---
class CmdBase: 
    def __init__(self, repo, **k): self.repo, self.k = repo, k

class DistanciaCmd(CmdBase):
    def execute(self):
        c1, c2 = self.repo.buscar(self.k.get('a','')), self.repo.buscar(self.k.get('b',''))
        if c1 and c2: return {"dist_km": round(haversine(c1[0]['lat'], c1[0]['lon'], c2[0]['lat'], c2[0]['lon']), 2)}
        return {"erro": "Cidades não encontradas"}

class CoordCmd(CmdBase):
    def execute(self): return self.repo.buscar(self.k.get('nome',''))

class DupCmd(CmdBase):
    def execute(self):
        n = [c['nome'] for c in self.repo.todas()]
        return {"duplicadas": list(set([x for x in n if n.count(x)>1]))}

class ProxCmd(CmdBase):
    def execute(self):
        r = float(self.k.get('raio', 50))
        res = [{**c, "dist": round(haversine(float(self.k.get('lat',0)), float(self.k.get('lon',0)), c['lat'], c['lon']),2)} for c in self.repo.todas()]
        return sorted([c for c in res if c['dist'] <= r], key=lambda x: x['dist'])

# --- PADRÃO FACTORY ---
class Factory:
    @staticmethod
    def criar(tipo, repo, **k):
        # O Dicionário decide qual Comando usar baseado na URL
        mapa = {'distancia': DistanciaCmd, 'coordenadas': CoordCmd, 'duplicadas': DupCmd, 'proximas': ProxCmd}
        return mapa.get(tipo, CmdBase)(repo, **k)

# Rota Dinâmica do Flask
px = Proxy()
@app.route('/<comando>')
def api(comando):
    cmd = Factory.criar(comando, px, **request.args)
    return jsonify(cmd.execute() if hasattr(cmd, 'execute') else {"erro": "Comando inválido"})

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5555)
