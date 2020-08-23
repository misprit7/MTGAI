import datahelper as dh

class GameObject:
    def __init__(self, gameObject):
        self.grpId = gameObject.get('grpId')
        self.instanceId = gameObject.get('instanceId')
        self.owner = gameObject.get('ownerSeatId')
        self.controller = gameObject.get('controllerSeatId')
        self.visibility = gameObject.get('visibility')
        self.type = gameObject.get('type')
        self.zone = gameObject.get('zoneId')
        self.name = dh.namefromtitleid(gameObject.get('name'))
        
class Card(GameObject):
    def __init__(self, gameObject):
        GameObject.__init__(self, gameObject)
        self.cardData = [x for x in dh.cards if x['grpid'] == gameObject['grpId']][0]
        self.cardTypes = gameObject.get('cardTypes')
        self.color = gameObject.get('color')
        

class Permanent(Card):
    def __init__(self, gameObject):
        Card.__init__(self, gameObject)

        self.isTapped = gameObject.get('isTapped') if 'isTapped' in gameObject else False
        self.subtypes = gameObject.get('subtypes') if 'subtypes' in gameObject else []
        self.supertypes = gameObject.get('supertypes') if 'supertypes' in gameObject else []

class Creature(Permanent):
    def __init__(self, gameObject):
        Permanent.__init__(self, gameObject)

        self.power = gameObject.get('power').get('value') if 'power' in gameObject and 'value' in gameObject['power'] else 0
        self.toughness = gameObject.get('toughness').get('value') if 'toughness' in gameObject and gameObject and 'value' in gameObject['toughness'] else 0
        self.hasSummoningSickness = gameObject.get('hasSummoningSickness') if 'hasSummoningSickness' in gameObject else False
        self.attackState = gameObject.get('attackState') if 'attackState' in gameObject else ""

class Land(Permanent):
    def __init__(self, gameObject):
        Permanent.__init__(self, gameObject)


class InstantSorcery(Card):
    def __init(self, gameObject):
        Card.__init__(self, gameObject)