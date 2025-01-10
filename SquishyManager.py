# Import OS Functions
import os
import subprocess
import pickle
from pathlib import Path
from datetime import datetime
from os import system, name

# Define Constants
USER_DIR = str(Path.home())
SAVE_DIR = "SquishyCoopManager.pik"
VERSION = "v1 (In-Dev)"
APPDATA_DIR = USER_DIR + "\\AppData\\Roaming\\sm64coopdx\\mods"
DATE = datetime.now().strftime("%m/%d/%Y")

def clear(header):
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')
        
    if header:
        # Header
        header = "Squishy CoopDX Manager " + VERSION + " - " + DATE
        headerBreak = ""
        while len(headerBreak) < len(header):
            headerBreak = headerBreak + "-"
        print(headerBreak)
        print(header)
        print(headerBreak)
        print()

def read_or_new_pickle(path, default):
    if os.path.isfile(path):
        with open(path, "rb") as f:
            try:
                return pickle.load(f)
            except Exception: # so many things could go wrong, can't be more specific.
                pass 
    with open(path, "wb") as f:
        pickle.dump(default, f)
    return default

coopDir = read_or_new_pickle(SAVE_DIR, USER_DIR + '\\Downloads\\sm64coopdx\\sm64coopdx.exe')

def config_coop_dir():
    print("Please enter a new Directory to use for CoopDX")
    while(True):
        inputDir = input()
        print(inputDir)
        if os.path.isfile(inputDir):
            pickle.dump(coopDir, open(SAVE_DIR, "wb"))
            return inputDir
        else:
            print("Directory not found, please enter a valid directory")

# Main Options
while(True):
    clear(True)
    print("Main Options:")
    print("1. Open SM64CoopDX")
    print("2. Configure Directory")
    print("3. Mod Options")
    print("4. Close Program")

    prompt1 = input()
    if prompt1 == "1": # Open Coop
        while(True):
            clear(True)
            if os.path.isfile(coopDir):
                print("Opening from Directory: '" + coopDir + "'")
                os.startfile(coopDir)
                break
            else:
                print("CoopDX not found at Directory '" + coopDir + "'")
                coopDir = config_coop_dir()
        break
    if prompt1 == "2": # Set Coop Directory
        config_coop_dir()
    if prompt1 == "3": # Mod Options
        clear(True)
        if not os.path.isdir(APPDATA_DIR):
            print("Appdata Directory does not exist, please open CoopDX first!")
            input("Press Enter to return to Main Options")
            clear(False)
        else:
            print("Mod Options:")
            print("1. Open Mods Folder (Appdata)")
            print("2. Load Mods Folder")
            print("3. Backup and Clear Mods Folder")
            print("4. Back")

            while(True):
                prompt2 = input()
                if prompt2 == "1":
                    os.startfile(APPDATA_DIR)
                if prompt2 == "4":
                    break
    if prompt1 == "4": # Exit
        break
clear(False)
exit()