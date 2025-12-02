defmodule AnalyticsServerTest do
  use ExUnit.Case

  @moduletag :integration

  @host {127, 0, 0, 1}
  @port 7001

  setup_all do
    # Arrange (server): server starten *eenmalig* voor alle tests
    spawn(fn ->
      AnalyticsServer.start(@host, @port)
    end)

    # Klein beetje wachten zodat de server klaar is
    Process.sleep(150)

    :ok
  end

  test "leaderboard request returns a valid response in AAA-style" do
    # --------------------
    #  Arrange
    # --------------------

    # 1. Verbinden met server
    {:ok, socket} =
      :gen_tcp.connect(@host, @port, [:binary, packet: :raw, active: false])

    # 2. Bouw het bericht dat we willen versturen
    msg = %{
      "id" => "test-1",
      "action" => "leaderboard",
      "resource" => "/analytics",
      "payload" => %{}
    }

    encoded = Jason.encode!(msg) <> "\n"

    # --------------------
    #  Act
    # --------------------
    :ok = :gen_tcp.send(socket, encoded)

    {:ok, raw_response} = :gen_tcp.recv(socket, 0)
    {:ok, response} = Jason.decode(raw_response)

    # --------------------
    #  Assert
    # --------------------

    assert response["id"] == "test-1"
    assert response["status"] == 200
    assert response["resource"] == "/analytics"

    # payload-structure check
    assert is_map(response["payload"])
    assert Map.has_key?(response["payload"], "entries")
    assert is_list(response["payload"]["entries"])
  end
end
