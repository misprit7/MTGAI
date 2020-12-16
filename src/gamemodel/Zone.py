# Class representing game zone

class Zone:
    type: str
    visibility: str
    id: int
    owner: int

    def __init__(self, zone) -> None:
        self.type = zone.get('type')
        self.visibility = zone.get('visibility')
        self.id = zone.get('zoneId')

        self.owner = zone.get('ownerSeatId')