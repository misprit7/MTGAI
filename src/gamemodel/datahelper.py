# Helper module to get data and parse names, etc.
# Note that most of this code was stolen from the python-mtga module

# The main part of this module is cards, loc and enum
# These are all retrieved from the local machine where mtga holds them to keep up to date
# cards is a list of all mtga cards with attributes
# loc is a dictionary relating text ids with text
# enums is a list of dictionaries associating misc. attributes with their ids

import json, os, sys
from enum import Enum
from pathlib import Path
from typing import Dict

def _get_data_location_hardcoded() -> str:
    root: str = os.environ.get(
        "ProgramFiles",
        r"C:\Program Files"
    )
    return os.path.join(root, "Wizards of the Coast", "MTGA", "MTGA_Data", "Downloads", "Data")

def get_data_location() -> str:
    current_os: str = sys.platform

    return {
        "darwin": get_darwin_data_location,
        "win32": get_win_data_location,
    }[current_os]()

def get_darwin_data_location() -> str:
    return os.path.join(
        os.path.expanduser("~"),
        "Library/Application Support/com.wizards.mtga/Downloads/Data",
    )

def get_win_data_location() -> str:
    try:
        from winreg import ConnectRegistry, OpenKey, HKEY_LOCAL_MACHINE, QueryValueEx
        registry_connection = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        reg_path = r"SOFTWARE\Wizards of the Coast\MTGArena"
        registry_key = OpenKey(registry_connection, reg_path)
        data_location = QueryValueEx(registry_key, "Path")[0] + r"MTGA_Data\Downloads\Data"
        print("Found data @ ")
        print(data_location)
        print(r"C:\Program Files\Wizards of the Coast\MTGA\MTGA_Data\Downloads\Data")
    except:
        print("Couldn't locate MTGA from registry, falling back to hardcoded path...")
        data_location = _get_data_location_hardcoded()
    return data_location

# def getMtgaData():
data_location: str = get_data_location()

json_filepaths: Dict[str, str] = {"enums": "", "cards": "", "abilities": "", "loc": ""}

# A newer file SHOULD be the preference; alpha sort of hashes may be out of order
# Otherwise it will be necessary to find which is really used
for filepath in sorted(Path(data_location).iterdir(), key=os.path.getmtime):
    filename = os.path.basename(filepath)
    # In case of rogue files
    filesplit = filename.split("_")
    if len(filesplit) > 1:
        key = filesplit[1]
    else:
        key = ""
    if key in json_filepaths.keys() and filename.endswith("mtga"):
        # print("setting {} to {}".format(key, filename))
        json_filepaths[key] = filepath

with open(json_filepaths["cards"], "r", encoding="utf-8") as card_in:
    cards = json.load(card_in)

with open(json_filepaths["loc"], "r", encoding="utf-8") as loc_in:
    loc = json.load(loc_in)[0]['keys']

with open(json_filepaths["enums"], "r", encoding="utf-8") as enums_in:
    enums = json.load(enums_in)


# Helper functions, name pretty much describes them
def namefromgrpid(grpid: int) -> str:
    return loctext([x['titleId'] for x in cards if x['grpid'] == grpid][0])

def loctext(id: str) -> str:
    return next(x['text'] for x in loc if x['id'] == id)

def cmcfromgrpid(grpid: int) -> int:
    return next(x['cmc'] for x in cards if x['grpid'] == grpid)


# Constants
keyid: Dict[str, str] = {
    'actions': 'instanceId', 
    'annotations': 'id', 
    'gameObjects': 'instanceId',
    'players': 'controllerSeatId', 
    'teams': 'id', 
    'timers': 'timerId', 
    'zones': 'zoneId'
}

zones = Enum('zone', 'hand battlefield graveyard library')
