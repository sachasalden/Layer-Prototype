require "json"

def error_message(status, resource, reason)
  {
    "status"   => status,
    "resource" => resource,
    "payload"  => { "error" => reason }
  }
end

# Modern sync send_message, geen async syntax meer
def send_message(writer, msg)
  json = JSON.generate(msg) + "\n"
  writer.write(json)
  writer.flush
end

def parse_messages(buffer)
  messages = []

  while buffer.include?("\n")
    line, buffer = buffer.split("\n", 2)
    next if line.strip.empty?
    messages << JSON.parse(line)
  end

  [messages, buffer]
end

def read_messages(buffer)
  messages = []

  while buffer.include?("\n")
    line, buffer = buffer.split("\n", 2)
    next if line.strip.empty?

    begin
      messages << JSON.parse(line)
    rescue JSON::ParserError
      messages << error_message(400, "/", "INVALID_JSON")
    end
  end

  [messages, buffer]
end
