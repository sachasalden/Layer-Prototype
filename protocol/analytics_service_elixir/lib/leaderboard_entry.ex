defmodule LeaderboardEntry do
  @moduledoc """
  Struct voor één regel in het leaderboard.

  LET OP:
  - Types zijn afgeleid uit het klassediagram:
      player_id: integer
      rank: String
      win_rate: float
      games_played: integer
      mmr: integer
  """

  @enforce_keys [:player_id, :rank, :win_rate, :games_played, :mmr]
  defstruct [:player_id, :rank, :win_rate, :games_played, :mmr]
end
