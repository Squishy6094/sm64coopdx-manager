# Import Python's Default Libs
import os
import sys
import subprocess
import stat
import shutil
import pickle
import webbrowser
import time
from pathlib import Path
from datetime import datetime
import platform
import fnmatch

PLATFORM_WINDOWS = "Windows"
PLATFORM_LINUX = "Linux"
def platform_is_windows():
    systemName = platform.system()
    # Get Platform's Appdata Folder
    if systemName == PLATFORM_WINDOWS:
        return True
    elif systemName == PLATFORM_LINUX:
        return False
    else:
        print("SM64CoopDX Manager is not supported on your Operating System")
        input("Press Enter to Close Program")
        exit()


# Clear Console
def clear():
    if platform_is_windows(): # Windows
        _ = os.system('cls')
    else: # Linux
        _ = os.system('clear')

# Ensure Errors are Readable and Reportable
def show_exception_and_exit(exc_type, exc_value, tb):
    clear()
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    print()
    print("Please report this error to the Github!")
    input("Press Enter to Close Program")
    sys.exit(-1)
sys.excepthook = show_exception_and_exit

# Define Constants
NAME_SM64COOPDX = "SM64CoopDX"
NAME_MANAGER = NAME_SM64COOPDX + " Manager"
NAME_MANAGER_MODS = "Managed Mods"
NAME_MAIN_MENU = "Main Options"
NAME_MODS_MENU = "Mod Options"
NAME_MANAGER_PATH_CONFIG = "Configure Paths"
NAME_MANAGER_SETTINGS_AND_HELP = "Settings and Help"
NAME_MANAGER_SETTINGS = "Settings"
NAME_MANAGER_HELP = "Help"
NAME_FOLDER_OPTIONS = "Mod Folder Toggles"
VERSION = "1.1"
DATE = datetime.now().strftime("%m/%d/%Y")

clear()
print("Booting " + NAME_MANAGER + "...")

def return_consistent_dir(dir):
    if platform_is_windows():
        dir = str(dir).replace("/", "\\")
    else:
        dir = str(dir).replace("\\", "/")
    return dir

def split_consistent_dir(dir):
    dir = return_consistent_dir(dir)
    if platform_is_windows():
        dir = str(dir).split("\\")
    else:
        dir = str(dir).split("/")
    return dir
    
def folder_from_file_dir(filename):
    splitDir = split_consistent_dir(filename)
    dirCount = 0
    returnString = ""
    for x in splitDir:
        dirCount = dirCount + 1
        if dirCount < len(splitDir):
            returnString = returnString + x + "/"
    return returnString

# Define Constant Paths
USER_DIR = return_consistent_dir(Path.home())
os.chdir(USER_DIR)
FILE_DIR = return_consistent_dir(os.path.realpath(__file__))
SAVE_DIR = return_consistent_dir((folder_from_file_dir(FILE_DIR) + "coop-manager-" + VERSION + ".pickle"))
def get_appdata_dir():
    generalAppdata = ""

    # Get Platform's Appdata Folder
    if platform_is_windows():
        generalAppdata = USER_DIR + "/AppData/Roaming/"
    else:
        generalAppdata = USER_DIR + "/.local/share/"

    # Get Appdata folder for Coop
    if os.path.isdir(generalAppdata + "sm64ex-coop"):
        return generalAppdata + "sm64ex-coop"
    else:
        return generalAppdata + "sm64coopdx"
APPDATA_DIR = get_appdata_dir()

# Check External Libs
import importlib.util
installedModuleList = []
mustInstallModuleList = []
queueRestart = False
def check_module(package):
    packageSpec = importlib.util.find_spec(package)
    if packageSpec == None:
        mustInstallModuleList.append(package)
    else:
        installedModuleList.append(package)

def check_missing_module_and_stop():
    if len(mustInstallModuleList) > 0:
        clear()
        print(NAME_MANAGER + " requires the following python libraries to be installed before use:")
        for x in mustInstallModuleList:
            print("- " + x.capitalize())
        print()
        print("The following command can be used if you have 'pip' Installed")
        installCommand = "'pip install"
        for x in mustInstallModuleList:
            installCommand = installCommand + " " + x
        installCommand = installCommand + "'"
        print(installCommand)
        print()
        input("Press Enter to Exit Program")
        exit()
    
check_module('requests')
check_module('chime')
check_module('watchdog')
check_missing_module_and_stop()
import requests
import chime
import watchdog

def github_version_check():
    try:
        return requests.get("https://api.github.com/repos/Squishy6094/sm64coopdx-manager/releases/latest").json()["tag_name"]
    except:
        return None

def clear_with_header():
    clear()
    updateString = github_version_check()
    header = " " + NAME_MANAGER + " v" + VERSION + " - " + DATE + " "
    headerBreak = ""
    while len(headerBreak) < len(header):
        headerBreak = headerBreak + "="
    print(headerBreak)
    print(header)
    if updateString != None and updateString != "v" + VERSION:
        print(" Update Avalible! v" + VERSION + " -> " + updateString)
    print(headerBreak)
    print()

SUB_HEADER_LENGTH_DEFAULT = 29
def sub_header(headerText="|", length=SUB_HEADER_LENGTH_DEFAULT):
    subheaderText = " " + headerText + " "
    while len(subheaderText) < length:
        subheaderText = "=" + subheaderText + "="
    if len(subheaderText) == length:
        subheaderText = subheaderText + "="
    print(subheaderText)

def read_or_new_pickle(path, default):
    if os.path.isfile(path):
        with open(path, "rb") as f:
            try:
                return pickle.load(f)
            except Exception:
                pass
    else:
        with open(path, 'wb') as f:
            pickle.dump(default, f)
    return default

# Save Data Handler
saveData = {
    "coopDir": return_consistent_dir(USER_DIR + '/Downloads/sm64coopdx/sm64coopdx.exe'),
    "managedDir": return_consistent_dir(APPDATA_DIR + '/managed-mods'),
    "autoBackup": True,
    "loadChime": True,
    "showDirs": True,
    "skipUncompiled": False,
    "mods-.backup": False,
}
saveData = read_or_new_pickle(SAVE_DIR, saveData)
def save_field(field, value):
    saveData[field] = value
    with open(SAVE_DIR, "wb") as f:
        pickle.dump(saveData, f)
    return value

if not os.path.isdir(saveData["managedDir"]):
   os.makedirs(saveData["managedDir"])

NOTIF_1UP = 0
NOTIF_COIN = 1
def notify(sound=NOTIF_1UP):
    if saveData["loadChime"]:
        if sound == NOTIF_1UP:
            chime.theme('mario')
            chime.success(sync=True)
        if sound == NOTIF_COIN:
            chime.theme('mario')
            chime.info(sync=True)

# File Management
def file_unpermitted(filepath):
    fileStats = os.stat(filepath).st_file_attributes
    return not (bool(fileStats & stat.S_IRWXU) and bool(fileStats & stat.FILE_ATTRIBUTE_HIDDEN))

def unhide_tree(inputDir):
    for root, dirs, files in os.walk(inputDir):  
        for dir in dirs:
            path = os.path.join(root, dir)
            if file_unpermitted(path):
                os.chmod(path, stat.S_IRWXU)
        for file in files:
            path = os.path.join(root, file)
            if file_unpermitted(path):
                os.chmod(path, stat.S_IRWXU)

def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

def backup_mods(wipeModFolder=False, forceBackup=False):
    dir = return_consistent_dir(APPDATA_DIR + "/mods")
    if not saveData["autoBackup"]:
        if not forceBackup:
            print("Skipping Auto-Backup...")
            if wipeModFolder:
                print("Cleaning " + NAME_SM64COOPDX + "'s Appdata Mods Folder...")
                shutil.rmtree(dir, ignore_errors=True, onerror=del_rw)
            return
        else:
            print("Forcing Auto-Backup...")
    if os.path.isdir(dir):
        print("Appdata Mods Folder Found!")
        print("Ensuring " + NAME_SM64COOPDX + "'s Appdata Mods are moveable...")
        unhide_tree(dir)
        print("Ensuring Backups Folder is writeable...")
        unhide_tree(saveData["managedDir"] + "/.backup")
        print("Backing up " + NAME_SM64COOPDX + "'s Appdata Mods Folder...")
        shutil.copytree(dir, saveData["managedDir"] + "/.backup", dirs_exist_ok=True, copy_function=shutil.copy)
        if wipeModFolder:
            print("Cleaning " + NAME_SM64COOPDX + "'s Appdata Mods Folder...")
            shutil.rmtree(dir, ignore_errors=True, onerror=del_rw)
    dir = folder_from_file_dir(saveData["coopDir"]) + "/mods"
    if os.path.isdir(dir):
        print("Install Directory Mods Folder Found!")
        print("Ensuring " + NAME_SM64COOPDX + "'s Install Mods are moveable...")
        unhide_tree(dir)
        print("Cleaning " + NAME_MANAGER + "'s Default Folder...")
        shutil.rmtree(saveData["managedDir"] + "/default", ignore_errors=True)
        print("Backing up " + NAME_SM64COOPDX + "'s Install Mods Folder...")
        shutil.copytree(dir, saveData["managedDir"] + "/.backup", dirs_exist_ok=True)
        print("Moving " + NAME_SM64COOPDX + "'s Install Mods Folder to Defaults...")
        shutil.move(dir, saveData["managedDir"] + "/default")

# Backup on Bootup
clear_with_header()
backup_mods(False)

def include_patterns(*patterns):
    def _ignore_patterns(path, names):
        keep = set(name for pattern in patterns
            for name in fnmatch.filter(names, pattern))
        ignore = set(name for name in names
            if name not in keep and not os.path.isdir(os.path.join(path, name)))
        return ignore
    return _ignore_patterns

def get_mod_folders():
    modFolders = []
    for (dirpath, dirnames, filenames) in os.walk(saveData["managedDir"]):
        modFolders.extend(dirnames)
        for x in dirnames:
            if x[0:1] == ".":
                modFolders.remove(x)
        return modFolders

def get_enabled_mod_folders():
    modFolders = get_mod_folders()
    enabledModFolders = []
    for s in saveData:
        for f in modFolders:
            if s == ("mods-" + f) and saveData[s] == True:
                enabledModFolders.append(f)
    return enabledModFolders


IGNORE_INCLUDE_FILES = include_patterns('*.lua', '*.luac',
'*.bin', '*.col', '*.c', '*.h',
'*.bhv',
'*.mp3', '*.ogg', '*.m64', '*.aiff',
'*.lvl',
'*.png', '*.tex')

IGNORE_INCLUDE_FILES_COMP_ONLY = include_patterns('*.lua', '*.luac',
'*.bin', '*.col',
'*.bhv',
'*.mp3', '*.ogg', '*.m64', '*.aiff',
'*.lvl',
'*.tex')

def load_mod_folders():
    if not os.path.isdir(APPDATA_DIR):
        return
    print("Loading mods...")
    backup_mods(True)
    enabledMods = get_enabled_mod_folders()
    if saveData["skipUncompiled"]:
        print("Uncompiled Files will be skipped when moving!")
    for f in enabledMods:
        print("Ensuring " + f + "'s Mods are moveable...")
        unhide_tree(saveData["managedDir"] + "/" + f)
        print("Cloning " + f + " to " + NAME_SM64COOPDX + "'s Mods Folder")
        ignoreInput = IGNORE_INCLUDE_FILES
        if saveData["skipUncompiled"]:
            ignoreInput = IGNORE_INCLUDE_FILES_COMP_ONLY
        shutil.copytree(saveData["managedDir"] + "/" + f, APPDATA_DIR + "/mods",
            ignore=ignoreInput, dirs_exist_ok=True)
    notify()

def open_file(filename):
    if platform_is_windows():
        os.startfile(filename)
    else:
        subprocess.call(filename, cwd=folder_from_file_dir(filename))

        
def open_folder(foldername):
    if platform_is_windows():
        os.startfile(foldername)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, foldername],)

def boot_coop():
    coopDirectory = saveData["coopDir"]
    sub_header("Standard Boot")
    load_mod_folders()
    if saveData["showDirs"]:
        print("Booting " + NAME_SM64COOPDX + " from Path: '" + coopDirectory + "'")
    else:
        print("Booting " + NAME_SM64COOPDX)
    open_file(coopDirectory)


def config_coop_dir(notFound=False):
    clear_with_header()
    if notFound:
        if not saveData["showDirs"]:
            print(NAME_SM64COOPDX + " not found at expected Path!")
        else:
            print(NAME_SM64COOPDX + " not found at Path '" + saveData["coopDir"] + "'")
    else:
        if saveData["showDirs"]:
            print("Your current " + NAME_SM64COOPDX + " path is '" + saveData["coopDir"] + "'")
    print("Please enter a new Path to use for " + NAME_SM64COOPDX)
    if not saveData["showDirs"]:
        print("Anything typed below is not censored! Configure with caution!")
    print("(Type 'back' to return to " + NAME_MAIN_MENU + ")")
    while(True):
        inputDir = return_consistent_dir(input("> "))
        if os.path.isfile(inputDir):
            saveData["coopDir"] = save_field("coopDir", inputDir)
            return True
        elif inputDir == "back":
            return False
        else:
            print("Executible not found, please enter a valid directory")

def config_managed_dir():
    clear_with_header()
    print("Please enter a new Directory to put your " + NAME_MANAGER_MODS + " Folder")
    if not saveData["showDirs"]:
        print("Anything typed below is not censored! Configure with caution!")
    else:
        print("Your current " + NAME_MANAGER_MODS + " directory is in '" + folder_from_file_dir(saveData["managedDir"]) + "'")
    print("(Type 'back' to return to " + NAME_MAIN_MENU + ")")
    while(True):
        inputDir = return_consistent_dir(input("> "))
        if os.path.isdir(inputDir):
            prevManagedDir = saveData["managedDir"]
            saveData["managedDir"] = save_field("managedDir", inputDir + '/managed-mods')
            try:
                shutil.move(prevManagedDir, saveData["managedDir"])
            except:
                print("Hit error while attempting to move Mods to Inputted Directory")
                print("Please check both your previous and new directory for unmoved files!")
                input("Press Enter to Continue")

            return False
        elif inputDir == "back":
            return False
        else:
            print("Directory not found, please enter a valid directory")

#############################
## Automatic Menu Creation ##
#############################

def menu_option_name_with_toggle(name="Option", toggle=True, dots=-1):
    toggleString = ""
    if isinstance(toggle, bool):
        if toggle:
            toggleString = "(O)"
        else:
            toggleString = "(X)"
    else:
        toggleString = "(" + str(toggle) + ")"

    if dots < 0:
        dots = SUB_HEADER_LENGTH_DEFAULT - (len(name) + len(str(toggleString)) + 4)
    if dots < 0:
        dots = 0

    returnString = ""
    while len(returnString) < dots:
        returnString = returnString + "."
    returnString = name + " " + returnString + " " + toggleString
    return returnString

menuTable = []
def menu_clear():
    menuTable.clear()
    
def menu_back():
    return True

def menu_failsafe():
    return False

def menu_option_add(name="Option", function=menu_failsafe):
    menuTable.append({"name": name, "func": function})
    print(str(len(menuTable)) + ". " + menuTable[(len(menuTable) - 1)]["name"])

def menu_input():
    userInput = input("> ")
    if userInput == "":
        return False
    userInput = userInput.lower()
    optionCount = 0
    for x in menuTable:
        optionCount = optionCount + 1
        optionName = str(x["name"]).lower()
        if userInput == str(optionCount) or userInput == optionName or userInput == optionName.split(" ")[0]:
            menu_clear()
            return x["func"]() if x["func"] != None else False
    menu_clear()
    return False

####################
## Menu Functions ##
####################

def menu_toggle_backup():
    toggle_save_field("autoBackup")
def menu_toggle_chime():
    toggle_save_field("loadChime")
def menu_manager_toggle_dirs():
    toggle_save_field("showDirs")
def menu_toggle_uncomp_files():
    toggle_save_field("skipUncompiled")

def menu_main_open_coop():
    while(True):
        clear_with_header()
        if os.path.isfile(saveData["coopDir"]):
            boot_coop()
            break
        else:
            if config_coop_dir(True) == True:
                clear_with_header()
                boot_coop()
                break
            else:
                break

# Mod Options
def menu_mod_folder_config():
    while(True):
        clear_with_header()
        mods = get_mod_folders()
        modNum = 0
        if len(mods) < 1:
            print(NAME_MANAGER + "'s " + NAME_MANAGER_MODS + " Folder is empty!")
            if saveData["showDirs"]:
                print("Your " + NAME_MANAGER_MODS + " can be found at: '" + saveData["managedDir"] + "'")
            input("Press Enter to return to " + NAME_MODS_MENU)
            break
        sub_header(NAME_FOLDER_OPTIONS)
        for x in mods:
            modOnOff = False
            modNum = modNum + 1
            try:
                modOnOff = saveData["mods-" + x]
            except:
                saveData["mods-" + x] = save_field("mods-" + x, True)
                modOnOff = True
            print(str(modNum) + ". " + menu_option_name_with_toggle(x, modOnOff))
        print()
        print("Mods can be sorted in your 'managed-mods' Folder")
        if saveData["showDirs"]:
            print("(" + saveData["managedDir"] + ")")
        print()
        print("Type a Folder's Name / Number to Toggle it")
        print("Type 'all' or 'none' to Enable or Disable all Folders")
        print("Type 'apply' to Apply Current Folders without leaving")
        print("Type 'back' to return to " + NAME_MODS_MENU)
        prompt3 = input("> ")
        if prompt3 == "all":
            for x in mods:
                save_field("mods-" + x, True)
            save_field("mods-.backup", False)
        if prompt3 == "none":
            for x in mods:
                save_field("mods-" + x, False)
        if prompt3 == "apply" or prompt3 == "":
            clear_with_header()
            load_mod_folders()
        if prompt3 == "back":
            clear_with_header()
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

def menu_mod_backup_clear():
    clear_with_header()
    backup_mods(True, True)

def menu_mod_open_managed_folder():
    open_folder(saveData["managedDir"])

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

class watchdogHandler(FileSystemEventHandler):
    def on_any_event(self, event: FileSystemEvent) -> None:
        print()
        
        if str(event.src_path).find(".git") != -1 or str(event.src_path).endswith("~"):
            print("Ignoring " + event.src_path)
            return None
        
        if saveData["showDirs"]:
            print("Change detected at " + event.src_path)
        else:
            print("Change detected!")
        load_mod_folders()

def watchdog_mode():
    clear_with_header()
    print(NAME_MANAGER + " will now enter Development Mode")
    print()
    print("The program will idle and look for changes in your active " + NAME_MANAGER_MODS + " Folders,")
    print("Once a change is detected it will automatically push the " + NAME_MANAGER_MODS + " to " + NAME_SM64COOPDX + "'s Mods Folder")
    print("The program cannot exit out of this mode via prompts once started")
    if saveData["autoBackup"] or not saveData["skipUncompiled"]:
        print()
        print("Note: It is highly recommended you turn off the following settings in Manager Options")
        if saveData["autoBackup"]:
            print("Auto-Backup")
        if not saveData["skipUncompiled"]:
            print("Skip Uncompiled Files")
    print()
    print("Press ENTER to continute, or type 'back' to exit")
    confirm = input("> ")
    if confirm.lower() == "back":
        return False
    else:
        notify(NOTIF_COIN)
        clear()
        modFolders = get_enabled_mod_folders()
        observer = Observer()
        print("Setting up Observer")
        for x in modFolders:
            print("Scheduling Mod Folder " + x)
            observer.schedule(watchdogHandler(), return_consistent_dir(saveData["managedDir"] + "/" + x), recursive=True)
        observer.start()
        print("Observer Started")
        while True:
            time.sleep(1)

def menu_mod_config_settings():
    while(True):
        clear_with_header()
        sub_header("Management Settings:")
        menu_clear()
        menu_option_add(menu_option_name_with_toggle("Auto-Backup", saveData["autoBackup"]), menu_toggle_backup)
        menu_option_add(menu_option_name_with_toggle("Load Chime", saveData["loadChime"]), menu_toggle_chime)
        menu_option_add(menu_option_name_with_toggle("Uncompiled Files", (not saveData["skipUncompiled"])), menu_toggle_uncomp_files)
        
        expectedLoadTime = 0
        if saveData["autoBackup"]:
            expectedLoadTime = expectedLoadTime + 1
        if not saveData["skipUncompiled"]:
            expectedLoadTime = expectedLoadTime + 1
        if expectedLoadTime == 0:
            expectedLoadTime = "Low"
        elif expectedLoadTime == 1:
            expectedLoadTime = "Medium"
        else:
            expectedLoadTime = "High"
        print("Management Time: " + expectedLoadTime)
        sub_header()
        menu_option_add("Back", menu_back)
        if menu_input():
            break

def menu_main_mod_options():
    while(True):
        clear_with_header()
        if not os.path.isdir(APPDATA_DIR):
            print("Appdata Directory does not exist, please open " + NAME_SM64COOPDX + " first!")
            input("Press Enter to return to " + NAME_MAIN_MENU)
            clear()
        else:
            sub_header(NAME_MODS_MENU)
            menu_clear()
            menu_option_add("Config " + NAME_MANAGER_MODS, menu_mod_folder_config)
            menu_option_add("Open " + NAME_MANAGER_MODS + " Folder", menu_mod_open_managed_folder)
            menu_option_add("Backup and Clear Mods Folder", menu_mod_backup_clear)
            menu_option_add("Management Settings", menu_mod_config_settings)
            menu_option_add("Development Mode", watchdog_mode)
            sub_header()
            menu_option_add("Back", menu_back)
            if menu_input():
                break

# Manager Options
def toggle_save_field(saveString):
    if saveData[saveString] != None:
        saveData[saveString] = save_field(saveString, not saveData[saveString])

def menu_manager_info():
    clear_with_header()
    sub_header("Manager Info")
    print(NAME_MANAGER + " by Squishy6094")
    print("Version " + VERSION + " / Github Version " + str(github_version_check()).replace("v", ""))
    sub_header("User Info")
    # Executible Exists
    if os.path.isfile(saveData["coopDir"]):
        if saveData["showDirs"]:
            print("Executible Path: '" + saveData["coopDir"] + "'")
        else:
            print("Executible Path Valid")
    else:
        print("Executible Path Invalid")
    # Appdata Exists
    if os.path.isdir(APPDATA_DIR):
        if saveData["showDirs"]:
            print(NAME_MANAGER_MODS + " Directory: '" + saveData["managedDir"] + "'")
        else:
            print(NAME_MANAGER_MODS + " Directory Valid")
    else:
        print(NAME_MANAGER_MODS + " Directory Invalid")
    # Other Save Data
    print("Auto-Backup Mods: " + str(saveData["autoBackup"]))
    print("Load Chime: " + str(saveData["loadChime"]))
    print("Streamer Mode (Hide Directories): " + str(not saveData["loadChime"]))
    sub_header("Library Info")
    print("Required Python Libraries Installed:")
    for x in installedModuleList:
        print("- " + x)
    input("Press Enter to return to " + NAME_MAIN_MENU)

def menu_manager_link_github():
    webbrowser.open("https://github.com/Squishy6094/sm64coopdx-manager", new=0, autoraise=True)
def menu_manager_link_community():
    webbrowser.open("https://discord.gg/HtpXAxrgAw", new=0, autoraise=True)
def menu_manager_link_central():
    webbrowser.open("https://discord.gg/G2zMwjbxdh", new=0, autoraise=True)

def menu_manager_links():
    while(True):
        clear_with_header()
        sub_header("Support Links:")
        menu_clear()
        menu_option_add(NAME_MANAGER + " - Issue Reporting - (Github)", menu_manager_link_github)
        menu_option_add("Squishy Community - Manager Support - (Discord)", menu_manager_link_community)
        menu_option_add("Coop Central - " + NAME_SM64COOPDX + " Support - (Discord)", menu_manager_link_central)
        sub_header()
        menu_option_add("Back", menu_back)
        if menu_input():
            break
    
def menu_main_manager_options():
    while(True):
        clear_with_header()
        sub_header(NAME_MANAGER_PATH_CONFIG)
        menu_clear()
        menu_option_add(NAME_SM64COOPDX + " Executible Path", config_coop_dir)
        menu_option_add(NAME_MANAGER_MODS + " Directory", config_managed_dir)
        sub_header(NAME_MANAGER_SETTINGS_AND_HELP)
        menu_option_add(menu_option_name_with_toggle("Streamer Mode", (not saveData["showDirs"])), menu_manager_toggle_dirs)
        menu_option_add("Info", menu_manager_info)
        menu_option_add("Support Links", menu_manager_links)
        sub_header()
        menu_option_add("Back", menu_back)
        if menu_input():
            break


###############
## Main Menu ##
###############

notify()
while(True):
    clear_with_header()
    sub_header(NAME_MAIN_MENU)
    menu_clear()
    menu_option_add("Open " + NAME_SM64COOPDX, menu_main_open_coop)
    menu_option_add("Mod Options", menu_main_mod_options)
    menu_option_add("Manager Options", menu_main_manager_options)
    sub_header()
    menu_option_add("Close Program", menu_back)
    if menu_input():
        break
clear()
exit()
