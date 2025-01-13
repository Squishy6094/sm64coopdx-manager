# Import OS Functions
import os
import sys
import subprocess
import glob
import time
import stat
import shutil
import pickle
from pathlib import Path
from datetime import datetime
import platform

# Define Constants
NAME_SM64COOPDX = "SM64CoopDX"
NAME_MANAGER = "Squishy " + NAME_SM64COOPDX + " Manager"
NAME_MAIN_MENU = "Main Options"
NAME_MODS_MENU = "Mod Options"
NAME_MANAGER_OPTIONS = "Manager Options"
NAME_FOLDER_OPTIONS = "Mod Folder Toggles"
VERSION = "1 (In-Dev)"
DATE = datetime.now().strftime("%m/%d/%Y")
PLATFORM_WINDOWS = "Windows"
PLATFORM_LINUX = "Linux"

# Define Constant Paths
USER_DIR = str(Path.home()).replace("\\", "/")
SAVE_DIR = "SquishyCoopManager.pickle"
def get_appdata_dir():
    systemName = platform.system()
    generalAppdata = ""

    # Get Platform's Appdata Folder
    if systemName == PLATFORM_LINUX:
        generalAppdata = USER_DIR + "/.local/share/"
    else:
        generalAppdata = USER_DIR + "/AppData/Roaming/"

    # Get Appdata folder for Coop
    if os.path.isdir(generalAppdata + "sm64ex-coop"):
        return generalAppdata + "sm64ex-coop"
    else:
        return generalAppdata + "sm64coopdx"

APPDATA_DIR = get_appdata_dir()
MANAGED_MODS_DIR = APPDATA_DIR + "/managed-mods"
if not os.path.isdir(MANAGED_MODS_DIR):
   os.makedirs(MANAGED_MODS_DIR)

def read_or_new_pickle(path, default):
    if os.path.isfile(path):
        with open(path, "rb") as f:
            try:
                return pickle.load(f)
            except Exception:
                pass 
    with open(path, "wb") as f:
        pickle.dump(default, f)
    return default

from fnmatch import filter

def include_patterns(*patterns):
    def _ignore_patterns(path, names):
        keep = set(name for pattern in patterns
                            for name in filter(names, pattern))
        ignore = set(name for name in names
                        if name not in keep and not os.path.isdir(os.path.join(path, name)))
        return ignore
    return _ignore_patterns

# Save Data
saveData = {
    "coopDir": (USER_DIR + '/Downloads/sm64coopdx/sm64coopdx.exe'),
    "autoBackup": True,
}
saveDataPickle = read_or_new_pickle(SAVE_DIR, saveData)
for s in saveDataPickle:
    saveData[s] = saveDataPickle[s]

def save_field(field, value):
    saveData[field] = value
    with open(SAVE_DIR, "wb") as f:
        pickle.dump(saveData, f)
    return value
   
def clear(header):
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux
    else:
        _ = os.system('clear')
        
    if header: # Header
        header = NAME_MANAGER + " v" + VERSION + " - " + DATE
        headerBreak = ""
        while len(headerBreak) < len(header):
            headerBreak = headerBreak + "-"
        print(headerBreak)
        print(header)
        print(headerBreak)
        print()

def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

def unhide_tree(inputDir):
    for root, dirs, files in os.walk(inputDir):  
        for dir in dirs:
            os.chmod(os.path.join(root, dir), stat.S_IRWXU)
        for file in files:
            os.chmod(os.path.join(root, file), stat.S_IRWXU)    

def backup_mods(wipeModFolder):
    if (not os.path.isdir(APPDATA_DIR)):
        return
    print("Ensuring " + NAME_SM64COOPDX + "'s Mods are moveable...")
    unhide_tree(APPDATA_DIR + "/mods")
    # unhide_tree(MANAGED_MODS_DIR)
    if os.path.isdir(APPDATA_DIR + "/mods"):
        #print("Cleaning old Backups...")
        #shutil.rmtree(MANAGED_MODS_DIR + "/backup", ignore_errors=True)
        print("Backing up " + NAME_SM64COOPDX + "'s Mods Folder...")
        shutil.copytree(APPDATA_DIR + "/mods", MANAGED_MODS_DIR + "/backup", dirs_exist_ok=True)
        if wipeModFolder:
            print("Cleaning " + NAME_SM64COOPDX + "'s Mods Folder...")
            shutil.rmtree(APPDATA_DIR + "/mods", ignore_errors=True, onerror=del_rw)

clear(True)
backup_mods(False)

def get_mod_folders():
    modFolders = []
    for (dirpath, dirnames, filenames) in os.walk(MANAGED_MODS_DIR):
        modFolders.extend(dirnames)
        return modFolders

def load_mod_folders():
    if not os.path.isdir(APPDATA_DIR):
        return
    print("Loading mods...")
    print("Ensuring " + NAME_MANAGER + "'s Mods are moveable...")
    # unhide_tree(APPDATA_DIR + "/mods")
    unhide_tree(MANAGED_MODS_DIR)
    if saveData["autoBackup"]:
        backup_mods(True)
    else:
        print("Cleaning " + NAME_SM64COOPDX + "'s Mods Folder...")
        shutil.rmtree(APPDATA_DIR + "/mods", ignore_errors=True, onerror=del_rw)
    mods = get_mod_folders()
    for s in saveData:
        for f in mods:
            if s == ("mods-" + f) and saveData[s] == True:
                print("Cloning " + f + " to " + NAME_SM64COOPDX + "'s Mods Folder")
                shutil.copytree(MANAGED_MODS_DIR + "/" + f, APPDATA_DIR + "/mods",
                    ignore=include_patterns('*.lua', '*.luac',
                                            '*.bin', '*.col', '*.c', '*.h',
                                            '*.bhv'
                                            '*.mp3', '*.ogg', '*.m64', '*.aiff'
                                            '*.lvl',
                                            '*.png', '*.tex'), dirs_exist_ok=True)
                break

def folder_from_file_dir(filename):
    filename = filename.replace("\\", "/")
    splitDir = filename.split("/")
    dirCount = 0
    returnString = ""
    for x in splitDir:
        dirCount = dirCount + 1
        if dirCount < len(splitDir):
            returnString = returnString + x + "/"
    return returnString

def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        subprocess.call(filename, cwd=folder_from_file_dir(filename))

        
def open_folder(foldername):
    if sys.platform == "win32":
        os.startfile(foldername)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, foldername],)

def boot_coop():
    coopDirectory = saveData["coopDir"]
    print("Standard Boot:")
    load_mod_folders()
    print("Booting " + NAME_SM64COOPDX + " from Directory: '" + coopDirectory + "'")
    open_file(coopDirectory)


def config_coop_dir():
    print("Please enter a new Directory to use for " + NAME_SM64COOPDX)
    print("(Type 'back' to return to " + NAME_MAIN_MENU + ")")
    while(True):
        inputDir = input()
        if os.path.isfile(inputDir):
            return inputDir
        elif inputDir == "back":
            break
        else:
            print("Directory not found, please enter a valid directory")

# Main Options
while(True):
    clear(True)
    print(NAME_MAIN_MENU + ":")
    print("1. Open " + NAME_SM64COOPDX)
    print("2. Mod Options")
    print("3. Manager Options")
    print("4. Close Program")

    prompt1 = input()
    if prompt1 == "1": # Open Coop
        while(True):
            clear(True)
            if os.path.isfile(saveData["coopDir"]):
                boot_coop()
                break
            else:
                print(NAME_SM64COOPDX + " not found at Directory '" + saveData["coopDir"] + "'")
                config = config_coop_dir()
                if config != None:
                    saveData["coopDir"] = save_field("coopDir", config)
                    clear(True)
                    boot_coop()
                    break
                else:
                    break
    if prompt1 == "2": # Mod Options
        while(True):
            clear(True)
            if not os.path.isdir(APPDATA_DIR):
                print("Appdata Directory does not exist, please open " + NAME_SM64COOPDX + " first!")
                input("Press Enter to return to Main Options")
                clear(False)
            else:
                print(NAME_MODS_MENU + ":")
                print("1. Configure Loaded Mod Folders")
                print("2. Backup and Clear Mods Folder")
                print("3. Open Appdata")
                print("4. Back")

            prompt2 = input()
            if prompt2 == "1": # Mod Folder Config
                while(True):
                    clear(True)
                    print(NAME_FOLDER_OPTIONS + ":")
                    #oldstr.replace("M", "")
                    mods = get_mod_folders()
                    modNum = 0
                    for x in mods:
                        modOnOff = False
                        modNum = modNum + 1
                        try:
                            modOnOff = saveData["mods-" + x]
                        except:
                            saveData["mods-" + x] = save_field("mods-" + x, True)
                            modOnOff = True
                        spacing = " "
                        while len(spacing) < 25 - (len(x) + 2):
                            spacing = spacing + "."
                        spacing = spacing + " "
                        print(str(modNum) + ". " + x + spacing + ("(O) Enabled" if modOnOff else "(X) Disabled"))
                    print()
                    print("Type a Folder's Name or it's Number to Toggle it")
                    print("Type 'all' to Enable all Folders")
                    print("Type 'none' to Disable all Folders")
                    print("Type 'back' to return to " + NAME_MODS_MENU)
                    prompt3 = input()
                    if prompt3 == "all":
                        for x in mods:
                            save_field("mods-" + x, True)
                    if prompt3 == "none":
                        for x in mods:
                            save_field("mods-" + x, False)
                    if prompt3 == "back" or prompt3 == "":
                        clear(True)
                        load_mod_folders()
                        break
                    modNum = 0
                    for x in mods:
                        modNum = modNum + 1
                        modNumString = str(modNum)
                        if prompt3 == modNumString or prompt3.lower() == x.lower():
                            modOnOff = False
                            try:
                                modOnOff = saveData["mods-" + x]
                            except:
                                modOnOff = True
                            save_field("mods-" + x, (not modOnOff))
            if prompt2 == "2": # Backup and Clear Mods
                backup_mods(True)
                break
            if prompt2 == "3": # Open Appdata
                open_folder(APPDATA_DIR)
            if prompt2 == "4": # Back
                break
    if prompt1 == "3": # Manager Options
        while(True):
            clear(True)
            print(NAME_MANAGER_OPTIONS + ":")
            print("1. Configure Directory")
            print("2. Toggle Auto-Backup (" + str(saveData["autoBackup"]) + ")")
            print("3. " + NAME_MANAGER + " Info")
            print("4. Back")

            prompt2 = input()
            if prompt2 == "1": # Set Coop Directory
                clear(True)
                while(True):
                    config = config_coop_dir()
                    if config != None:
                        saveData["coopDir"] = save_field("coopDir", config)
                        break
                    else:
                        break
            if prompt2 == "2": # Set Coop Directory
                saveData["autoBackup"] = save_field("autoBackup", not saveData["autoBackup"])
            if prompt2 == "3": # Squishy Manager Info
                clear(True)
                print(NAME_MANAGER)
                print("Version " + VERSION)
                print()
                # Executible Exists
                if os.path.isfile(saveData["coopDir"]):
                    print("Executible Directory: '" + saveData["coopDir"] + "'")
                else:
                    print("Executible Directory Invalid")
                # Appdata Exists
                if os.path.isdir(APPDATA_DIR):
                    print("Appdata Directory: '" + APPDATA_DIR + "'")
                else:
                    print("Appdata Directory Invalid")
                # Other Save Data
                print("Auto-Backup Mods: " + str(saveData["autoBackup"]))
                print()
                input("Press Enter to return to " + NAME_MAIN_MENU)
            if prompt2 == "4": # Exit
                break
    if prompt1 == "4": # Exit
        break
clear(False)
exit()
