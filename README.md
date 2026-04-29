🌍 Sistema de Localização de Cidades

Este projeto utiliza uma arquitetura distribuída para gerir dados geográficos e calcular distâncias.


🏗️ Arquitetura do Servidor (Padrões: Factory, Command, Proxy)
O servidor organiza as solicitações através de uma fábrica de comandos e protege os dados com um Proxy.

```mermaid
classDiagram
    class FlaskServer { +Rota /comando }
    class CommandFactory { <<Factory>> +criar() }
    class ICommand { <<Interface>> +execute() }
    class Proxy { <<Proxy>> +buscar() }
    
    FlaskServer --> CommandFactory : solicita
    CommandFactory --> ICommand : instancia
    ICommand --> Proxy : acessa dados
    ICommand <|-- DistanciaCmd
    ICommand <|-- CoordCmd
    ICommand <|-- DupCmd
