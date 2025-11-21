# JSON Line Protocol — Elixir-implementatie (`JsonLineProtocol`)

Dit document specificeert het gedrag van het JSON-gebaseerde line-protocol zoals geïmplementeerd in `JsonLineProtocol` binnen het Elixir-project.  
Het beschrijft **formaat**, **gedrag**, **edge cases** en **verwachte output** voor de relevante functies.

## 1. Doel van het protocol

Het JSON Line Protocol transporteert berichten over een stream.  
Elke boodschap bestaat uit:

- één JSON-object  
- gevolgd door exact één newline (`"\n"`)

Voorbeelden:

```
{"event":"ping"}\n
{"status":200,"resource":"/"}\n
```

Meerdere berichten kunnen achter elkaar in een buffer staan:

```
{"x":1}\n{"y":2}\nrest
```

## 2. JSON-structuur

### 2.1 Geldige berichten

Een bericht bevat een JSON-object:

```
{
  "hello": "world"
}
```

### 2.2 Ongeldige berichten

Wanneer een bericht geen valide JSON is, wordt het vervangen door een foutstructuur:

```
{
  "status": 400,
  "resource": "/",
  "payload": {
    "error": "INVALID_JSON"
  }
}
```


## 3. Moduleoverzicht

Naam van de module:

```elixir
defmodule JsonLineProtocol do
end
```

Beschikbare functies:

| Functie            | Beschrijving                                                        |
|--------------------|---------------------------------------------------------------------|
| `encode_message/1` | Encodeert een bericht naar JSON + `\n`                             |
| `parse_messages/1` | Strict parser — decode-fouten leiden tot een exception             |
| `read_messages/1`  | Tolerante parser — decode-fouten leveren foutberichten op          |
| `error_message/3`  | Produceert de foutstructuur met `status`, `resource` en `payload`  |

## 4. Gedrag per functie

### 4.1 `encode_message/1`

Voorbeeldinput:

```elixir
JsonLineProtocol.encode_message(%{"hello" => "world"})
```

Voorbeeldoutput:

```
"{\"hello\":\"world\"}\n"
```

### 4.2 `parse_messages/1` (strict)

```elixir
JsonLineProtocol.parse_messages("{\"x\":1}\n{\"y\":2}\nrest")
```

Output:

```elixir
{[%{"x" => 1}, %{"y" => 2}], "rest"}
```

### 4.3 `read_messages/1` (tolerant)

```elixir
JsonLineProtocol.read_messages("{ not json }\n")
```

Output:

```elixir
{
  [
    %{
      "status" => 400,
      "resource" => "/",
      "payload" => %{"error" => "INVALID_JSON"}
    }
  ],
  ""
}
```

## 5. Bufferregels

### 5.1 Complete regels

Eindigen op `"\n"` en worden verwerkt.

### 5.2 Incomplete regels

Alles na de laatste newline wordt teruggegeven als restbuffer.

## 6. Runtime-testen

### Test 1 — `encode_message/1`

```elixir
JsonLineProtocol.encode_message(%{"hello" => "world"})
```

### Test 2 — `parse_messages/1`

```elixir
JsonLineProtocol.parse_messages("{\"x\":1}\n{\"y\":2}\nrest")
```

### Test 3 — `read_messages/1`

```elixir
JsonLineProtocol.read_messages("{ not json }\n")
```

## 7. Edge cases

### Lege regels

Resultaat:

```elixir
{[], ""}
```

### Valide + invalide JSON gemixt

Buffer:

```
{"ok":1}\n{invalid}\n{"done":true}\n
```

## 8. Dependencies

```elixir
defp deps do
  [
    {:jason, "~> 1.4"}
  ]
end
```

Starten:

```
iex.bat -S mix
```

## 9. Samenvatting

`JsonLineProtocol` implementeert een newline-gebaseerd JSON-protocol met een strict pad, tolerant pad, uniforme foutstructuur en consistente bufferlogica.
