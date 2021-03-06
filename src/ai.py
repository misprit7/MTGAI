# Intelligence behind game decisions
#
# Note that this is heavily WIP right now, so it's pretty much all test stuff for the moment

import sys
import time


sys.path.append(r"./src/gamemodel")
import Game
import gamecontroller as gc
import datahelper as dh
import ConfigHelper as config
from Choice import Cast, DeclareBlockers, Pass, Play, DeclareAttackers
from GameObject import Creature


def playLand(game: Game) -> bool:
    try:
        playchoice = next(x for x in game.choices if isinstance(x, Play))
        playchoice.execute()
        print("Playing land...")
        return True
    except:
        return False


def playCreature(game: Game) -> bool:
    try:
        playchoice = sorted(
            [
                x
                for x in game.choices
                if isinstance(x, Cast)
                and "CardType_Creature" in game.gameObject(x.instanceId).cardTypes
                and x.hasAutoTap == True
            ],
            key=lambda x: sum(y["count"] for y in x.manaCost),
            reverse=True,
        )[0]
        print("Playing creature...")
        playchoice.execute()
        return True
    except:
        return False


def passTurn(game: Game) -> bool:
    try:
        playchoice = next(x for x in game.choices if isinstance(x, Pass))
        print("Passing...")
        playchoice.execute()
        return True
    except:
        return False


def attackAll(game: Game) -> bool:
    try:
        choice = next(x for x in game.choices if isinstance(x, DeclareAttackers))
        print("Attacking...")
        choice.attackers = choice.qualifiedAttackers
        choice.execute()
        return True
    except:
        return False


def blockNone(game: Game) -> bool:
    try:
        choice = next(x for x in game.choices if isinstance(x, DeclareBlockers))
        print("Blocking...")
        choice.execute()
        return True
    except:
        return False


if __name__ == "__main__":
    game = Game.Game(config.logpath)
    gc.beginindexing()
    while 1:
        if game.update() and game.turnInfo["decisionPlayer"] == game.curPlayer:
            gc.resetindexing()
            if (
                not playLand(game)
                and not playCreature(game)
                and not passTurn(game)
                and not attackAll(game)
                and not blockNone(game)
            ):
                print("No action available!")
        time.sleep(1)
