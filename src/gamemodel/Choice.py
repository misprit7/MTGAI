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
    hasAutoTap: bool

    def __init__(self, choice: Dict[str, Any]) -> None:
        Choice.__init__(self, choice)

        self.grpid = choice.get('grpId')
        self.instanceId = choice.get('instanceId')
        self.manaCost = choice.get('manaCost')
        self.hasAutoTap = 'autoTapSolution' in choice

        self.shouldStop = choice.get('shouldStop')

    def execute(self):
        gc.playcard(self.instanceId)

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
    
    def execute(self):
        gc.passpriority()
        
class DeclareAttackers(Choice):
    attackerId: int
    attackers: List[int]
    qualifiedAttackers: List[int]

    def __init__ (self, msg: Dict[str, Any]) -> None:
        self.actionType = 'ActionType_DeclareAttackers'
        self.attackerId = msg.get('systemSeatIds')[0]
        self.attackers = [x['attackerInstanceId'] for x in msg.get('declareAttackersReq').get('attackers')]
        self.qualifiedAttackers = [x['attackerInstanceId'] for x in msg.get('declareAttackersReq').get('qualifiedAttackers')]
    
    def execute(self):
        gc.allattack()
        
class DeclareBlockers(Choice):
    blockerId: int
    blockers: Dict[str, Any]

    def __init__ (self, msg: Dict[str, Any]) -> None:
        self.actionType = 'ActionType_DeclareBlockers'
        self.blockerId = msg.get('systemSeatIds')[0]
        self.blockers = msg.get('declareBlockersReq').get('blockers')

    def execute(self):
        gc.passpriority()
