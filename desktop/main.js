const { app, BrowserWindow, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');

// Keep a global reference of the window object
let mainWindow = null;
let flaskProcess = null;

// Configuration
const FLASK_PORT = 5000;
const isDev = !app.isPackaged;

// Get the correct paths based on dev vs production
function getResourcePath(relativePath) {
  if (isDev) {
    return path.join(__dirname, '..', relativePath);
  }
  return path.join(process.resourcesPath, relativePath);
}

function getFrontendPath() {
  if (isDev) {
    return path.join(__dirname, '..', 'web', 'frontend', 'dist');
  }
  return path.join(process.resourcesPath, 'frontend');
}

function getBackendPath() {
  if (isDev) {
    return path.join(__dirname, '..', 'web', 'backend');
  }
  return path.join(process.resourcesPath, 'backend');
}

// Find Python executable
function findPython() {
  const pythonCommands = process.platform === 'win32' 
    ? ['python', 'python3', 'py'] 
    : ['python3', 'python'];
  
  for (const cmd of pythonCommands) {
    try {
      const result = require('child_process').spawnSync(cmd, ['--version']);
      if (result.status === 0) {
        return cmd;
      }
    } catch (e) {
      continue;
    }
  }
  return null;
}

// Check if Flask server is running
function checkServer(port, callback) {
  const options = {
    host: '127.0.0.1',
    port: port,
    path: '/api/health',
    timeout: 1000
  };

  const req = http.request(options, (res) => {
    callback(res.statusCode === 200);
  });

  req.on('error', () => {
    callback(false);
  });

  req.on('timeout', () => {
    req.destroy();
    callback(false);
  });

  req.end();
}

// Wait for server to be ready
function waitForServer(port, maxAttempts = 30) {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    
    const check = () => {
      attempts++;
      checkServer(port, (isRunning) => {
        if (isRunning) {
          resolve();
        } else if (attempts >= maxAttempts) {
          reject(new Error('Server failed to start'));
        } else {
          setTimeout(check, 500);
        }
      });
    };
    
    check();
  });
}

// Start Flask backend
async function startFlaskServer() {
  const pythonCmd = findPython();
  
  if (!pythonCmd) {
    dialog.showErrorBox(
      'Python Not Found',
      'Python 3 is required to run this application.\n\nPlease install Python 3.10 or later from https://python.org'
    );
    app.quit();
    return false;
  }

  const backendPath = getBackendPath();
  const srcPath = isDev 
    ? path.join(__dirname, '..', 'src')
    : path.join(process.resourcesPath, 'src');

  // Set environment variables
  const env = {
    ...process.env,
    PYTHONPATH: srcPath,
    FLASK_ENV: 'production',
    PORT: FLASK_PORT.toString()
  };

  console.log('Starting Flask server...');
  console.log('Backend path:', backendPath);
  console.log('Python command:', pythonCmd);

  flaskProcess = spawn(pythonCmd, ['app.py'], {
    cwd: backendPath,
    env: env,
    stdio: ['ignore', 'pipe', 'pipe']
  });

  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask: ${data}`);
  });

  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask Error: ${data}`);
  });

  flaskProcess.on('error', (error) => {
    console.error('Failed to start Flask:', error);
    dialog.showErrorBox(
      'Backend Error',
      `Failed to start the backend server:\n${error.message}`
    );
  });

  flaskProcess.on('exit', (code) => {
    console.log(`Flask process exited with code ${code}`);
    if (code !== 0 && code !== null && mainWindow) {
      dialog.showErrorBox(
        'Backend Stopped',
        'The backend server has stopped unexpectedly.'
      );
    }
  });

  try {
    await waitForServer(FLASK_PORT);
    console.log('Flask server is ready');
    return true;
  } catch (error) {
    console.error('Flask server failed to start:', error);
    dialog.showErrorBox(
      'Backend Error',
      'The backend server failed to start. Please check that all Python dependencies are installed.'
    );
    return false;
  }
}

// Create the browser window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'icon.png'),
    show: false, // Don't show until ready
    backgroundColor: '#ffffff'
  });

  // Load the app
  if (isDev) {
    // In development, try to connect to Vite dev server first
    mainWindow.loadURL('http://localhost:5173').catch(() => {
      // Fall back to built files
      const frontendPath = getFrontendPath();
      mainWindow.loadFile(path.join(frontendPath, 'index.html'));
    });
  } else {
    const frontendPath = getFrontendPath();
    mainWindow.loadFile(path.join(frontendPath, 'index.html'));
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Open external links in browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Open DevTools in development
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }
}

// App lifecycle events
app.whenReady().then(async () => {
  // Show loading message
  console.log('Starting Data Cleaner...');
  
  // Start Flask server
  const serverStarted = await startFlaskServer();
  
  if (serverStarted) {
    createWindow();
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  // Stop Flask server
  if (flaskProcess) {
    console.log('Stopping Flask server...');
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', flaskProcess.pid, '/f', '/t']);
    } else {
      flaskProcess.kill('SIGTERM');
    }
  }

  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (flaskProcess) {
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', flaskProcess.pid, '/f', '/t']);
    } else {
      flaskProcess.kill('SIGTERM');
    }
  }
});
