
import pyautogui as ag, numpy as np
import time
# For OCR, see https://stackoverflow.com/questions/48118094/pytesseract-trying-to-detect-text-from-on-screen
# https://stackoverflow.com/questions/48928592/how-to-get-the-co-ordinates-of-the-text-recogonized-from-image-using-ocr-in-pyth
# pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'


def click():
    ag.mouseDown()
    time.sleep(0.1)
    ag.mouseUp()

def scroll(amount):
    for i in range(amount if amount > 0 else -amount):
        ag.scroll(5 if amount > 0 else -5)

def press(key):
    ag.keyDown(key)
    time.sleep(0.1)
    ag.keyUp(key)

def mreset():
    ag.moveTo(50, 540)

# From main screen, starts game
def startgame(mode):
    ag.moveTo(1730, 1000)
    click()
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

def locatecard(cardnum, cardpile, piles):
    edges = [(), (), (), (600, 1310), (515, 1400), (425, 1485), (335, 1575), (274, 1635)]

    edge = edges[piles[0] - 1]

    x = edge[0] + (edge[1] - edge[0]) / piles[0] * (cardnum + 0.5)

    return x

def playcard(cardnum, cardpile, piles):

    x = locatecard(cardnum, cardpile, piles)
    
    dragcard(x)

    mreset()

def selectcard(cardnum, cardpile, piles):

    x = locatecard(cardnum, cardpile, piles)

    ag.moveTo(x, 1900, duration=0.1)
    ag.click()

    mreset()

def dragcard(x):
    ag.moveTo(x, 1900, duration=0.1)
    ag.dragTo(960, 540, duration=0.3)

def passpriority():
    press('space')

def allattack():
    press('space')
    press('space')

def chooseoption(numoptions, choice):
    if numoptions == 2:
        ag.moveTo(1200 if choice == 2 else 720, 450, duration=0.1)
        click()

if __name__ == "__main__":
    startgame('bot')
    # openingHand(True)
    # selectcard(4, 0, [5])
    # time.sleep(3)
    # passpriority()
    # allattack()
    # playcard(4, 0, [5])
    # chooseoption(2, 2)