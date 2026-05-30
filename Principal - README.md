# Projeto: Buscador de Cidades Inteligente

Sistema distribuído composto por um servidor backend (Flask) e dois clientes (CLI e interface gráfica em PyQt5) para processamento de dados geográficos dos municípios brasileiros.

## 👥 Membros da Equipe
**Nome Completo: Arthur Silva Florentino ** - R.A.: 2400220

## 🛠️ Arquitetura e Padrões Utilizados
**Servidor:** Factory Method, Command, Proxy
**Cliente:** Facade, Programação Baseada em Eventos (Signals/Slots com Qt)



## 📂 Estrutura do Projeto

Aqui está a ordem lógica dos arquivos do nosso sistema:

**Servidor (Backend)**
`app.py` - Coração do servidor (Padrões Factory, Command, Proxy).
`municipios.csv` - Base de dados real consumida pelo servidor.
`Servidor - README.md` - Diagrama e arquitetura do servidor.

**Clientes (Frontend)**
`client.py` - Cliente de terminal CLI (Padrão Facade).
`gui_client.py` - Cliente com interface gráfica em PyQt5 (Padrão Facade e Sinais/Slots).
`Cliente - README.md` - Diagrama e arquitetura do cliente.

**Testes Automatizados e Execução**
`teste_integracao.py` - Validação das rotas e regras de negócio do servidor.
`teste_ui.py` - Simulação de cliques e validação da interface gráfica.
`requirements.txt` - Manual passo a passo para instalar e rodar o projeto.
