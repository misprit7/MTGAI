# Log Parsing

Log parsing is currently done in the Game.py class. Luckily, MTGA has an option to enable full game logs, which logs every single message exchanged between client and server. This data is all plaintext json, making it relatively easy to parse. While there are many different kinds of messages, the ones we mostly care about are game state ones. From the perspective of the client the game at every point is encapsulated in a gamestate json object. Whenever there's a change to this gamestate the server sends a json message representing the differences. This document is to document the format of the relevant messages. Note that this is super incomplete right now and something I need to get around to doing. 

# Game State Message
```json
{
    "gameinfo": { ... }, 
    "gameObjects": { ... }, 
    "players": { ... }, 
    "teams": { ... }, 
    "timers": { ... }, 
    "turnInfo": { ... },
    "zones": { ... }
}
```