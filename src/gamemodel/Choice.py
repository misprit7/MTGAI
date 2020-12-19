from typing import Any, Dict, List
import gamecontroller as gc

class Choice:
    def __init__(self, choice: Dict[str, Any]) -> None:
        self.actionType = choice.get('actionType')

    def execute(self) -> None:
        pass



class Cast(Choice):
    grpid: int
    instanceId: int
    manaCost: List[Dict[str, Any]]
    shouldStop: bool

    def __init__(self, choice: Dict[str, Any]) -> None:
        Choice.__init__(self, choice)

        self.grpid = choice.get('grpId')
        self.instanceId = choice.get('instanceId')
        self.manaCost = choice.get('manaCost')

        self.shouldStop = choice.get('shouldStop')

    def execute(self):
        gc.playcard(self.instanceId)
        gc.stopindexing()

class Play(Choice):
    grpid: int
    instanceId: int
    shouldStop: bool

    def __init__(self, choice: Dict[str, Any]):
        Choice.__init__(self, choice)

        self.grpid = choice.get('grpId')
        self.instanceId = choice.get('instanceId')

        self.shouldStop = choice.get('shouldStop')

    def execute(self):
        gc.playcard(self.instanceId)

class Pass(Choice):
    def __init__(self, choice):
        Choice.__init__(self, choice)