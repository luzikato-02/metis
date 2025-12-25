# Desktop App Build Guide

This guide provides detailed instructions on how to build the Data Cleaner desktop application for Windows, macOS, and Linux.

## Overview

The Data Cleaner desktop app is built with:
- **Electron** - Desktop application framework
- **React + Vite** - Frontend UI (from `web/frontend`)
- **Flask** - Backend API server (from `web/backend`)
- **Python** - Core data cleaning logic (from `src/data_cleaning`)

The Electron app bundles everything together and manages the Flask backend as a child process.

---

## Prerequisites

### Required Software

| Software | Version | Download |
|----------|---------|----------|
| **Node.js** | 18+ (recommended: 20) | https://nodejs.org |
| **Python** | 3.10+ (recommended: 3.12) | https://python.org |
| **npm** | Comes with Node.js | - |
| **pip** | Comes with Python | - |

### Verify Installation

```bash
node --version    # Should output v18.x.x or higher
npm --version     # Should output 9.x.x or higher
python3 --version # Should output Python 3.10.x or higher
pip --version     # Should output pip 23.x or higher
```

---

## Quick Start (Automated Setup)

The easiest way to set up everything is using the automated setup script:

```bash
cd desktop
python setup.py
```

This script will:
1. ✅ Check Python and Node.js installations
2. ✅ Install Python dependencies
3. ✅ Install and build the frontend
4. ✅ Install Electron dependencies

After setup completes, run:

```bash
npm start
```

---

## Manual Build Steps

### Step 1: Install Python Dependencies

From the project root directory:

```bash
# Install the main data-cleaning package in development mode
pip install -e ".[dev]"

# Install Flask backend dependencies
pip install -r web/backend/requirements.txt
```

**Dependencies installed:**
- `pandas` - Data manipulation
- `flask` - Web server
- `flask-cors` - Cross-origin support
- `flask-sqlalchemy` - Database ORM
- `openpyxl` - Excel file support
- `pytest` - Testing (dev only)

### Step 2: Build the Frontend

```bash
cd web/frontend

# Install npm dependencies
npm install

# Build the production bundle
npm run build

cd ../..
```

This creates the `web/frontend/dist` folder with optimized static files.

### Step 3: Install Electron Dependencies

```bash
cd desktop
npm install
```

### Step 4: Run in Development Mode

```bash
npm start
```

This will:
1. Start the Flask backend server on port 5000
2. Open the Electron window with the app
3. In dev mode, DevTools opens automatically

---

## Building Distributable Packages

### Build for Current Platform

```bash
cd desktop
npm run dist
```

### Build for Specific Platforms

```bash
# Windows (creates .exe installer and portable .exe)
npm run dist:win

# macOS (creates .dmg and .zip)
npm run dist:mac

# Linux (creates .AppImage and .deb)
npm run dist:linux
```

### Output Location

Built packages are saved to:

```
desktop/dist/
├── Data Cleaner Setup 1.0.0.exe     # Windows NSIS installer
├── Data Cleaner 1.0.0.exe            # Windows portable
├── Data Cleaner-1.0.0.dmg            # macOS disk image
├── Data Cleaner-1.0.0-mac.zip        # macOS zip archive
├── Data Cleaner-1.0.0.AppImage       # Linux AppImage
└── data-cleaner_1.0.0_amd64.deb      # Linux Debian package
```

---

## Build Configuration

### Package Configuration (`desktop/package.json`)

Key build settings:

```json
{
  "build": {
    "appId": "com.datacleaner.app",
    "productName": "Data Cleaner",
    "extraResources": [
      { "from": "../web/frontend/dist", "to": "frontend" },
      { "from": "../web/backend", "to": "backend" },
      { "from": "../src", "to": "src" }
    ]
  }
}
```

### What Gets Bundled

| Source | Destination | Description |
|--------|-------------|-------------|
| `web/frontend/dist` | `resources/frontend` | React app static files |
| `web/backend/*.py` | `resources/backend` | Flask server code |
| `src/data_cleaning/*.py` | `resources/src` | Core Python modules |
| `pyproject.toml` | `resources/` | Python project config |

### Platform-Specific Outputs

| Platform | Targets | Icon Format |
|----------|---------|-------------|
| Windows | NSIS installer, Portable | PNG or ICO (256x256) |
| macOS | DMG, ZIP | PNG or ICNS (512x512) |
| Linux | AppImage, DEB | PNG (256x256) |

---

## CI/CD Pipeline

The project includes a GitHub Actions workflow for automated builds.

### Workflow File

`.github/workflows/build app for win.yml`

### Trigger Conditions

| Trigger | Description |
|---------|-------------|
| Push to `main` | Builds on every push to main branch |
| Pull requests to `main` | Builds on PRs for testing |
| Tag `v*` | Creates a GitHub release with artifacts |
| Manual | Can be triggered manually via GitHub UI |

### Build Matrix

The workflow builds for all three platforms in parallel:

```yaml
matrix:
  include:
    - os: ubuntu-latest   # Linux
    - os: windows-latest  # Windows
    - os: macos-latest    # macOS
```

### Release Process

To create a release:

1. Create and push a version tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. The workflow will:
   - Build for all platforms
   - Upload artifacts
   - Create a GitHub release with all installers

---

## Architecture

### How the Desktop App Works

```
┌─────────────────────────────────────────────────────────┐
│                    Electron App                          │
│  ┌─────────────────┐         ┌────────────────────────┐ │
│  │   Main Process  │         │   Renderer Process     │ │
│  │   (main.js)     │         │   (React Frontend)     │ │
│  │                 │         │                        │ │
│  │  - Spawns Flask │ ──────> │  - Loads index.html    │ │
│  │  - Creates      │         │  - Calls API on :5000  │ │
│  │    BrowserWindow│         │  - Displays UI         │ │
│  └────────┬────────┘         └────────────────────────┘ │
│           │                                              │
│           ▼                                              │
│  ┌─────────────────┐                                    │
│  │  Flask Backend  │                                    │
│  │  (port 5000)    │                                    │
│  │                 │                                    │
│  │  - REST API     │                                    │
│  │  - Data cleaning│                                    │
│  │  - File I/O     │                                    │
│  └─────────────────┘                                    │
└─────────────────────────────────────────────────────────┘
```

### Key Files

| File | Purpose |
|------|---------|
| `desktop/main.js` | Electron main process - manages window and Flask |
| `desktop/preload.js` | Secure bridge between main and renderer |
| `desktop/package.json` | Dependencies and electron-builder config |
| `desktop/setup.py` | Automated setup script |

---

## Troubleshooting

### Common Issues

#### "Python Not Found" Error

**Problem:** Electron can't find Python executable.

**Solution:**
```bash
# Ensure Python is in PATH
python3 --version

# On Windows, you may need:
python --version
```

#### "Backend Error" on Startup

**Problem:** Flask server fails to start.

**Solution:**
```bash
# Reinstall backend dependencies
pip install flask flask-cors flask-sqlalchemy pandas openpyxl
```

#### App Window is Blank

**Problem:** Frontend wasn't built.

**Solution:**
```bash
cd web/frontend
npm run build
```

#### Port 5000 Already in Use

**Problem:** Another app is using port 5000.

**Solution:**
1. Close the other application, OR
2. Edit `FLASK_PORT` in `desktop/main.js`

#### Build Fails on Windows

**Problem:** electron-builder fails on Windows.

**Solution:**
```bash
# Run as Administrator
npm cache clean --force
npm install
npm run dist:win
```

### Debug Mode

To see detailed logs:

```bash
# Start with debug output
DEBUG=electron-builder npm run dist
```

---

## Customization

### Changing App Icon

Replace `desktop/icon.svg` (or add `icon.png`) with your custom icon:

| Platform | Recommended Format | Size |
|----------|-------------------|------|
| Windows | PNG or ICO | 256x256 |
| macOS | PNG or ICNS | 512x512 |
| Linux | PNG | 256x256 |

### Changing App Name

Edit `desktop/package.json`:

```json
{
  "name": "your-app-name",
  "build": {
    "appId": "com.yourcompany.yourapp",
    "productName": "Your App Name"
  }
}
```

### Changing Flask Port

Edit `desktop/main.js`:

```javascript
const FLASK_PORT = 5001;  // Change from 5000
```

---

## Development Tips

### Hot Reload Frontend

For faster frontend development:

```bash
# Terminal 1: Start Vite dev server
cd web/frontend
npm run dev

# Terminal 2: Start Electron (connects to Vite on :5173)
cd desktop
npm start
```

### View DevTools

- **Windows/Linux:** `Ctrl+Shift+I`
- **macOS:** `Cmd+Option+I`

DevTools opens automatically in development mode.

### Check Flask Logs

Flask logs appear in the terminal where you started Electron.

---

## System Requirements for End Users

| Platform | Minimum Version |
|----------|-----------------|
| Windows | Windows 10 or later |
| macOS | macOS 10.13 (High Sierra) or later |
| Linux | Ubuntu 18.04 or equivalent |

**Note:** End users do NOT need Python installed if you bundle a Python runtime (advanced configuration not covered here).

---

## Summary Commands

```bash
# Full build from scratch
pip install -e ".[dev]"
pip install -r web/backend/requirements.txt
cd web/frontend && npm install && npm run build && cd ../..
cd desktop && npm install

# Run in development
cd desktop && npm start

# Build for distribution
cd desktop && npm run dist        # Current platform
cd desktop && npm run dist:win    # Windows
cd desktop && npm run dist:mac    # macOS
cd desktop && npm run dist:linux  # Linux
```

---

## Additional Resources

- [Electron Documentation](https://www.electronjs.org/docs)
- [electron-builder Documentation](https://www.electron.build/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Vite Documentation](https://vitejs.dev/)
