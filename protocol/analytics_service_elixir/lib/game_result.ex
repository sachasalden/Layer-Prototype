defmodule GameResult do
  @moduledoc """
  Struct voor één matchresultaat.

  LET OP:
  - timestamp wordt als DateTime opgeslagen.
    Voor JSON-export moet deze geconverteerd worden naar een string,
    zoals gedaan wordt in AnalyticsService.player_results/2.
  """

  @enforce_keys [
    :winner_id,
    :loser_id,
    :winner_damage,
    :loser_damage,
    :timestamp
  ]
  defstruct [
    :winner_id,
    :loser_id,
    :winner_damage,
    :loser_damage,
    :timestamp
  ]
end
