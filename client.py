# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, json

# --- PADRÃO FACADE ---
class APIFacade:
    def call(self, op, **p):
        op_api = op.lower()
        # Se o usuário escolher 'informacoes', mapeia internamente para a rota 'duplicadas' do servidor
        if op_api == 'informacoes':
            op_api = 'duplicadas'
            
        url = f"http://127.0.0.1:5555/{op_api}?{urllib.parse.urlencode(p)}"
        try:
            with urllib.request.urlopen(url) as r: 
                return json.loads(r.read())
        except Exception as e:
            return {"erro": str(e)}

# --- INTERFACE (TELA DE TEXTO) ---
f = APIFacade()

while True:
    print("\n" + "="*50)
    print("               BUSCADOR DE CIDADES               ")
    print("="*50)
    print("Comandos disponíveis:")
    print("▶ Distancia | Informacoes | Proximas | Sair")
    
    op = input("\nDigite o comando desejado: ").strip().lower()

    if op == 'sair':
        print("\nEncerrando o sistema. Até logo! 👋\n")
        break

    print("\n" + "-"*18 + " RESULTADO " + "-"*18)

    if op == 'distancia': 
        a = input("Cidade Origem (ex: Bauru): ")
        b = input("Cidade Destino (ex: Campinas): ")
        res = f.call(op, a=a, b=b)
        
        if "erro" in res:
            print(f"\n⚠️ Ops! {res['erro']}")
        else:
            print(f"\n📍 Origem: {res.get('origem')}")
            print(f"📍 Destino: {res.get('destino')}")
            print(f"🚗 Distância: {res.get('distancia_km')} km")

    elif op == 'informacoes': 
        alvo = input("Digite o nome do município (ex: São Pedro): ")
        print("⏳ Consultando a base de dados, aguarde...\n")
        res = f.call(op, nome=alvo)
        
        if "erro" in res:
            print(f"⚠️ Erro: {res['erro']}")
        else:
            qtd = res.get('quantidade', 0)
            print(f"📊 O município '{alvo.title()}' aparece {qtd} vez(es) no Brasil.")
            
            if qtd > 0:
                print("\n📍 Detalhes da(s) ocorrência(s) encontrada(s):")
                for c in res.get('ocorrencias', []):
                    print(f"\n   🏙️  {c['nome']}")
                    for chave, valor in sorted(c.items()):
                        # Remove 'siafi_id' e os outros campos que não devem listar diretamente
                        if chave.lower() not in ['nome', 'lat', 'lon', 'latitude', 'longitude', 'siafi_id'] and valor:
                            label = chave.replace('_', ' ').capitalize()
                            
                            # Tratamento especial para o campo Capital (Sim/Não)
                            if chave.lower() == 'capital':
                                valor_formatado = "Sim" if str(valor) == "1" else "Não"
                                print(f"       ↳ {label}: {valor_formatado}")
                            else:
                                print(f"       ↳ {label}: {valor}")
                                
                    print(f"       ↳ Latitude: {c['lat']}")
                    print(f"       ↳ Longitude: {c['lon']}")

    elif op == 'proximas': 
        lat = input("Latitude (ex: -22.32): ")
        lon = input("Longitude (ex: -49.08): ")
        raio = input("Raio em km (ex: 50): ")
        res = f.call(op, lat=lat, lon=lon, raio=raio)
        
        if not res:
            print("\n⚠️ Nenhuma cidade encontrada neste raio.")
        elif isinstance(res, dict) and "erro" in res:
            print(f"Erro: {res['erro']}")
        else:
            print(f"\nCidades num raio de {raio} km:")
            for c in res[:15]: 
                print(f"    objectivity  {c.get('dist')} km | {c.get('nome')}")
    else:
        print("\n⚠️ Comando inválido! Tente novamente.")
