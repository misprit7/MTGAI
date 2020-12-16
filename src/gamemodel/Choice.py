import gamecontroller as gc

class Choice:
    def __init__(self, choice):
        self.actionType = choice.get('actionType')

    def execute(self):
        pass



class Cast(Choice):
    def __init__(self, choice):
        Choice.__init__(self, choice)

        self.grpid = choice.get('grpId')
        self.instanceId = choice.get('instanceId')
        self.manaCost = choice.get('manaCost')

        self.shouldStop = choice.get('shouldStop')

    def execute(self):
        gc.playcard(self.instanceId)
        gc.stopindexing()

class Play(Choice):
    def __init__(self, choice):
        Choice.__init__(self, choice)

        self.grpid = choice.get('grpId')
        self.instanceId = choice.get('instanceId')

        self.shouldStop = choice.get('shouldStop')

    def execute(self):
        gc.playcard(self.instanceId)
        gc.stopindexing()

class Pass(Choice):
    def __init__(self, choice):
        Choice.__init__(self, choice)