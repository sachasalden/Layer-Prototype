defmodule PlayerStats do
  @moduledoc """
  Struct voor geaggregeerde spelerstatistieken.
  """

  @enforce_keys [
    :player_id,
    :games_played,
    :wins,
    :losses,
    :win_rate,
    :avg_damage,
    :mmr
  ]
  defstruct [
    :player_id,
    :games_played,
    :wins,
    :losses,
    :win_rate,
    :avg_damage,
    :mmr
  ]
end
