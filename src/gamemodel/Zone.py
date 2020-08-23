# Class representing game zone

class Zone:
    def __init__(self, zone):
        self.type = zone.get('type')
        self.visibility = zone.get('visibility')
        self.id = zone.get('zoneId')

        self.owner = zone.get('ownerSeatId')