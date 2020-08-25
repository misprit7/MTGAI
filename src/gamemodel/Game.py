# Class representing full game state at any given point

import sys
sys.path.append(r'./src')
# from mtga.set_data import all_mtga_cards as cards
import datahelper as dh
import logparser as lp
from GameObject import *

class Game:
    def __init__(self, gamestate):
        self.gamestate = gamestate
        self.gameObjects = []
        self.zones = []
        try:
            for zone in gamestate.get('zones'):
                self.zones.append(Zone(zone))
        except:
            pass
        try:
            for gameObject in gamestate.get('gameObjects'):
                self.addGameObject(gameObject)
        except:
            pass

        self.actionQueue = []

        turninfo = gamestate.get('turnInfo')
        if turninfo:
            self.activePlayer = turninfo.get('activePlayer')
            self.priorityPlayer = turninfo.get('priorityPlayer')
            self.phase = turninfo.get('phase')

    


    # Helper funtions
    def addGameObject(self, gameObject):
        if gameObject['type'] == 'GameObjectType_Card':
            if gameObject['zoneId'] == self.zoneId('Battlefield'):
                if 'CardType_Creature' in gameObject['cardTypes']:
                    self.gameObjects.append(Creature(gameObject))
            else:
                self.gameObjects.append(Card(gameObject))

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
        


if __name__ == "__main__":
    game = Game(lp.gamestate)
    print([x.name for x in game.creatures()])
