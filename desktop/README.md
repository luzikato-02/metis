# Data Cleaner Desktop Application

A standalone desktop application for cleaning production data, built with Electron.

## Prerequisites

Before running the desktop app, make sure you have:

1. **Node.js 18+** - Download from https://nodejs.org
2. **Python 3.10+** - Download from https://python.org
3. **Python dependencies** installed

## Quick Start (Development Mode)

### 1. Install Python Dependencies

```bash
# From the project root
pip install -e ".[dev]"
pip install -r web/backend/requirements.txt
```

### 2. Build the Frontend

```bash
cd web/frontend
npm install
npm run build
cd ../..
```

### 3. Install Electron Dependencies

```bash
cd desktop
npm install
```

### 4. Run the App

```bash
npm start
```

This will:
- Start the Flask backend server
- Open the Electron window with the app

## Building Distributable Packages

### Build for Your Current Platform

```bash
cd desktop
npm run dist
```

### Build for Specific Platforms

```bash
# Windows
npm run dist:win

# macOS
npm run dist:mac

# Linux
npm run dist:linux
```

Built packages will be in the `desktop/dist` folder.

## Project Structure

```
desktop/
├── main.js          # Electron main process
├── preload.js       # Preload script for security
├── package.json     # Electron dependencies and build config
├── icon.png         # App icon (add your own)
└── dist/            # Built packages (after running npm run dist)
```

## How It Works

1. **Electron** creates a native desktop window
2. **Flask** runs as a background process on port 5000
3. The **React frontend** is loaded into the Electron window
4. All data cleaning happens locally on your machine

## Troubleshooting

### "Python Not Found" Error

Make sure Python 3 is installed and accessible from the command line:

```bash
python3 --version
# or on Windows:
python --version
```

### "Backend Error" on Startup

Install the required Python packages:

```bash
pip install flask flask-cors flask-sqlalchemy pandas openpyxl
```

### App Window is Blank

Make sure you've built the frontend first:

```bash
cd web/frontend
npm run build
```

### Port 5000 Already in Use

Another application is using port 5000. Close it or modify the `FLASK_PORT` in `main.js`.

## Customizing the App Icon

Replace `icon.png` with your own icon:
- **Windows**: 256x256 PNG or ICO file
- **macOS**: 512x512 PNG or ICNS file
- **Linux**: 256x256 PNG file

## Development Tips

### Hot Reload Frontend

Run the Vite dev server alongside Electron:

```bash
# Terminal 1: Start Vite dev server
cd web/frontend
npm run dev

# Terminal 2: Start Electron (will connect to Vite)
cd desktop
npm start
```

### View Console Logs

In development mode, DevTools opens automatically. You can also:
- Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (macOS)

### Debug Flask Backend

Check the terminal where Electron is running for Flask logs.

## System Requirements

- **Windows**: Windows 10 or later
- **macOS**: macOS 10.13 (High Sierra) or later
- **Linux**: Ubuntu 18.04 or later (or equivalent)

## License

MIT
