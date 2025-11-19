require 'async'
require 'async/tcp'

class Server
  def initialize(host: "127.0.0.1", port: 6767)
    @host = host
    @port = port
    @service = Service.new

    @routes = {
      "playedcard"    => @service.method(:login)
    }
  end

  def start
    Async do |task|
      endpoint = Async::IO::Endpoint.tcp(@host, @port)

      puts "BattleEngineServer started on #{@host}:#{@port}"

      endpoint.accept do |client|
        task.async { handle_client(client) }
      end
    end
  end

  async def handle_client(socket)
    buffer = ""

    reader = socket
    writer = socket

    loop do
      data = reader.read(1024)
      break if data.nil? || data.empty?

      buffer << data

      messages, buffer = parse_messages(buffer)

      messages.each do |msg|
        Async::Task.current.async do
          process_message(msg, writer)
        end
      end
    end

    socket.close
  end

  async def process_message(msg, writer)
    req_id   = msg["id"]
    action   = msg["action"]
    resource = msg["resource"]
    payload  = msg["payload"] || {}

    unless @routes.key?(action)
      resp = {
        "id" => req_id,
        "status" => 400,
        "resource" => resource,
        "payload" => { "error" => "unknown action" }
      }
      send_message(writer, resp)
      return
    end

    handler = @routes[action]

    result = handler.(payload, resource).wait

    resp = { "id" => req_id }.merge(result)

    send_message(writer, resp)
  end
end

if __FILE__ == $0
  server = Server.new(host: "127.0.0.1", port: 6001)
  server.start
end
