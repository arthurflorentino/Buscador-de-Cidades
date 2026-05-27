# Arquitetura do Cliente

O cliente utiliza o padrão **Facade** para ocultar a complexidade das requisições HTTP, centralizar o mapeamento de endpoints e simplificar a comunicação das interfaces de usuário com a API do servidor. 

Uma grande vantagem dessa arquitetura é a reutilização: tanto a interface de linha de comando (CLI) quanto a interface gráfica (GUI) consomem exatamente a mesma fachada de serviços.

```mermaid
classDiagram
    class TerminalUI {
        +Menu interativo CLI
        +capturar_entrada()
    }
    class BuscadorCidadesGUI {
        +Interface Gráfica PyQt5
        +Abas e Campos de Texto
        +Sinais e Slots (Eventos)
    }
    class APIFacade {
        <<Facade>>
        +call(op, **p)
    }
    
    TerminalUI --> APIFacade : solicita dados simplificados
    BuscadorCidadesGUI --> APIFacade : solicita dados simplificados
