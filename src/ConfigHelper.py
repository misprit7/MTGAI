import json, os

config = {}

try:
    f = open('./config.json')
    config = json.load(f)
    f.close()
except:
    pass

playername = config.get('playername', '_rednax_#30532')
logpath = os.path.expandvars(config.get('logpath', '%APPDATA%/../LocalLow/Wizards Of The Coast/MTGA/')) + 'Player.log'