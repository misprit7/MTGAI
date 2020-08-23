import sys
import gamecontroller as gc, logparser as lp
sys.path.append(r'./src/gamemodel')
import Game


def onchoice(gamestate, choices):
    game = Game.Game(gamestate)
    # print(choices)
    # print('\n')
    # print([x for x in gamestate['gameObjects'] if x['zoneId'] == game.zoneId('hand')])
    try:
        landchoice = next(x for x in choices['actions'] if x['actionType'] == 'ActionType_Play')

        cardnum = next(i for i, x in enumerate(game.hand()) if x.instanceId == landchoice['instanceId'])

        hand = game.hand()

        print('land: ' + str(landchoice['grpId']) + '; num: ' + str(cardnum))

        gc.playcard(cardnum, 0, [len(game.hand())])

        return
    except Exception as e:
        print('no land to play: ')
        print(e)

    # try:
    # print(next(game.gameObject(x['grpId']).type for x in choices['actions'] if x['actionType'] == 'ActionType_Cast'))
    creaturechoice = next(x for x in choices['actions'] if x['actionType'] == 'ActionType_Cast' and 'CardType_Creature' in game.gameObject(x['instanceId']).cardTypes)

    print('creature: ' + str(creaturechoice['instanceId']))

    cardnum = next(i for i, x in enumerate(game.hand()) if x.instanceId == creaturechoice['instanceId'])

    print('creature: ' + str(creaturechoice['grpId']) + '; num: ' + str(cardnum))

    gc.playcard(cardnum, 0, [len(game.hand())])

    return
    # except:
    #     print('no creature to play')
    
    # print('passing...')
    # gc.passpriority()
    # print([Game.dh.name(x['grpId']) for x in choices['actions'] if x['actionType'] == 'ActionType_Play'])
    # print([x['actionType'] for x in choices['actions']])

if __name__ == '__main__':
    # gc.startgame('bot')
    lp.parseGame(onchoice = onchoice, onperiod = print('finished'), period = 10, live = True)