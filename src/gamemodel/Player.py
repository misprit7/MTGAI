# Player class

from typing import Any, Dict
import datahelper as dh

class Player:
    id: int
    life: int
    maxHandSize: int
    startingLifeTotal: int
    turnNumber: int
    manaPool: Dict[str, Any]

    def __init__(self, player) -> None:
        self.id = player.get('controllerSeatId')
        self.life = player.get('lifeTotal')
        self.maxHandSize = player.get('maxHandSize')
        self.startingLifeTotal = player.get('startingLifeTotal')
        self.turnNumber = player.get('turnNumber')

        self.manaPool = player.get('manaPool') if 'manaPool' in player else []