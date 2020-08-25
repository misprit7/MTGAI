# Player class

import datahelper as dh

class Player:
    def __init__(self, player):
        self.id = player.get('controllerSeatId')
        self.life = player.get('lifeTotal')
        self.maxHandSize = player.get('maxHandSize')
        self.startingLifeTotal = player.get('startingLifeTotal')
        self.turnNumber = player.get('turnNumber')

        self.manaPool = player.get('manaPool') if 'manaPool' in player else []