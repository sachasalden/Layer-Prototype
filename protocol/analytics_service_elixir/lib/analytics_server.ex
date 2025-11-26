defmodule AnalyticsServer do
  @moduledoc """
  TCP-server voor de Analytics-service.

  - Gebruikt JsonLineProtocol voor (de)serialisatie.
  - Verwacht berichten met de velden: "id", "action", "resource", "payload".
  - Routeert op basis van "action" naar functies in AnalyticsService.

  LET OP:
  - De gekozen action-namen in `route/1` zijn een aannemelijk voorstel
    op basis van het klassediagram (leaderboard, stats, results), maar
    hiervoor ontbreekt eigenlijk een formeel API-contract met:
      * exacte action-strings (zoals de gateway ze verstuurt),
      * voorbeeld JSON-requests,
      * voorbeeld JSON-responses,
      * foutcodes (player not found, invalid payload, etc.).
    → Deze zaken MOETEN in een apart API-document worden vastgelegd
      om deze server 100% contract-juist te maken.
  """

  # Publieke start-functie om de server handmatig te draaien.
  # Voor nu geen OTP-supervisor, maar een simpel luisterende socket.
  @spec start(charlist() | :inet.ip_address(), non_neg_integer()) :: :ok | {:error, term()}
  def start(host \\ {0, 0, 0, 0}, port \\ 7001) do
    # NOTE:
    # - host-parameter wordt nu alleen gebruikt voor logging, niet voor listen.
    #   :gen_tcp.listen bindt op alle interfaces, tenzij anders geconfigureerd.
    #   Als dit belangrijk is, moet hier nog expliciet binding op `host` komen.
    {:ok, listen_socket} =
      :gen_tcp.listen(port, [:binary, packet: :raw, active: false, reuseaddr: true])

    IO.puts("[AnalyticsServer] Listening on #{:inet.ntoa(host)}:#{port}")

    accept_loop(listen_socket)
  end

  # Interne accept-loop: accepteert clients en start per client een proces.
  defp accept_loop(listen_socket) do
    {:ok, socket} = :gen_tcp.accept(listen_socket)
    IO.puts("[AnalyticsServer] Client connected")

    # Voor elke client een nieuw proces starten.
    # In een volwassen OTP-app zou dit via een Supervisor gebeuren.
    spawn(fn -> handle_client(socket, "") end)

    accept_loop(listen_socket)
  end

  # Leest data van de client, bouwt een buffer op en parseert berichten
  # via JsonLineProtocol.parse_messages/1 (strict; invalid JSON gooit exception).
  #
  # LET OP:
  # - We gebruiken hier parse_messages/1 en NIET read_messages/1.
  #   Dit volgt de Ruby/Python servers, maar betekent:
  #   → protocolniveau JSON-fouten worden NIET afgehandeld als nette error_message.
  #   Als contractueel is afgesproken dat INVALID_JSON via het protocol moet
  #   worden teruggegeven, moet hier read_messages/1 gebruikt worden
  #   en extra error-afhandeling plaatsvinden.
  defp handle_client(socket, buffer) do
    case :gen_tcp.recv(socket, 0) do
      {:ok, data} ->
        buffer = buffer <> data
        {messages, rest} = JsonLineProtocol.parse_messages(buffer)

        Enum.each(messages, fn msg ->
          # Per bericht een apart proces, zodat trage analytics-logica
          # de recv-loop niet blokkeert.
          spawn(fn -> process_message(msg, socket) end)
        end)

        handle_client(socket, rest)

      {:error, :closed} ->
        IO.puts("[AnalyticsServer] Client disconnected")

      {:error, reason} ->
        IO.puts("[AnalyticsServer] recv error: #{inspect(reason)}")
    end
  end

  # Verwerkt één bericht:
  # - leest id, action, resource, payload
  # - zoekt de handler in route/1
  # - stuurt response terug via JsonLineProtocol.send_message/2
  #
  # LET OP:
  # - Hier gaan we ervan uit dat action/resource/payload altijd aanwezig
  #   zijn en een bepaald type hebben. In de praktijk hoort hier:
  #     * validatie op verplichte velden,
  #     * type-checks,
  #     * duidelijke foutcodes (bijv. 422 voor invalid payload).
  #   → Deze regels horen in het API-contract + implementatie te worden vastgelegd.
  defp process_message(msg, socket) do
    id = msg["id"]
    action = msg["action"]
    resource = msg["resource"]
    payload = Map.get(msg, "payload", %{})

    case route(action) do
      nil ->
        # Onbekende actie → zelfde gedrag als de andere talen.
        resp = %{
          "id" => id,
          "status" => 400,
          "resource" => resource,
          "payload" => %{"error" => "unknown action"}
        }

        JsonLineProtocol.send_message(socket, resp)

      {:ok, handler} ->
        # Handler heeft signatuur: (payload :: map(), resource :: String.t()) :: map()
        result = handler.(payload, resource)

        # We plakken de id erbij
        resp = Map.put(result, "id", id)
        JsonLineProtocol.send_message(socket, resp)
    end
  end

  # Routeert action-string naar de bijbehorende functie in AnalyticsService.
  #
  # BELANGRIJK:
  # - De onderstaande action-namen zijn een aannemelijke mapping op basis
  #   van de routes uit het diagram:
  #       /leaderboard
  #       /leaderboard/top20
  #       /stats/:playerId
  #       /stats/:playerId/getStats
  #       /results/:playerId
  #       /results/:playerId/last20games
  #
  #   Maar:
  #   → De gateway kan andere action-strings gebruiken (bijv. "get_leaderboard"
  #      i.p.v. "leaderboard"). Zonder voorbeeld-JSON van de gateway blijft dit
  #      een aannname.
  #   → Dit hoort formeel vastgelegd te worden in het API-contract tussen
  #      gateway en Analytics-service.
  defp route(action) do
    case action do
      "leaderboard" ->
        {:ok, &AnalyticsService.leaderboard/2}

      "leaderboard_top20" ->
        {:ok, &AnalyticsService.leaderboard_top20/2}

      "stats_for_player" ->
        {:ok, &AnalyticsService.player_stats/2}

      "stats_getStats" ->
        {:ok, &AnalyticsService.player_stats_detailed/2}

      "results_for_player" ->
        {:ok, &AnalyticsService.player_results/2}

      "results_last20" ->
        {:ok, &AnalyticsService.player_last20_results/2}

      _ ->
        nil
    end
  end
end

# Start automatisch wanneer Mix.env() == :dev
if Mix.env() == :dev do
  # Bind op 0.0.0.0 zodat Docker het kan bereiken
  spawn(fn -> AnalyticsServer.start({0, 0, 0, 0}, 7001) end)
end
