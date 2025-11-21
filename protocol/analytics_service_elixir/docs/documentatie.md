# Analytics Service (Elixir) — Documentatie

Deze documentatie beschrijft het JSON Line Protocol, de Analytics TCP-server, de service-laag, testen (incl. AAA-stijl), en wat er nog ontbreekt om deze service formeel af te ronden. 

Het doel is om een server te realiseren die overeenkomt met de bestaande microservices in Ruby, Python en C#, maar specifiek gericht is op de Analytics-domeinlogica zoals gedefinieerd in het [klassendiagram](https://confluenceasd.aimsites.nl/download/attachments/500346264/image-2025-11-14_15-47-7.png?version=1&modificationDate=1763131626650&api=v2) in [Confluence](https://confluenceasd.aimsites.nl/x/mK3SHQ).

## 1. Doel van de Analytics-service

De Analytics-service verwerkt verzoeken voor: 
- Het ophalen van leaderboardgegevens.
- Het berekenen van de top 20 spelers.
- Het ophalen van statistieken van een speler.
- Het ophalen van game-resultaten (en laatste 20 games).

De server gebruikt newline-gebaseerde JSON-berichten en verwerkt deze via het protocol `JsonLineProtocol`.

## 2. Transportprotocol: JSON Line Protocol

De volledige specificatie van dit protocol staat hieronder samengevat.

### 2.1. Formaat van berichten

Een bericht bestaat uit: 
- Eén JSON-object
- Gevolgd door een newline `\n`

Voorbeeld:
```
{"id":"1","action":"leaderboard","payload":{}}\n
```

### 2.2. Bufferregels

Buffers kunnen meerdere berichten bevatten:
```
{"x":1}\n{"y":2}\nrest
```

### 2.3. Parsers

| Functie            | Gedrag                           |
| ------------------ | -------------------------------- |
| `encode_message/1` | JSON → string + newline          |
| `parse_messages/1` | Strict, errors → exception       |
| `read_messages/1`  | Tolerant, errors → error-payload |

### 2.4. Errorstructuur

```
{
  "status": 400,
  "resource": "/",
  "payload": { "error": "INVALID_JSON" }
}
```

## 3. AnalyticsServer — TCP-server

De server luistert op een TCP-poort en verwerkt inkomende JSON-berichten.

### 3.1. Taken van de server

1. TCP-verbinding accepteren
2. Buffer opbouwen
3. Berichten parsen via `JsonLineProtocol`
4. `action` uitlezen
5. Doorsturen naar de juiste functie in `AnalyticsService`
6. Response terugsturen met exact dezelfde `id`

### 3.2. Routes

De server ondersteunt:
| Action               | Functie                                    |
| -------------------- | ------------------------------------------ |
| `leaderboard`        | `AnalyticsService.leaderboard/2`           |
| `leaderboard_top20`  | `AnalyticsService.leaderboard_top20/2`     |
| `stats_for_player`   | `AnalyticsService.player_stats/2`          |
| `stats_getStats`     | `AnalyticsService.player_stats_detailed/2` |
| `results_for_player` | `AnalyticsService.player_results/2`        |
| `results_last20`     | `AnalyticsService.player_last20_results/2` |

## 4. AnalyticsService — businesslogica

De service biedt functies die dummy-data retourneren (placeholder voor echte logica):
- `leaderboard/2` → lijst `LeaderboardEntry`
- `leaderboard_top20/2` → top 20 spelers
- `player_stats/2` → basisstatistieken (`PlayerStats`)
- `player_stats_detailed/2` → meer detail (zelfde als `player_stats/2`)
- `player_results/2` → lijst van `GameResult`
- `player_last20_results/2` → laatste 20 resultaten

> Opmerking:

Er ontbreken formele eisen voor:
- Foutcodes (bijv. player not found)
- Validatie van payload
- Sorteerlogica, limieten (top20, last20)
- Exacte JSON-vorm van response
- Opslagmechanisme

## 5. Data-structuren

Drie structs worden gebruikt:

### 5.1. LeaderboardEntry
| Key          | Type    |
| ------------ | ------- |
| player_id    | integer |
| rank         | string  |
| win_rate     | float   |
| games_played | integer |
| mmr          | integer |

### 5.2. PlayerStats
| Key          | Type    |
| ------------ | ------- |
| player_id    | integer |
| games_played | integer |
| wins         | integer |
| losses       | integer |
| win_rate     | float   |
| avg_damage   | integer |
| mmr          | integer |

### 5.3. GameResult
| Key           | Type           |
| ------------- | -------------- |
| winner_id     | integer        |
| loser_id      | integer        |
| winner_damage | integer        |
| loser_damage  | integer        |
| timestamp     | ISO8601 string |

## 6. Opstarten van de server

Ga naar de projectmap:
```
cd analytics_service_elixir
```

Start de server in de terminal:
```
iex.bat -S mix
```

Vervolgens in iex:
```
AnalyticsServer.start({127,0,0,1}, 7001)
```

Je ziet:
```
[AnalyticsServer] Listening on 127.0.0.1:7001
```
Als het gelukt is. Laat dit venster openstaan.

## 7. Testen van de service

### 7.1. Testclient (`test_client.exs)

Run in een tweede terminal (weer in dezelfde projectmap):
```
mix run test_client.exs
```

Voorbeeldoutput:
```
{"id":"1","payload":{"entries":[...]},
 "resource":"/leaderboard","status":200}
```

### 7.2. AAA-stijl testen

De test `analytics_server_test.exs` gebruikt AAA-stijl. 

Voer in de projectmap uit:
```
mix test test/analytics_server_test.exs
```

## 8. Tekortkoming voor een volledige service

Ondanks dat de server _werkt_, ontbreken formeel nog:

### 8.1. Domeinspecificaties

- Hoe leaderboard berekend moet worden (rank, mmr-formule, sortering)
- Hoe top20 precies moet worden bepaald
- Welke statistieken verplicht zijn
- Prioriteit van berekeningen
- Performance-eisen bij grote datasets

### 8.2. Error handling

- 400 → missing field
- 404 → player not found
- 500 → internal analytics error
- etc.

### 8.3. Opslag van analyticsdata

Op dit moment is alle data dummy.

## 9. Samenvatting

De Analytics-service bestaat uit:
1. JsonLineProtocol
- JSON newline-protocol
- strict & tolerant parsing
- standaard foutstructuur
2. AnalyticsServer
- TCP-listener
- route dispatch
3. AnalyticsService
- dummy-implementaties van leaderboard/stats/results
- gebruikt struct-modellen uit het [klassendiagram](https://confluenceasd.aimsites.nl/download/attachments/500346264/image-2025-11-14_15-47-7.png?version=1&modificationDate=1763131626650&api=v2)
4. Testclient
- stuurt berichten en leest serverrespons