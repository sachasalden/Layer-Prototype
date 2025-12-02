{:ok, socket} = :gen_tcp.connect({127, 0, 0, 1}, 7001, [:binary, packet: :raw, active: false])

msg = %{
  "id" => "1",
  "action" => "leaderboard",
  "resource" => "/analytics",
  "payload" => %{}
}

line = Jason.encode!(msg) <> "\n"
:gen_tcp.send(socket, line)

{:ok, response} = :gen_tcp.recv(socket, 0)
IO.puts("Response: #{response}")
