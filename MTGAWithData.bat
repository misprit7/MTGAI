@echo off
copy "C:\Users\xander\AppData\LocalLow\Wizards Of The Coast\MTGA\Player.log" ".\data\%DATE%-%TIME:~0,2%-%TIME:~3,2%.log"
"C:\Program Files\Wizards of the Coast\MTGA\MTGALauncher\MTGALauncher.exe"