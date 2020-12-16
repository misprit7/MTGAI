# 
# https://github.com/mtgatool/mtgatool-metadata
# https://github.com/mtgatracker/python-mtga
# https://github.com/mtgatool/mtgatool-metadata
# 
# 
# 
# 
# 
# 
# 

# config variables
playername = '_rednax_#30532'
logpath = "C:\\Users\\xander\\AppData\\LocalLow\\Wizards Of The Coast\\MTGA\\Player.log"

import json, time, re, sys
sys.path.append(r'./src/gamemodel')
import datahelper as dh

# Variable to keep track of the hand order
# MTGA mixes up the hand order every time, so a consistently ordered array is necessary
# Note that in python globals are restricted to the module, so this isn't as bad practice as it looks (although it's still not great)
handorder = []

# Returns (messagetype, choices) where messagetype is an array of the messages and choices is an array of possible choices to make
def parseLine(gamestate, line):

    transtypes = []
    choices = None

    # Check if line is a semi-valid json
    if line.__contains__("{") and line.__contains__("}") and re.sub(r'^.*?{', '{', line):
        # Load json
        try:
            trans = json.loads(re.sub(r'^.*?{', '{', line))
        except ValueError as identifier:
            # if line.__contains__("{"):
            #     print(identifier)
            #     print(lnum)
            return ([], None)

        # Handle different message types
        if 'greToClientEvent' in trans and 'greToClientMessages' in trans['greToClientEvent']:
            msgs = trans['greToClientEvent']['greToClientMessages']
            for msg in msgs:
                # print(msg['msgId'])
                if msg['type'] == 'GREMessageType_GameStateMessage':
                    # if msg['gameStateMessage']['type'] == "GameStateType_Full":
                    # Update game state based on message
                    updateGameState(gamestate, msg['gameStateMessage'])

                    # Order cards in hand on mulligan decision
                    try:
                        if  msg['gameStateMessage']['players'][gamestate['curPlayer']]['pendingMessageType'] == 'ClientMessageType_MulliganResp':
                            handid = next(x['zoneId'] for x in gamestate['zones'] if x['type'] == 'ZoneType_Hand' and x['ownerSeatId'] == gamestate['curPlayer'])
                            cards = [x['instanceId'] for x in gamestate['gameObjects'] if x['zoneId'] == handid]
                            gamestate['cardOrder'] = sorted(cards, key=lambda x: (dh.cmcfromgrpid(grpidfrominstanceid(gamestate, x)), dh.namefromgrpid(grpidfrominstanceid(gamestate, x))))
                    except Exception as e:
                        # print(e)
                        pass

                elif msg['type'] == 'GREMessageType_ActionsAvailableReq':
                    # Update choices based on choices available
                    choices = msg['actionsAvailableReq']
                transtypes.append(msg['type'])

        # Signals beginning of game, important to establish which player is player 1 vs 2
        elif 'matchGameRoomStateChangedEvent' in trans:
            gamestate.clear()
            players = trans['matchGameRoomStateChangedEvent']['gameRoomInfo']['gameRoomConfig'].get('reservedPlayers')
            if players:
                # playername is configured above to be the name of the mtga player
                gamestate['curPlayer'] = [x['teamId'] for x in players if x['playerName'] == playername][0]

            transtypes.append('gameRoomInfo')
    
    return (transtypes, choices)


# updates the gamestate based on the message
# extras signifies whether to include annotations and actions
def updateGameState(gamestate, msg, extras = False):
    keys = msg.keys()
    for key in keys:
        # Make sure not taking data from misc. header info
        if key == 'type' or key == 'msgId':
            continue
        # Exclude actions and annotations if not wanted
        elif not extras and (key == 'actions' or key == 'annotations'):
            continue
        # If random header information log it and continue
        elif type(msg[key]) != dict and type(msg[key]) != list:
            gamestate[key] = msg[key]
            continue
        # Initialize new keys
        if key not in gamestate and key != 'diffDeletedInstanceIds':
            gamestate[key] = msg[key]

        if key != "diffDeletedInstanceIds":
            # Dicts are easy since they just get updated
            if type(msg[key]) == dict:
                gamestate[key].update(msg[key])
            else:
                # Initialize the 'id' for each of the different arrays, which may look slightly different on which is in question
                updated = False
                id = ''
                if key == 'actions':
                    id = 'instanceId'
                elif key == 'annotations':
                    id = 'id'
                elif key == 'gameObjects':
                    id = 'instanceId'
                elif key == 'players':
                    id = 'controllerSeatId'
                elif key == 'teams':
                    id = 'id'
                elif key == 'timers':
                    id = 'timerId'
                elif key == 'zones':
                    id = 'zoneId'
                # This effectively updates the old list by replacing old items with the new ones but appending completely new keys
                for new in msg[key]:
                    for k in range(len(gamestate[key])):
                        if key != 'actions':
                            if gamestate[key][k][id] == new[id]:
                                # Still not sure if it's better to update or replace here
                                # TODO: Test further
                                gamestate[key][k] = new  #.update(new)
                                updated = True
                                break
                        else:
                            # This whole section is a bit weird
                            # TODO: Clean this up
                            # For some reason some random ability actions don't have an instanceId
                            if id not in new['action'] or id:
                                break
                            elif id not in gamestate[key][k]['action']:
                                continue
                            if gamestate[key][k]['action'][id] == new['action'][id]:
                                gamestate[key][k].update(new)
                                updated = True
                                break
                    # If key has not been used already, append it as a new one
                    if not updated:
                        gamestate[key].append(new)
                    else:
                        updated = False
        else:
            # Get rid of all of the deleted gameObjects and actions
            try:
                gamestate['gameObjects'] = [x for x in gamestate['gameObjects'] if x['instanceId'] not in msg[key]]
                gamestate['actions'] = [x for x in gamestate['actions'] if 'instanceId' in x['action'] and x['action']['instanceId'] not in msg[key]]
            except:
                pass

# Pretty prints json object
def pp(obj):
    return json.dumps(obj, sort_keys=True, indent=4)

def writeGameStateFile(gamestate, filename):
    f = open(filename, "w")
    n = f.write(json.dumps(gamestate, sort_keys=True, indent=4))

    print('Successfully wrote ' + str(n) + ' characters to ' + filename)
    f.close()

def grpidfrominstanceid(gamestate, instanceId):
    return next(x['grpId'] for x in gamestate['gameObjects'] if x['instanceId'] == instanceId)


def parseFile(filename, type):
    f = open(filename)
    gamestate = {}
    for line in f:
        parseLine(gamestate, line)
    f.close()
    # print(json.dumps(gamestate, sort_keys=True, indent=4))
    # for x in [x for x in gamestate['gameObjects'] if x['zoneId'] == 28]:
    #     pp(x)
    # print(len([x for x in gamestate['gameObjects'] if x['zoneId'] == 28]))
    if type == 'w':
        writeGameStateFile(gamestate, './data/gamestate{}.json'.format(int(time.time())))
    elif type == 'r':
        return gamestate

def parseGame(onupdate = None, onchoice = None, onperiod = None, period = None, live = True):
    f = open(logpath)
    gamestate = json.loads("{}")
    
    lastprint = time.time()
    islive = False

    while 1:
        where = f.tell()
        line = f.readline()
        if not line:
            islive = True
            time.sleep(0.1)
            if 'gameObjects' in gamestate and time.time() - lastprint > period:
                lastprint = time.time()
                if onperiod:
                    onperiod(gamestate)
            
            f.seek(where)
        else:
            (msgs, choices) = parseLine(gamestate, line)
            if not live or islive:
                if 'GREMessageType_GameStateMessage' in msgs and onupdate:
                    onupdate(gamestate)
                if choices:
                    onchoice(gamestate, choices)


if __name__ == "__main__":
    
    gamestate = parseFile(logpath, 'r')
    print(gamestate)
    # parseGame(None, printCards, 10)
elif __name__ == "logparser":
    # gamestate = parseFile("C:\\Users\\Kids\\AppData\\LocalLow\\Wizards Of The Coast\\MTGA\\Player.log", 'r')
    pass