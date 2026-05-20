# Arquitetura do Cliente

O cliente utiliza o padrão **Facade** para ocultar a complexidade das requisições HTTP e simplificar a comunicação da interface de linha de comando (CLI) com a API do servidor.

```mermaid
classDiagram
    class TerminalUI {
        +exibir_menu()
        +capturar_entrada()
    }
    class APIFacade {
        <<Facade>>
        +call(endpoint, params)
    }
    
    TerminalUI --> APIFacade : solicita dados simplificados
