#!/usr/bin/env python3
"""
Setup script for the Data Cleaner desktop application.
Run this to prepare everything for running the Electron app.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None, description=None):
    """Run a command and print status."""
    if description:
        print(f"\n{'='*60}")
        print(f"  {description}")
        print('='*60)
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    
    if result.returncode != 0:
        print(f"❌ Command failed with code {result.returncode}")
        return False
    
    print("✅ Done")
    return True

def main():
    # Get paths
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    web_dir = project_root / "web"
    frontend_dir = web_dir / "frontend"
    backend_dir = web_dir / "backend"
    
    print("="*60)
    print("  Data Cleaner Desktop App Setup")
    print("="*60)
    
    # Check Python
    print("\n🐍 Checking Python...")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"   Found: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Python not found: {e}")
        return 1
    
    # Check Node.js
    print("\n📦 Checking Node.js...")
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"   Found: Node.js {result.stdout.strip()}")
    except Exception:
        print("❌ Node.js not found. Please install from https://nodejs.org")
        return 1
    
    # Install Python dependencies
    if not run_command(
        [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
        cwd=project_root,
        description="Installing Python package"
    ):
        return 1
    
    if not run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        cwd=backend_dir,
        description="Installing backend dependencies"
    ):
        return 1
    
    # Install frontend dependencies
    if not run_command(
        ["npm", "install"],
        cwd=frontend_dir,
        description="Installing frontend dependencies"
    ):
        return 1
    
    # Build frontend
    if not run_command(
        ["npm", "run", "build"],
        cwd=frontend_dir,
        description="Building frontend"
    ):
        return 1
    
    # Install Electron dependencies
    if not run_command(
        ["npm", "install"],
        cwd=script_dir,
        description="Installing Electron dependencies"
    ):
        return 1
    
    print("\n" + "="*60)
    print("  ✅ Setup Complete!")
    print("="*60)
    print("\nTo run the desktop app:")
    print(f"  cd {script_dir}")
    print("  npm start")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
