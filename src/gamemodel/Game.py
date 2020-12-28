# Class representing full game state at any given point

from typing import Any, Dict, List
import sys, json, re, time
sys.path.append(r'./src')
# from mtga.set_data import all_mtga_cards as cards
import datahelper as dh
import ConfigHelper as config
import gamecontroller as gc
from GameObject import *
from Player import *
from Zone import *
import Choice




class Game:

    gameObjects: List[GameObject] = []
    zones: List[Zone] = []
    players: List[Player] = []
    turnInfo: Dict[str, Any] = {}
    choices: List[Choice.Choice] = []

    fp: int = 0
    path: str
    nummessages: int = 0
    gameStateId = 0
    curPlayer: int

    def __init__(self, path: str ='') -> None:
        self.reset()
        self.path = path

        # Only initialize path if it's actually passed
        if path:
            self.parseFile()

    def reset(self) -> None:
        self.gameObjects = []
        self.zones = []
        self.players = []

        self.turnInfo = {}
        self.choices = []

        self.gameStateId = 0
    


    # Helper functions
    def addGameObject(self, gameObject: GameObject) -> None:
        if gameObject['type'] == 'GameObjectType_Card':
            if gameObject['zoneId'] == self.zoneId('Battlefield'):
                if 'CardType_Creature' in gameObject['cardTypes']:
                    return Creature(gameObject)
                else:
                    return Card(gameObject)
            else:
                return Card(gameObject)
        else:
            return GameObject(gameObject)

    def addChoice(self, choice: Choice) -> None:
        if choice['actionType'] == 'ActionType_Cast':
            self.choices.append(Choice.Cast(choice))
        elif choice['actionType'] == 'ActionType_Play':
            self.choices.append(Choice.Play(choice))
        elif choice['actionType'] == 'ActionType_Pass':
            self.choices.append(Choice.Pass(choice))
        else:
            self.choices.append(Choice.Choice(choice))

    def zoneName(self, id: int) -> str:
        return next(x.type for x in self.zones if x.id == id)

    def zoneId(self, name: str) -> int:
        return next(x.id for x in self.zones if name.lower() in x.type.lower())

    def gameObject(self, instanceid: int) -> GameObject:
        return next(x for x in self.gameObjects if x.instanceId == instanceid)

    # Get subsets of gameObjects
    def permanents(self) -> List[Permanent]:
        return [x for x in self.gameObjects if isinstance(x, Permanent)]

    def creatures(self) -> List[Creature]:
        return [x for x in self.gameObjects if isinstance(x, Creature)]

    def lands(self) -> List[Land]:
        return [x for x in self.gameObjects if isinstance(x, Land)]

    def graveyard(self) -> List[Card]:
        return [x for x in self.gameObjects if self.zoneName(x.zone) == 'ZoneType_Graveyard' and isinstance(x, Card)]

    def hand(self) -> List[Card]:
        # return [self.zoneName(x.zone) for x in self.gameObjects]
        return [x for x in self.gameObjects if self.zoneName(x.zone) == 'ZoneType_Hand' and isinstance(x, Card)]
        
    
    # Log parsing

    # Parses file, game state will reflect state at end of file
    def parseFile(self) -> None:
        f = open(self.path)
        for line in f:
            if line.__contains__("{") and line.__contains__("}"):
                self.parseLine(line)
        f.close()

    # Updates game state from changes to file
    # Returns true if any update since last time, false otherwise
    def update(self) -> bool:
        f = open(self.path)
        f.seek(self.fp)
        ret: bool = False
        for line in f:
            if line.__contains__("{") and line.__contains__("}"):
                if self.parseLine(line):
                    ret = True
        self.fp = f.tell()
        f.close()
        return ret

    # Parses a single line passed as a string
    # Returns true if line is parsed successfully, false otherwise
    def parseLine(self, line: str) -> bool:
        try:
            # Parse transaction
            trans = json.loads(re.sub(r'^.*?{', '{', line))
        except:
            return False

        if 'greToClientEvent' in trans and 'greToClientMessages' in trans['greToClientEvent']:
            return self.parseMessages(trans)
        elif 'matchGameRoomStateChangedEvent' in trans:
            self.parseGameRoomChange(trans)
        return False

    # Parses game state changed event (i.e. game start)
    # Mostly for figuring out which player the AI actually is
    def parseGameRoomChange(self, trans: Dict[str, Any]) -> None:
        # Don't want to reset at end of game while testing
        # Might be worth changing so "Game" encapsulates one game instead of session
        if trans['matchGameRoomStateChangedEvent']['gameRoomInfo'].get('stateType') != 'MatchGameRoomStateType_Playing':
            return 
        # Reset variables
        self.reset()
        # Set current player to proper one
        players: Dict[str, Any] = trans['matchGameRoomStateChangedEvent']['gameRoomInfo']['gameRoomConfig'].get('reservedPlayers')
        if players:
            self.curPlayer = next(x['teamId'] for x in players if x['playerName'] == config.playername)

    # Parses messages
    def parseMessages(self, trans: Dict[str, Any]) -> bool:
        try: 
            msgs = trans['greToClientEvent']['greToClientMessages']
        except:
            return False

        ret = False
        for msg in msgs:
            if msg.get('type') == 'GREMessageType_GameStateMessage':
                self.updateGameState(msg.get('gameStateMessage'))
                ret = True
            elif msg.get('type') == 'GREMessageType_ActionsAvailableReq':
                self.updateChoices(msg.get('actionsAvailableReq'))
                ret = True
            elif msg.get('type') == 'GREMessageType_DeclareAttackersReq':
                self.updateAttackers(msg)
                ret = True
            elif msg.get('type') == 'GREMessageType_DeclareBlockersReq':
                self.updateBlockers(msg)
                ret = True
        
        return ret
        # if len([x for x in msgs if x['type'] == 'GREMessageType_ActionsAvailableReq']) == 0:
        #     self.choices.clear()

    def updateGameState(self, msg: Dict[str, Any]) -> None:
        for key in msg.keys():
            if key in ('type', 'msgId', 'actions', 'annotations'):
                continue
            
            if type(msg[key]) != dict and type(msg[key]) != list:
                if key == 'gameStateId':
                    self.gameStateId = msg[key]
                continue

            if key == 'turnInfo':
                self.turnInfo = msg[key]
                continue
            
            id: str = dh.keyid.get(key, '')
            updated: bool = False

            if key != 'diffDeletedInstanceIds':
                for new in msg[key]:
                    if key == 'gameObjects':
                        for k in range(len(self.gameObjects)):
                            if self.gameObjects[k].instanceId == new[id]:
                                self.gameObjects[k] = self.addGameObject(new)
                                updated = True
                    elif key == 'players':
                        for k in range(len(self.players)):
                            if self.players[k].id == new[id]:
                                self.players[k] = Player(new)
                                updated = True
                    elif key == 'zones':
                        for k in range(len(self.zones)):
                            if self.zones[k].id == new[id]:
                                self.zones[k] = Zone(new)
                                updated = True
                    
                    if not updated:
                        if key == 'gameObjects':
                            self.gameObjects.append(self.addGameObject(new))
                        elif key == 'players':
                            self.players.append(Player(new))
                        elif key == 'zones':
                            self.zones.append(Zone(new))
                    else:
                        updated = False
            else:
                self.gameObjects = [x for x in self.gameObjects if x.instanceId not in msg[key]]

    def updateChoices(self, actions: List[Choice.Choice]):
        self.choices.clear()
        for action in actions.get('actions'):
            self.addChoice(action)

    def updateAttackers(self, msg: Dict[str, Any]):
        assert msg.get('gameStateId') == self.gameStateId
        self.choices.clear()
        self.choices.append(Choice.DeclareAttackers(msg))

    def updateBlockers(self, msg: Dict[str, Any]):
        assert msg.get('gameStateId') == self.gameStateId
        self.choices.clear()
        self.choices.append(Choice.DeclareBlockers(msg))



if __name__ == "__main__":
    game = Game(config.logpath)
    gc.beginindexing()
    while 1:
        game.update()
        if game.turnInfo['decisionPlayer'] == game.curPlayer:
            print([x.actionType for x in game.choices])
            playchoice = next(x for x in game.choices if x.actionType == 'ActionType_Play')
            playchoice.execute()
        time.sleep(1)
