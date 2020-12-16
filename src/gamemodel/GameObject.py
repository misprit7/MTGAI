# GameObject and inheritors

from typing import Any, Dict, List
import datahelper as dh

class GameObject:
    grpId: int
    instanceId: int
    owner: int
    controller: int
    visibility: str
    type: str
    zone: int
    name: str

    def __init__(self, gameObject: Dict[str, Any]) -> None:
        self.grpId = gameObject.get('grpId')
        self.instanceId = gameObject.get('instanceId')
        self.owner = gameObject.get('ownerSeatId')
        self.controller = gameObject.get('controllerSeatId')
        self.visibility = gameObject.get('visibility')
        self.type = gameObject.get('type')
        self.zone = gameObject.get('zoneId')

        self.name = '' if 'name' not in gameObject else dh.loctext(gameObject.get('name'))
        
class Card(GameObject):
    cardTypes: List[str]
    color: List[str]

    def __init__(self, gameObject) -> None:
        GameObject.__init__(self, gameObject)
        self.cardTypes = gameObject.get('cardTypes')
        self.color = gameObject.get('color')
        

class Permanent(Card):
    isTapped: bool
    subtypes: List[str]
    supertypes: List[str]

    def __init__(self, gameObject) -> None:
        Card.__init__(self, gameObject)

        self.isTapped = gameObject.get('isTapped', False)
        self.subtypes = gameObject.get('subtypes', [])
        self.supertypes = gameObject.get('supertypes', [])

class Creature(Permanent):
    power: int
    toughness: int
    hasSummoningSickness: bool
    attackState: str

    def __init__(self, gameObject):
        Permanent.__init__(self, gameObject)

        self.power = gameObject.get('power').get('value') if 'power' in gameObject and 'value' in gameObject['power'] else 0
        self.toughness = gameObject.get('toughness').get('value') if 'toughness' in gameObject and gameObject and 'value' in gameObject['toughness'] else 0
        self.hasSummoningSickness = gameObject.get('hasSummoningSickness', False)
        self.attackState = gameObject.get('attackState', '')

class Land(Permanent):
    def __init__(self, gameObject):
        Permanent.__init__(self, gameObject)


class InstantSorcery(Card):
    def __init(self, gameObject):
        Card.__init__(self, gameObject)