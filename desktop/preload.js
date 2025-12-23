// Preload script for Electron
// This runs in a sandboxed context with access to Node.js APIs

const { contextBridge } = require('electron');

// Expose protected methods to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  platform: process.platform,
  isElectron: true
});

console.log('Preload script loaded');
