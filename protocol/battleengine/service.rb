require 'async'

class Service
  include Async::Await

  async def playedcard(payload, resource)
    Async::Task.current.sleep(0.5)
    {
      status: 200,
      resource: resource,
      payload: { playedcard: "pot-o-greed" }
    }
  end
