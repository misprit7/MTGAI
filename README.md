# MTGAI

This is a project to make a functional AI to parse, decide and execute decisions on the game Magic the Gathering Arena. 

## Architecture

This project is essentially split up into 4 main sections: log parsing, controlling the game UI, game logic and AI. Parsing logs give information about the full game state at every point, the AI uses the built in game logic to makes a decision based on this information and the game controller actually carries it out. 

### Log Parsing

Parsing the logs is described [here](./doc/log-messages.md). These logs are always here: 

```
%APPDATA%\..\LocalLow\Wizards Of The Coast\MTGA\Player.log
```

### Game Logic

For the AI to be able to make it's decision, the program must have an understanding of decisions in a game of Magic change future events. This is accomplished by essentially running a full rules engine to decide where events take the game state. This is done in the gamemodel directory. The `Game` class encapsulates a game at a given state and is derived from the game state modeled above. 

### AI

The AI actually makes the decisions regarding game actions. Not too much has been done on this yet, to be written later. 

### Game Controller

Once the AI has made a decision the program must interact with the GUI to actually carry it out. This is done through pyautogui, a python library that can click, drag and type as if a person on the computer was. This is interacts with the UI to make the appropriate action. 

## Setup for Dev

### Virtual Environment
Use a virtual environment for development. This is used to keep package versions consistent. To install this feature, run the following: 

```
pip install virtualenv
```

To set up, run the following in the main directory: 
```
python -m venv env
source env/bin/activate (Linux) or ./env/Scripts/activate (Windows)
pip install -r requirements.txt
```
In the future to enter the virtual environment use `source env/bin/activate` or `./env/Scripts/activate.` To exit virtual environment, just type `deactivate.` 

### Config file
Make a file called config.json in root path. Format as follows with your respective username and logpaths (otherwise defaults to values shown): 
```
{
    "playername": "_rednax_#30532", 
    "logpath": "%APPDATA%/../LocalLow/Wizards Of The Coast/MTGA/"
}
```