# Base image 
# Gebruik Elixir + Erlang
FROM elixir:1.16.2

# Installeer tools 
RUN mix local.hex --force && \
    mix local.rebar --force

# Maak app directory 
WORKDIR /app

# Kopieer mix files (voor caching) 
COPY mix.exs mix.lock ./

# Installeren van dependencies (dev mode)
RUN mix deps.get

# Kopiëren van applicatie code
COPY lib ./lib

# Expose TCP port van Analytics Server
EXPOSE 7001

# Commando om Analytics Development Server te runnen 
# mix run --no-halt zort ervoor dat de server runt in de container 
CMD ["mix", "run", "--no-halt"]
