defmodule JsonLineProtocol do
  @moduledoc """
  Line-based JSON protocol:

  - Elke boodschap is één JSON-object, gevolgd door een newline (`\\n`).
  - Buffers kunnen meerdere berichten bevatten.
  - `parse_messages/1` leest alleen geldige JSON en laat fouten doorslaan.
  - `read_messages/1` vervangt ongeldige JSON door een gestandaardiseerd `error_message/3`.
  """

  # error_message/3
  # ---------------------------------------------------------------------------
  @doc """
  Maakt een foutbericht.
  """
  @spec error_message(integer(), String.t(), String.t()) :: map()
  def error_message(status, resource, reason) do
    %{
      "status" => status,
      "resource" => resource,
      "payload" => %{
        "error" => reason
      }
    }
  end

  # encode_message/1
  # ---------------------------------------------------------------------------
  @doc """
  Encodeert een Elixir-structuur (`msg`) naar JSON + newline.
  """
  @spec encode_message(term()) :: binary()
  def encode_message(msg) do
    # Jason.encode!/1 gooit een exception bij fout; Fouten worden afgevangen
    # in de call-site.
    Jason.encode!(msg) <> "\n"
  end

  # send_message/2
  # ---------------------------------------------------------------------------
  @doc """
  Stuurt een bericht via een gegeven `writer`.
  """
  @spec send_message(:gen_tcp.socket(), term()) :: :ok | {:error, term()}
  def send_message(writer, msg) do
    data = encode_message(msg)
    # In Elixir is dit asynchroon genoeg; de process die dit aanroept
    # blokkeert slechts kort. Expliciete async/await zoals
    # in Python is niet nodig.
    :gen_tcp.send(writer, data)
  end

  # parse_messages/1
  # ---------------------------------------------------------------------------
  @doc """
  Parseert alle volledige JSON-berichten uit een `buffer` zonder foutafhandeling.
  """
  @spec parse_messages(binary()) :: {list(map()), binary()}
  def parse_messages(buffer) when is_binary(buffer) do
    do_parse_messages(buffer, [])
  end

  # Private helper: loopt recursief door de buffer heen.
  defp do_parse_messages(buffer, acc) do
    # Split slechts in twee delen:
    # - `line` : alles tot de eerste `\\n`
    # - `rest` : de rest van de buffer
    case String.split(buffer, "\n", parts: 2) do
      # Geval 1: we hebben een complete regel + rest
      [line, rest] ->
        line = String.trim(line)

        acc =
          if line == "" do
            # Lege regels negeren.
            acc
          else
            # decode; kan een exception gooien bij ongeldige JSON.
            msg = Jason.decode!(line)
            [msg | acc]
          end

        do_parse_messages(rest, acc)

      # Geval 2: er is geen `\\n` meer → buffer bevat een incomplete regel
      [incomplete] ->
        {Enum.reverse(acc), incomplete}
    end
  end

  # read_messages/1
  # ---------------------------------------------------------------------------
  @doc """
  Leest alle berichten uit `buffer` maar vervangt ongeldige JSON door `error_message/3`.

  Gedrag:
  - Verschil: JSON-decode fouten worden afgevangen en vertaald naar:
      `error_message(400, "/", "INVALID_JSON")`
  - Ook hier:
      - Lege regels worden overgeslagen.
      - Resultaat is `{messages, rest_buffer}`.
  """
  @spec read_messages(binary()) :: {list(map()), binary()}
  def read_messages(buffer) when is_binary(buffer) do
    do_read_messages(buffer, [])
  end

  # Private helper voor read_messages/1
  defp do_read_messages(buffer, acc) do
    case String.split(buffer, "\n", parts: 2) do
      [line, rest] ->
        line = String.trim(line)

        acc =
          if line == "" do
            acc
          else
            msg =
              try do
                Jason.decode!(line)
              rescue
                _ ->
                  error_message(400, "/", "INVALID_JSON")
              end

            [msg | acc]
          end

        do_read_messages(rest, acc)

      [incomplete] ->
        {Enum.reverse(acc), incomplete}
    end
  end
end
