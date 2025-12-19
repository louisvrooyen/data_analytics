import os
import subprocess
import sys
import shutil
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

BASE_DIR = r"D:\Python\data_imports_project"
EXE_DIR = os.path.join(BASE_DIR, "exe")
EXE_NAME = "Dashboard.exe"
LAUNCHER_SCRIPT = os.path.join(BASE_DIR, "main_data", "main_launcher.py")
ICON_PATH = os.path.join(BASE_DIR, "Images", "dashboard.ico")
VERSION_FILE = os.path.join(BASE_DIR, "version_info.txt")
LOG_FILE = os.path.join(BASE_DIR, "build_log.txt")

EXE_PATH = os.path.join(EXE_DIR, EXE_NAME)

print("DEBUG: BUILD SCRIPT STARTED")
print(f"DEBUG: BASE_DIR = {BASE_DIR}")
print(f"DEBUG: LAUNCHER_SCRIPT = {LAUNCHER_SCRIPT}")
print(f"DEBUG: ICON_PATH = {ICON_PATH}")


# --------------------------------------------------
# VERSION HANDLING
# --------------------------------------------------

def read_version():
    print("DEBUG: Reading version file...")
    if not os.path.exists(VERSION_FILE):
        print("DEBUG: version_info.txt not found, using default 1.0.0")
        return "1.0.0"

    with open(VERSION_FILE, "r") as f:
        for line in f:
            if "FileVersion" in line:
                version = line.split("'")[3]
                print(f"DEBUG: Current version = {version}")
                return version

    print("DEBUG: Version not found in file, using default 1.0.0")
    return "1.0.0"


def increment_version(version):
    print(f"DEBUG: Incrementing version from {version}")
    major, minor, patch = map(int, version.split("."))
    patch += 1
    new_version = f"{major}.{minor}.{patch}"
    print(f"DEBUG: New version = {new_version}")
    return new_version


def write_version(new_version):
    print("DEBUG: Writing new version to version_info.txt...")
    content = f"""
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({new_version.replace('.', ',')},0),
    prodvers=({new_version.replace('.', ',')},0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0,0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', 'Sysman Group'),
          StringStruct('FileDescription', 'Dashboard Launcher'),
          StringStruct('FileVersion', '{new_version}'),
          StringStruct('InternalName', 'Dashboard'),
          StringStruct('OriginalFilename', 'Dashboard.exe'),
          StringStruct('ProductName', 'Dashboard'),
          StringStruct('ProductVersion', '{new_version}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    with open(VERSION_FILE, "w") as f:
        f.write(content)
    print("DEBUG: Version file updated.")


# --------------------------------------------------
# LOGGING
# --------------------------------------------------

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"LOG: {message}")


# --------------------------------------------------
# DELETE OLD EXE
# --------------------------------------------------

print("DEBUG: Checking for old EXE...")

if os.path.exists(EXE_PATH):
    print(f"DEBUG: Deleting old EXE at {EXE_PATH}")
    try:
        os.remove(EXE_PATH)
        log("Old EXE deleted.")
    except Exception as e:
        log(f"Failed to delete old EXE: {e}")
        sys.exit(1)
else:
    print("DEBUG: No old EXE found.")
    log("No previous EXE found.")


# --------------------------------------------------
# VERSION UPDATE
# --------------------------------------------------

old_version = read_version()
new_version = increment_version(old_version)
write_version(new_version)
log(f"Version updated: {old_version} -> {new_version}")


# --------------------------------------------------
# RUN PYINSTALLER
# --------------------------------------------------

print("DEBUG: Preparing PyInstaller command...")

cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--onefile",
    "--noconsole",
    "--name", "Dashboard",
    "--icon", ICON_PATH,
    "--version-file", VERSION_FILE,
    LAUNCHER_SCRIPT
]

print("DEBUG: RUNNING PYINSTALLER NOW...")
print("DEBUG: COMMAND:", " ".join(cmd))

try:
    result = subprocess.run(cmd, check=True)
except Exception as e:
    print("DEBUG: PYINSTALLER ERROR:", e)
    log(f"PyInstaller failed: {e}")
    sys.exit(1)


# --------------------------------------------------
# MOVE NEW EXE
# --------------------------------------------------

print("DEBUG: Checking for new EXE in /dist...")

dist_exe = os.path.join(BASE_DIR, "dist", "Dashboard.exe")

if os.path.exists(dist_exe):
    print("DEBUG: Moving EXE to /exe folder...")
    shutil.move(dist_exe, EXE_PATH)
    log(f"New EXE created at: {EXE_PATH}")
else:
    print("DEBUG: ERROR — EXE not found in /dist")
    log("Build failed: EXE not found in /dist")
    sys.exit(1)


# --------------------------------------------------
# BUILD COMPLETE POPUP
# --------------------------------------------------

print("DEBUG: Showing build complete popup...")

root = tk.Tk()
root.withdraw()

if messagebox.askyesno(
    "Build Complete",
    f"Dashboard v{new_version} built successfully.\n\nRun Dashboard now?"
):
    os.startfile(EXE_PATH)

root.destroy()