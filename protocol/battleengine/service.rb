class Service
  def playedcard(payload, resource)
    sleep 0.5

    {
      status: 200,
      resource: resource,
      payload: {
        playedcard: "pot-o-greed"
      }
    }
  end
end
