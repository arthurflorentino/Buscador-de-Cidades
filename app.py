# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import math
import csv

app = Flask(__name__)

# --- CARREGANDO A BASE DE DADOS REAL (INTELIGENTE) ---
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
                # Transforma a linha do CSV em um dicionário guardando TODAS as colunas
                cidade = dict(linha)
                
                # Garante os campos obrigatórios com os nomes padrão para não quebrar a matemática
                cidade["nome"] = linha[chave_nome]
                cidade["lat"] = float(linha[chave_lat])
                cidade["lon"] = float(linha[chave_lon])
                
                CIDADES.append(cidade)
            except:
                pass

    print(f"✅ SUCESSO: {len(CIDADES)} municípios carregados na memória com dados completos!")
except Exception as e:
    print(f"❌ ERRO FATAL AO LER O CSV: {e}")

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
        if c1 and c2: return {"distancia_km": round(haversine(c1[0]['lat'], c1[0]['lon'], c2[0]['lat'], c2[0]['lon']), 2), "origem": c1[0]['nome'], "destino": c2[0]['nome']}
        return {"erro": "Uma ou ambas as cidades não foram encontradas."}

class CoordCmd(CmdBase):
    def execute(self): return self.repo.buscar(self.k.get('nome',''))

class DupCmd(CmdBase):
    def execute(self):
        alvo = self.k.get('nome', '').strip()
        
        # Se o usuário digitou um nome específico, busca as ocorrências dele
        if alvo:
            # Busca exata (ignorando maiúsculas e minúsculas)
            exatas = [c for c in self.repo.todas() if c['nome'].lower() == alvo.lower()]
            return {"alvo": alvo, "quantidade": len(exatas), "ocorrencias": exatas}
            
        # Comportamento antigo (fallback): se não enviar nome, lista todas as repetidas
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

# Rota Dinâmica do Flask
px = Proxy()
@app.route('/<comando>')
def api(comando):
    cmd = Factory.criar(comando, px, **request.args)
    return jsonify(cmd.execute() if hasattr(cmd, 'execute') else {"erro": "Comando inválido"})

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5555)
