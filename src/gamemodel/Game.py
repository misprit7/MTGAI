# Class representing full game state at any given point

import sys, json, re, time
sys.path.append(r'./src')
# from mtga.set_data import all_mtga_cards as cards
import datahelper as dh
import logparser as lp
import ConfigHelper as config
import gamecontroller as gc
from GameObject import *
from Player import *
from Zone import *
import Choice




class Game:
    def __init__(self, path=''):
        self.reset()
        self.fp = 0
        self.path = path

        # Only initialize path if it's actually passed
        if path:
            self.parseFile()

    def reset(self):
        self.gameObjects = []
        self.zones = []
        self.players = []

        self.actionQueue = []
        self.turnInfo = {}
        self.choices = []

        self.gameStateId = 0
    


    # Helper funtions
    def addGameObject(self, gameObject):
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

    def addChoice(self, choice):
        if choice['actionType'] == 'ActionType_Cast':
            self.choices.append(Choice.Cast(choice))
        elif choice['actionType'] == 'ActionType_Play':
            self.choices.append(Choice.Play(choice))
        elif choice['actionType'] == 'ActionType_Pass':
            self.choices.append(Choice.Pass(choice))
        else:
            self.choices.append(Choice.Choice(choice))

    def zoneName(self, id):
        return next(x.type for x in self.zones if x.id == id)

    def zoneId(self, name):
        return next(x.id for x in self.zones if name.lower() in x.type.lower())

    def gameObject(self, instanceid):
        return next(x for x in self.gameObjects if x.instanceId == instanceid)

    # Get subsets of gameObjects
    def permanents(self):
        return [x for x in self.gameObjects if isinstance(x, Permanent)]

    def creatures(self):
        return [x for x in self.gameObjects if isinstance(x, Creature)]

    def lands(self):
        return [x for x in self.gameObjects if isinstance(x, Land)]

    def graveyard(self):
        return [x for x in self.gameObjects if self.zoneName(x.zone) == 'ZoneType_Graveyard']

    def hand(self):
        # return [self.zoneName(x.zone) for x in self.gameObjects]
        return [x for x in self.gameObjects if self.zoneName(x.zone) == 'ZoneType_Hand']
        
    
    # Log parsing

    # Parses file, game state will reflect state at end of file
    def parseFile(self):
        f = open(self.path)
        for line in f:
            if line.__contains__("{") and line.__contains__("}"):
                self.parseLine(line)
        f.close()

    # Updates game state from changes to file
    # Right now pretty much just copy of parseFile but might change later and should probably be seperate
    def update(self):
        f = open(self.path)
        f.seek(self.fp)
        for line in f:
            if line.__contains__("{") and line.__contains__("}"):
                self.parseLine(line)
        f.close()

    # Parses a single line passed as a string
    def parseLine(self, line):
        try:
            # Parse transaction
            trans = json.loads(re.sub(r'^.*?{', '{', line))
        except:
            return

        if 'greToClientEvent' in trans and 'greToClientMessages' in trans['greToClientEvent']:
            self.parseMessages(trans)
        elif 'matchGameRoomStateChangedEvent' in trans:
            self.parseGameRoomChange(trans)

    # Parses game state changed event (i.e. game start)\
    # Mostly for figuring out which player the AI actually is
    def parseGameRoomChange(self, trans):
        # Don't want to reset at end of game while testing
        # Might be worth changing so "Game" encapsulates one game instead of session
        if trans['matchGameRoomStateChangedEvent']['gameRoomInfo'].get('stateType') != 'MatchGameRoomStateType_Playing':
            return 
        # Reset variables
        self.reset()
        # Set current player to proper one
        players = trans['matchGameRoomStateChangedEvent']['gameRoomInfo']['gameRoomConfig'].get('reservedPlayers')
        if players:
                self.curPlayer = next(x['teamId'] for x in players if x['playerName'] == config.playername)

    # Parses messages
    def parseMessages(self, trans):
        try: 
            msgs = trans['greToClientEvent']['greToClientMessages']
        except:
            return

        for msg in msgs:
            if msg.get('type') == 'GREMessageType_GameStateMessage':
                self.updateGameState(msg.get('gameStateMessage'))
            elif msg.get('type') == 'GREMessageType_ActionsAvailableReq':
                self.updateChoices(msg.get('actionsAvailableReq'))
        
        # if len([x for x in msgs if x['type'] == 'GREMessageType_ActionsAvailableReq']) == 0:
        #     self.choices = []

    def updateGameState(self, msg):
        for key in msg.keys():
            if key in ('type', 'msgId', 'actions', 'annotations'):
                continue
            
            if type(msg[key]) != dict and type(msg[key]) != list:
                if key == 'gameStateId':
                    self.gameStateId = 26
                continue

            if key == 'turnInfo':
                self.turnInfo = msg[key]
                continue
            
            id = dh.keyid.get(key, '')
            updated = False

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
                            self.gameObjects.append(GameObject(new))
                        elif key == 'players':
                            self.players.append(Player(new))
                        elif key == 'zones':
                            self.zones.append(Zone(new))
                    else:
                        updated = False
            else:
                self.gameObjects = [x for x in self.gameObjects if x.instanceId not in msg[key]]

    def updateChoices(self, actions):
        self.choices = []
        for action in actions.get('actions'):
            self.addChoice(action)


if __name__ == "__main__":
    game = Game(config.logpath)
    while 1:
        game.update()
        if game.turnInfo['decisionPlayer'] == game.curPlayer:
            print([x.actionType for x in game.choices])
            gc.beginindexing()
            playchoice = next(x for x in game.choices if x.actionType == 'ActionType_Play')
            # playchoice.execute()
        time.sleep(1)
