import os

SERVICES = {
    "/user":   (os.getenv("USER_HOST", "userservice"), int(os.getenv("USER_PORT", "6001"))),
    "/card":   (os.getenv("CARD_HOST", "cardcollection"), int(os.getenv("CARD_PORT", "4001"))),
    "/battle": (os.getenv("BATTLE_HOST", "battleengine"), int(os.getenv("BATTLE_PORT", "6003"))), 
    "/analytics": (os.getenv("ANALYTICS_HOST", "analyticsservice"), int(os.getenv("ANALYTICS_POST", "7001")))
}
