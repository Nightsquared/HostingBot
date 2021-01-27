import discord
import random
from Functions import botadmin
import nest_asyncio as sy
from pynput.keyboard import Key, Controller

keyboard = Controller()

time = 1
currentbutton = ''
running = False
commandnum = 0


async def ControlRespond(messagearray, message):
    global time, currentbutton, running
    if botadmin(message.author):
        if messagearray[1].lower() == 'running':
            running = not running
            return
        elif messagearray[1].lower() == 'time':
            time = float(messagearray[2])
            return
    if running:
        await buttonpress(messagearray, message)

async def buttonpress(messagearray, message):
    global time, currentbutton, running, keyboard, commandnum
    commandnum += 1
    thiscommandnum = commandnum
    lastbutton = currentbutton
    currentbutton = messagearray[1].lower()
    try:
        t = int(messagearray[2])
    except:
        t = time
    if currentbutton == 'space':
        currentbutton = Key.space
    elif currentbutton == 'left':
        currentbutton = Key.left
    elif currentbutton == 'right':
        currentbutton = Key.right
    elif currentbutton == 'down':
        currentbutton = Key.down
    elif currentbutton == 'up':
        currentbutton = Key.up
    elif currentbutton == 'shift':
        currentbutton = Key.shift
    elif currentbutton == 'ctrl':
        currentbutton = Key.ctrl_l
    elif currentbutton == 'enter':
        currentbutton = Key.enter
    try:
        #keyboard.release(lastbutton)
        pass
    except:
        print('test2')
    try:
        keyboard.press(currentbutton)
        await sy.asyncio.sleep(t)
        if thiscommandnum == commandnum:
            keyboard.release(currentbutton)
            print('test')
    except:
        pass

        # keyboard.press('w')
        # await sy.sleep(3)
        # keyboard.release('w')