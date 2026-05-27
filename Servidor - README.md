# Arquitetura do Servidor

O servidor utiliza os padrões arquiteturais **Factory**, **Command** e **Proxy** para processar e isolar as regras de negócio de geolocalização de forma modular, limpa e performática.

```mermaid
classDiagram
    class FlaskServer {
        +Rota /<comando>
    }
    class CommandFactory {
        <<Factory>>
        +criar(tipo, repo, params)
    }
    class ICommand {
        <<Interface>>
        +execute()
    }
    class Proxy {
        <<Proxy>>
        +buscar(nome)
        +todas()
    }
    
    FlaskServer --> CommandFactory : solicita comando
    CommandFactory --> ICommand : fabrica
    ICommand --> Proxy : acessa dados
    ICommand <|-- DistanciaCmd
    ICommand <|-- CoordCmd
    ICommand <|-- InfoCmd
    ICommand <|-- ProxCmd
