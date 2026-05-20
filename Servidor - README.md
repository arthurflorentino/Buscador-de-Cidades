# Arquitetura do Servidor

O servidor utiliza os padrões **Factory**, **Command** e **Proxy**.

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
    }
    
    FlaskServer --> CommandFactory : solicita comando
    CommandFactory --> ICommand : fabrica
    ICommand --> Proxy : acessa dados
    ICommand <|-- DistanciaCmd
    ICommand <|-- CoordCmd
    ICommand <|-- DupCmd
