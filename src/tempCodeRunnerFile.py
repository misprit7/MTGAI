turechoice = next(x for x in choices['actions'] if x['actionType'] == 'ActionType_Cast' and game.gameObject(x['grpId']).type == 'CardType_Creature')

        cardnum = next(i for i, x in enumerate(game.hand()) if x.grpId == creaturechoice['grpId'])

        prin