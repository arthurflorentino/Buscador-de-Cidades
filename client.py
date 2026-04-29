# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, json

# --- PADRÃO FACADE ---
class APIFacade:
    def call(self, op, **p):
        url = f"http://127.0.0.1:5555/{op}?{urllib.parse.urlencode(p)}"
        try:
            with urllib.request.urlopen(url) as r: return json.loads(r.read())
        except Exception as e:
            return {"erro": str(e)}

# --- INTERFACE (TELA) ---
f = APIFacade()

print("=== BUSCADOR DE CIDADES ===")
print("Comandos disponíveis: distancia | coordenadas | duplicadas | proximas")
op = input("Digite o comando desejado: ").strip().lower()

print("\n--- RESULTADO ---")
if op == 'distancia': 
    print(f.call(op, a=input("Cidade Origem: "), b=input("Cidade Destino: ")))
elif op == 'coordenadas': 
    print(f.call(op, nome=input("Parte do nome da cidade: ")))
elif op == 'duplicadas': 
    print(f.call(op))
elif op == 'proximas': 
    print(f.call(op, lat=input("Latitude: "), lon=input("Longitude: "), raio=input("Raio em km: ")))
else: 
    print("Comando não reconhecido.")
