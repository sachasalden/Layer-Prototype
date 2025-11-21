defmodule AnalyticsService do
  @moduledoc """
  Businesslogica voor de Analytics-service.

  LET OP:
  - Alle functies hieronder geven nu dummy-data terug om de vorm
    van de responses en de integratie met AnalyticsServer te tonen.
  - In een echte implementatie hoort hier:
      * opslaglaag (database / ETS / externe service),
      * aggregatielogica (MMR, win_rate, avg_damage),
      * foutafhandeling (bijv. player niet gevonden),
      * performance-afwegingen (bij grote aantallen spelers).
  """

  alias LeaderboardEntry
  alias PlayerStats
  alias GameResult

  @type payload :: map()
  @type resource :: String.t()
  @type response :: map()

  # ---------------------------------------------------------------------------
  # Leaderboard: volledige lijst
  # ---------------------------------------------------------------------------

  @doc """
  Haalt het volledige leaderboard op.

  Contractueel verwachten we:
  - Request:
      action: "leaderboard"
      resource: bijv. "/leaderboard"
      payload: {} (waarschijnlijk leeg)

  - Response:
      {
        "status": 200,
        "resource": "/leaderboard",
        "payload": { "entries": [ ...LeaderboardEntry... ] }
      }

  LET OP:
  - De exacte JSON-structuur van `payload` ("entries" vs "leaderboard" etc.)
    is nu een aanname. Deze hoort in het API-contract met voorbeelden te worden
    vastgelegd.
  """
  @spec leaderboard(payload(), resource()) :: response()
  def leaderboard(_payload, resource) do
    # TODO: echte data ophalen i.p.v. dummy-lijst
    entries = [
      %LeaderboardEntry{
        player_id: 1,
        rank: "Gold I",
        win_rate: 0.61,
        games_played: 120,
        mmr: 1850
      },
      %LeaderboardEntry{
        player_id: 2,
        rank: "Silver II",
        win_rate: 0.53,
        games_played: 90,
        mmr: 1600
      }
    ]

    %{
      "status" => 200,
      "resource" => resource,
      "payload" => %{
        "entries" => Enum.map(entries, &Map.from_struct/1)
      }
    }
  end

  # ---------------------------------------------------------------------------
  # Leaderboard: top 20
  # ---------------------------------------------------------------------------

  @doc """
  Haalt de top 20 van het leaderboard op.

  LET OP:
  - In een echte implementatie zou hier:
      * sortering op mmr/rank,
      * beperking tot 20 entries,
      * duidelijke definitie van tie-breakers
    vastgelegd moeten worden. Dat ontbreekt nu nog als formele regel.
  """
  @spec leaderboard_top20(payload(), resource()) :: response()
  def leaderboard_top20(payload, resource) do
    base = leaderboard(%{}, resource)
    Map.put(base, "resource", resource)
  end

  # ---------------------------------------------------------------------------
  # Player stats
  # ---------------------------------------------------------------------------

  @doc """
  Basis player stats.

  Contractuele aannames:
  - action: "stats_for_player"
  - resource: bijv. "/stats/:playerId"
  - payload: { "player_id": integer }

  LET OP:
  - Zonder voorbeeld-requests uit de gateway is niet duidelijk of `player_id`
    in `resource` zit, in `payload`, of allebei.
  """
  @spec player_stats(payload(), resource()) :: response()
  def player_stats(payload, resource) do
    player_id = Map.get(payload, "player_id", 0)

    # TODO:
    # - echte lookup op player_id
    # - foutcode (404) als speler niet bestaat
    stats = %PlayerStats{
      player_id: player_id,
      games_played: 120,
      wins: 73,
      losses: 47,
      win_rate: 0.61,
      avg_damage: 350,
      mmr: 1850
    }

    %{
      "status" => 200,
      "resource" => resource,
      "payload" => Map.from_struct(stats)
    }
  end

  @doc """
  Gedetailleerde stats, bijv. andere aggregaties of extra velden.

  LET OP:
  - Zonder duidelijke use-case is het verschil met `player_stats/2`
    nu vooral illustratief. In een echt systeem zou hier extra
    data of een ander aggregatieniveau moeten zitten.
  """
  @spec player_stats_detailed(payload(), resource()) :: response()
  def player_stats_detailed(payload, resource) do
    # Voor nu: zelfde implementatie als player_stats/2
    player_stats(payload, resource)
  end

  # ---------------------------------------------------------------------------
  # Game results
  # ---------------------------------------------------------------------------

  @doc """
  Alle resultaten voor een speler.

  Contractuele aannames:
  - action: "results_for_player"
  - resource: bijv. "/results/:playerId"
  - payload: { "player_id": integer }

  TODO:
  - definieer paging/limit (bijv. max aantal resultaten),
  - definieer sorteerorde (recent eerst, op timestamp).
  """
  @spec player_results(payload(), resource()) :: response()
  def player_results(payload, resource) do
    player_id = Map.get(payload, "player_id", 0)

    # TODO: echte query op player_id
    results = [
      %GameResult{
        winner_id: player_id,
        loser_id: 42,
        winner_damage: 500,
        loser_damage: 250,
        timestamp: DateTime.utc_now()
      },
      %GameResult{
        winner_id: 42,
        loser_id: player_id,
        winner_damage: 430,
        loser_damage: 410,
        timestamp: DateTime.utc_now()
      }
    ]

    %{
      "status" => 200,
      "resource" => resource,
      "payload" => %{
        "results" =>
          Enum.map(results, fn r ->
            r
            |> Map.from_struct()
            # DateTime moet voor JSON naar string
            |> Map.update!("timestamp", &DateTime.to_iso8601/1)
          end)
      }
    }
  end

  @doc """
  Laatste 20 resultaten voor een speler.

  LET OP:
  - In een echte implementatie:
      * limit = 20 (hard of configureerbaar),
      * gegarandeerde sorteerorde (recentste eerst),
      * duidelijke performance-afspraken bij grote aantallen matches.
  """
  @spec player_last20_results(payload(), resource()) :: response()
  def player_last20_results(payload, resource) do
    # Voor nu: zelfde data als player_results/2, maar in een echt systeem
    # zou hier expliciet een LIMIT 20 of vergelijkbare restrictie op zitten.
    player_results(payload, resource)
  end
end
