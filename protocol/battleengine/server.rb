require "socket"
require "json"
require_relative "service"
require_relative "protocol"

class Server
  def initialize(host: "127.0.0.1", port: 6003)
    @host = host
    @port = port
    @service = Service.new

    @routes = {
      "playedcard" => @service.method(:playedcard)
    }
  end

  def start
    server = TCPServer.new(@host, @port)
    puts "BattleEngineServer started on #{@host}:#{@port}"

    loop do
      client = server.accept

      Thread.new(client) do |socket|
        begin
          handle_client(socket)
        rescue => e
          warn "Client error: #{e.class}: #{e.message}"
        ensure
          socket.close unless socket.closed?
        end
      end
    end
  end

  private

  def handle_client(socket)
    buffer = +""

    loop do
      data = socket.readpartial(1024)  # blokkeert tot er data is of client sluit
      buffer << data

      messages, buffer = parse_messages(buffer)

      messages.each do |msg|
        process_message(msg, socket)
      end
    end
  rescue EOFError
    # client heeft verbinding netjes gesloten → klaar
  end

  def process_message(msg, socket)
    req_id   = msg["id"]
    action   = msg["action"]
    resource = msg["resource"]
    payload  = msg["payload"] || {}

    handler = @routes[action]

    unless handler
      resp = {
        "id"       => req_id,
        "status"   => 400,
        "resource" => resource,
        "payload"  => { "error" => "unknown action" }
      }
      send_message(socket, resp)
      return
    end

    # Sync call naar de service
    result = handler.call(payload, resource)

    # result is bijv.:
    # { status: 200, resource: ..., payload: {...} }
    # We mergen het met de id:
    resp = { "id" => req_id }.merge(stringify_keys(result))

    send_message(socket, resp)
  end

  # Helper om symbol keys om te zetten naar strings (voor JSON / protocol-consistentie)
  def stringify_keys(hash)
    hash.transform_keys { |k| k.to_s }
  end
end

if __FILE__ == $0
  host = ENV.fetch("HOST", "0.0.0.0")
  port = Integer(ENV.fetch("PORT", "6003"))
  server = Server.new(host: host, port: port)
  server.start
end
