# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, json

# Dicionário para converter código numérico do IBGE na sigla do Estado
MAPA_UFS = {
    '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA', '16': 'AP', '17': 'TO', '21': 'MA',
    '22': 'PI', '23': 'CE', '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL', '28': 'SE', '29': 'BA',
    '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP', '41': 'PR', '42': 'SC', '43': 'RS', '50': 'MS',
    '51': 'MT', '52': 'GO', '53': 'DF'
}

# --- PADRÃO FACADE ---
class APIFacade:
    def call(self, op, **p):
        op_api = op.lower()
        url = f"http://127.0.0.1:5555/{op_api}?{urllib.parse.urlencode(p)}"
        try:
            with urllib.request.urlopen(url) as r: 
                return json.loads(r.read())
        except Exception as e:
            return {"erro": str(e)}

# --- INTERFACE (TELA CLI) ---
f = APIFacade()

while True:
    print("\n" + "="*50)
    print("               BUSCADOR DE CIDADES               ")
    print("="*50)
    print("Comandos disponíveis:")
    print("▶ Distancia | Duplicadas | Proximas | Sair")
    
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

    elif op == 'duplicadas':
        alvo = input("Digite o nome do município (ex: São Pedro): ").strip()
        print("⏳ Consultando a base de dados, aguarde...\n")
        res = f.call(op, nome=alvo)
        
        if "erro" in res:
            print(f"Erro: {res['erro']}")
        else:
            qtd = res.get('quantidade', 0)
            print(f"📊 O município '{alvo.title()}' aparece {qtd} vez(es) no Brasil.")
            
            if qtd > 0:
                print("\n📍 Detalhes da(s) ocorrência(s) encontrada(s):")
                for c in res.get('ocorrencias', []):
                    # Traduz o código numérico para a sigla do estado
                    cod_uf = str(c.get('codigo_uf', ''))
                    sigla = MAPA_UFS.get(cod_uf, f"UF: {cod_uf}")
                    
                    # Exibe no formato solicitado: Nome - SIGLA
                    print(f"\n   🏙️  {c['nome']} - {sigla}")
                    
                    # Exibe de forma limpa e estruturada as demais informações adicionais recebidas
                    for chave, valor in sorted(c.items()):
                        if chave.lower() not in ['nome', 'lat', 'lon', 'latitude', 'longitude']:
                            label = chave.replace('_', ' ').capitalize()
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
                print(f"   🛣️  {c.get('dist')} km | {c.get('nome')}")
    else:
        print("\n⚠️ Comando inválido! Tente novamente.")
