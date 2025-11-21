# Protocol

Voor dit prototype heb je de volgende programmeertalen nodig:
 - Python 3.11
 - .NET 9.0
 - ruby 3.3.10

## Hoe start je alles op

### Stap 1
Start de micro-services. Eigenlijk zou je een database eerst moeten opstarten maar die hebben we niet :). 
Onze services die we hebben geimplementeerd

```bash
 python -m protocol.userservice.user_service_server
```

```bash
cd protocol/CardCollection/CardCollection
dotnet run
```

```bash
cd protocol/battleengine
ruby server.rb
```

### Stap 2
Dan start je de gateway

```bash
 python -m protocol.gateway.gateway     
```

### Stap 3
Dan start je de client

```bash
 python -m protocol.client.client
```




