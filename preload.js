const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  openCoop: () => ipcRenderer.send('open-coop'),
  coopIsOpen: () => ipcRenderer.send('coop-is-open')
});
