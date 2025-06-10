const { app, BrowserWindow, ipcMain } = require('electron');
const { execFile } = require('child_process');
const path = require('path');

const createWindow = () => {
    const win = new BrowserWindow({
        width: 960,
        height: 700,
        webPreferences: {
        preload: path.join(__dirname, 'preload.js'),
        contextIsolation: true,
        nodeIntegration: false
        }
    })
    win.loadFile('index.html')
    win.setMenuBarVisibility(false);
}

app.whenReady().then(() => {
    createWindow()
})
function isCoopOpen() {
    return global.gameProcess && !global.gameProcess.killed;
}

ipcMain.on('coop-is-open', () => {
    return global.gameProcess && !global.gameProcess.killed;
})

// IPC handler to launch the game
ipcMain.on('open-coop', () => {
    const gamePath = '/home/squishy6094/Games/sm64coopdx/sm64coopdx';
    const gameDir = path.dirname(gamePath);

    // Store the child process globally
    if (!isCoopOpen()) {
        global.gameProcess = execFile(gamePath, {
            cwd: gameDir,
            env: { ...process.env, LD_LIBRARY_PATH: gameDir }
        }, (err) => {
            if (err) console.error('Failed to launch game:', err);
            else console.log('Game launched successfully');
            // Reset the process reference when it exits
            global.gameProcess = null;
        });
    } else {
        console.log('Game is already running.');
    }
})

// Ensure the game process is killed when the launcher closes
app.on('before-quit', () => {
    if (global.gameProcess && !global.gameProcess.killed) {
        global.gameProcess.kill();
    }
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})