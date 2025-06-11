// sm64coopdx-manager.js (Electron translation scaffold)

// Core Modules
const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { execFile } = require('child_process');
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));
const unzipper = require('unzipper');
const chokidar = require('chokidar');
const fse = require('fs-extra');

// Logging helper
var lastLog = "";

function log(msg) {
    lastLog = msg;
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${msg}`);
}

function getLatestLog() {
    return lastLog;
}

function getLastFolderName(dirPath) {
    return path.basename(path.resolve(dirPath));
}

// Constants
const PLATFORM = process.platform;
const USER_DIR = os.homedir();
const APPDATA_DIR = PLATFORM === 'win32'
  ? path.join(process.env.APPDATA || path.join(USER_DIR, 'AppData', 'Roaming'))
  : path.join(USER_DIR, '.local', 'share');
const NAME_SM64COOPDX = "SM64CoopDX";
const NAME_MANAGER = `${NAME_SM64COOPDX} Manager`;
const VERSION = "2";
// Set working directory to the current JS file's location
process.chdir(__dirname);
const SAVE_FILE = path.join(__dirname, "coop-manager.json");
const DEFAULT_SAVE_DATA = {
  coopDir: path.join(USER_DIR, "Downloads", "sm64coopdx", "sm64coopdx"),
  managedDir: path.join(APPDATA_DIR, "sm64coopdx", "managed-mods"),
  autoBackup: true,
  loadChime: true,
  showDirs: true,
  githubMods: true,
  skipUncompiled: false,
  "mods-.backup": false
};

function readSaveData() {
    try {
        if (!fs.existsSync(SAVE_FILE)) {
            fs.mkdirSync(path.dirname(SAVE_FILE), { recursive: true });
            fs.writeFileSync(SAVE_FILE, JSON.stringify(DEFAULT_SAVE_DATA, null, 2));
            return { ...DEFAULT_SAVE_DATA };
        }
        const raw = fs.readFileSync(SAVE_FILE, 'utf8');
        return JSON.parse(raw);
    } catch (e) {
        log("Failed to read save data:", e);
        try {
            fs.writeFileSync(SAVE_FILE, JSON.stringify(DEFAULT_SAVE_DATA, null, 2));
        } catch {}
        return { ...DEFAULT_SAVE_DATA };
    }
}

function writeSaveData(data) {
  try {
    fs.mkdirSync(path.dirname(SAVE_FILE), { recursive: true });
    fs.writeFileSync(SAVE_FILE, JSON.stringify(data, null, 2));
  } catch (e) {
    log("Failed to write save data:", e);
  }
}

let saveData;

function bootCoop() {
  log('Attempting to boot coop...');
  const coopPath = saveData.coopDir;
  if (fs.existsSync(coopPath)) {
    execFile(coopPath, {
      cwd: path.dirname(coopPath),
      env: { ...process.env, LD_LIBRARY_PATH: path.dirname(coopPath) }
    }, (err) => {
      if (err) log("Failed to launch:", err);
      else log("Launched successfully.");
    });
  } else {
    log(`Coop executable not found at: ${coopPath}`);
  }
}
function getAllModFolders() {
    try {
        const entries = fs.readdirSync(saveData.managedDir, { withFileTypes: true });
        const modFolders = entries.filter(e => e.isDirectory() && !e.name.startsWith('.')).map(e => e.name);

        // Set mods without save data to true
        let changed = false;
        modFolders.forEach(name => {
            const key = `mods-${name}`;
            if (saveData[key] === undefined) {
                // If folder starts with ".", set to false by default
                saveData[key] = name.startsWith('.') ? false : true;
                changed = true;
            }
        });
        if (changed) writeSaveData(saveData);

        return modFolders;
    } catch (e) {
        log("Failed to list mod folders:", e);
        return [];
    }
}
function getEnabledMods() {
    const allMods = getAllModFolders();
    return allMods.filter(modName => !!saveData[`mods-${modName}`]);
}
function loadMods() {
    const dest = path.join(APPDATA_DIR, "sm64coopdx", "mods");
    if (!fs.existsSync(dest)) {
        fs.mkdirSync(dest, { recursive: true });
    } else {
        // Clear the mods folder before loading new mods
        fse.emptyDirSync(dest);
    }

    getEnabledMods().forEach((modName) => {
        const src = path.join(saveData.managedDir, modName);
        if (fs.existsSync(src)) {
            log(`Moving ${getLastFolderName(src)} to Mods`);
            fse.copy(src, dest, { overwrite: true });
        }
    });
    log(`Finished Loading Mods!`);
}

async function backupMods() {
    const managedMods = saveData.managedDir;
    const backupDir = path.join(managedMods, ".backup");
    if (fs.existsSync(managedMods)) {
        fse.ensureDirSync(backupDir);
        const entries = fs.readdirSync(managedMods, { withFileTypes: true });
        entries.forEach(entry => {
            if (entry.isDirectory() && entry.name !== ".backup") {
                const src = path.join(managedMods, entry.name);
                const innerEntries = fs.readdirSync(src, { withFileTypes: true });
                innerEntries.forEach(innerEntry => {
                    const modSrc = path.join(src, innerEntry.name);
                    const modDest = path.join(backupDir, innerEntry.name);
                    if (innerEntry.isDirectory()) {
                        fse.copy(modSrc, modDest, { overwrite: true });
                    } else if (innerEntry.isFile() && innerEntry.name.endsWith('.lua')) {
                        fse.copy(modSrc, modDest, { overwrite: true });
                    }
                    log(`Backing up ${getLastFolderName(modSrc)}`);
                });
            }
        });
    }
}

async function updateGithubMod(repoKey) {
    if (!saveData.githubMods) return;
    const repo = repoKey.replace("github-", "");
    const commitsAPI = `https://api.github.com/repos/${repo}/commits/main`;
    const zipURL = `https://github.com/${repo}/archive/refs/heads/main.zip`;

    try {
        const res = await fetch(commitsAPI);
        if (!res.ok) throw new Error(`Failed to fetch commits: ${res.status}`);
        const data = await res.json();
        const latestSHA = Array.isArray(data) ? data[0]?.sha : data.sha;
        const storedSHA = saveData[repoKey] || "0";

        const modFolder = path.join(saveData.managedDir, "github-mods", `${repo.split("/")[1]}-main`);
        if (latestSHA !== storedSHA || !fs.existsSync(modFolder)) {
            log(`Updating ${repo} to latest commit ${latestSHA}`);
            saveData[repoKey] = latestSHA;
            writeSaveData(saveData);

            const zipPath = path.join(saveData.managedDir, `${repo.replace("/", "_")}_main.zip`);
            const extractPath = path.join(saveData.managedDir, "github-mods");

            const zipRes = await fetch(zipURL);
            if (!zipRes.ok) throw new Error(`Failed to download ZIP: ${zipRes.status}`);

            await new Promise((resolve, reject) => {
                const dest = fs.createWriteStream(zipPath);
                zipRes.body.pipe(dest);
                zipRes.body.on("error", reject);
                dest.on("finish", resolve);
            });

            await fse.ensureDir(extractPath);
            await fs.createReadStream(zipPath).pipe(unzipper.Extract({ path: extractPath })).promise();
            fs.unlinkSync(zipPath);
        } else {
            log(`${repo} already up-to-date.`);
        }
    } catch (err) {
        log(`Failed to update ${repo}: ${err}`);
    }
}

async function updateAllGithubMods() {
  const mods = Object.keys(saveData).filter(k => k.startsWith("github-"));
  for (const key of mods) {
    await updateGithubMod(key);
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  win.loadFile('index.html');
}

app.whenReady().then(async () => {
  log(`Booting ${NAME_MANAGER}...`);
  createWindow();

  saveData = readSaveData();
  await backupMods();
  await updateAllGithubMods();
  await loadMods();
});

// Expose functions to index.html
ipcMain.on('boot-coop', () => {
  loadMods();
  bootCoop();
});

ipcMain.on('save-settings', (event, newData) => {
  saveData = { ...saveData, ...newData };
  writeSaveData(saveData);
});

ipcMain.on('update-github-mods', () => {
  updateAllGithubMods();
});

ipcMain.handle('latest-log', () => {
    return getLatestLog(); // returns a string, not a promise
});

ipcMain.handle('get-mod-folders', () => {
  return getAllModFolders().map(name => ({
    name,
    enabled: !!saveData[`mods-${name}`]
  }));
});

ipcMain.on('toggle-mod', (event, modName) => {
  const key = `mods-${modName}`;
  saveData[key] = !saveData[key];
  writeSaveData(saveData);
});
