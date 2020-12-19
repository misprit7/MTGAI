
# Handles the interactions between AI and GUI

from typing import Dict, List, Tuple, Callable
import pyautogui as ag, numpy as np
import time, threading, sys, json, re
import ConfigHelper as config
from gamemodel import datahelper as dh
# For OCR, see https://stackoverflow.com/questions/48118094/pytesseract-trying-to-detect-text-from-on-screen
# https://stackoverflow.com/questions/48928592/how-to-get-the-co-ordinates-of-the-text-recogonized-from-image-using-ocr-in-pyth
# pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'

cards: Dict[int, Tuple[int, int]] = {}
indexing: bool = True
indexreset: bool = False
actionqueue: List[Callable] = []


###############################################################################
# Game level action functions
###############################################################################

# From main screen, starts game
def startgame(mode):
    ag.moveTo(1730, 1000)
    ag.click()
    time.sleep(0.3)
    if mode == 'bot':
        ag.moveTo(1730, 630, duration=0.1)
        scroll(-10)
        ag.moveRel(50, 5, duration=0.1)
        scroll(-20)
        ag.moveRel(-50, -5, duration=0.1)
        click()
    ag.moveTo(1730, 1000)
    click()

def openingHand(keep):
    if keep:
        ag.moveTo(1135, 870, duration=0.1)
    else:
        ag.moveTo(790, 870, duration=0.1)
    click()

def passpriority():
    press('space')

def allattack():
    press('space')
    press('space')

def chooseoption(numoptions, choice):
    if numoptions == 2:
        ag.moveTo(1200 if choice == 2 else 720, 450, duration=0.1)
        click()

def playcard(id):
    while id not in cards:
        time.sleep(0.1)
    # Wait for indexing to stop
    stopindexing()
    actionqueue.append(lambda: dragcard(cards[id]))

###############################################################################
# Basic Wrappers for PyAutoGUI functions
###############################################################################

def click():
    ag.mouseDown()
    time.sleep(0.1)
    ag.mouseUp()

# Have to scroll in chunks for arena to accept it
def scroll(amount):
    for i in range(amount if amount > 0 else -amount):
        ag.scroll(5 if amount > 0 else -5)

# Have to hold a bit for arena to accept it
def press(key):
    ag.keyDown(key)
    time.sleep(0.1)
    ag.keyUp(key)

# Consistent spot to reset mouse to
def mreset():
    ag.moveTo(50, 540)


def dragcard(pos):
    ag.moveTo(pos[0], pos[1], duration=0.1)
    ag.dragTo(960, 540, duration=0.3)

###############################################################################
# Indexing function
###############################################################################

def beginindexing():
    readthread = threading.Thread(target=readhovercards)
    hoverthread = threading.Thread(target=indexhover)

    readthread.start()
    hoverthread.start()

def stopindexing():
    indexing = False

def resetindexing():
    cards.clear()
    actionqueue.clear()
    resetindexing = True

def hoverover(zone):
    start = (0, 0)
    end = (0, 0)
    duration = 0
    if zone == dh.zones.hand:
        start = (10, 1079)
        end = (1920, 1079)
        duration = 4
    elif zone == dh.zones.battlefield:
        start = (10, 775)
        end = (1920, 775)
        duration = 4
    ag.moveTo(start[0], start[1])
    ag.click()
    ag.moveTo(end[0], end[1], duration=duration)

def indexhover():
    while True:
        for i in dh.zones:
            if indexing:
                hoverover(i)
            for action in actionqueue:
                action()
            actionqueue.clear()
            if resetindexing:
                break

def readhovercards():
    f = open(config.logpath)
    for line in f:
        f.readline()

    lastpnt = (0, 0)
    lastid = 0
    

    while indexing:
        where = f.tell()
        msg = f.read()
        if not msg:
            time.sleep(0.01)
            f.seek(where)
        else:
            try:
                # trans = json.loads(re.sub(r'^.*?{', '{', msg.replace('\n', ' ')))
                trans = json.JSONDecoder().raw_decode(re.sub(r'^.*?{', '{', msg.replace('\n', ' ')))[0]
                uiMessage = trans['payload']['uiMessage']['onHover']
                pos = ag.position()

                if 'objectId' in uiMessage:
                    id = uiMessage['objectId']
                    lastid = id
                    lastpnt = (pos[0], pos[1])
                else:
                    cards[lastid] = ((lastpnt[0] + pos[0])/2, (lastpnt[1] + pos[1])/2)
                    # print('New card. ID: ' + str(lastid) + '; pos: ' + str(cards[lastid]))

            except:
                # print("line parse failed")
                pass

if __name__ == "__main__":
    # startgame('bot')
    x = threading.Thread(target=readhovercards)
    x.start()
    hoverover(dh.zones.hand)
    hoverover(dh.zones.battlefield)
    print(cards)
