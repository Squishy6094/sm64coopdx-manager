const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  bootCoop: () => ipcRenderer.send('boot-coop'),
  coopIsOpen: () => ipcRenderer.send('coop-is-open'),
  getLatestLog: () => ipcRenderer.invoke('latest-log'),
});
