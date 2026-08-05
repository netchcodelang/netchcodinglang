#!/usr/bin/env python3
"""
Netch Package Manager
Usage:
    python netch_pkg.py install <packagename>
    python netch_pkg.py remove  <packagename>
    python netch_pkg.py list
    python netch_pkg.py info    <packagename>
"""

import sys, os, json, urllib.request, shutil, zipfile

NETCH_DIR     = os.path.join(os.path.expanduser("~"), "Netch2")
PACKAGES_DIR  = os.path.join(NETCH_DIR, "packages")
PKG_INDEX_URL = "https://raw.githubusercontent.com/netchcodelang/netchcodinglang/main/packages/index.json"
PKG_BASE_URL  = "https://raw.githubusercontent.com/netchcodelang/netchcodinglang/main/packages/"

os.makedirs(PACKAGES_DIR, exist_ok=True)

def banner():
    print("\u2501"*44)
    print("  \U0001f4e6  Netch Package Manager")
    print("\u2501"*44)

def fetch_index():
    try:
        req = urllib.request.Request(PKG_INDEX_URL, headers={"User-Agent":"netch-pkg"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  Error: Could not reach package index: {e}")
        print("      Check your internet connection.")
        sys.exit(1)

def install(pkg_name):
    banner()
    print(f"  Looking for package: {pkg_name}")
    index = fetch_index()
    if pkg_name not in index:
        print(f"\n  Package \"{pkg_name}\" not found.")
        print(f"  Available: {', '.join(index.keys())}")
        print("  Request one at: reddit.com/r/netchcoding2")
        sys.exit(1)
    pkg_info = index[pkg_name]
    pkg_dir  = os.path.join(PACKAGES_DIR, pkg_name)
    if os.path.exists(pkg_dir):
        print(f"  \"{pkg_name}\" is already installed.")
        return
    print(f"  Downloading {pkg_name} v{pkg_info.get('version','?')}...")
    os.makedirs(pkg_dir, exist_ok=True)
    pkg_file_url  = PKG_BASE_URL + pkg_info["file"]
    pkg_file_path = os.path.join(pkg_dir, pkg_info["file"])
    try:
        urllib.request.urlretrieve(pkg_file_url, pkg_file_path)
    except Exception as e:
        print(f"  Download failed: {e}")
        shutil.rmtree(pkg_dir, ignore_errors=True)
        sys.exit(1)
    try:
        with zipfile.ZipFile(pkg_file_path, 'r') as z:
            z.extractall(pkg_dir)
        os.remove(pkg_file_path)
    except zipfile.BadZipFile:
        pass  # raw file, keep as is
    meta = {**pkg_info, "name": pkg_name, "installed": True}
    with open(os.path.join(pkg_dir, "package.json"), 'w') as f:
        json.dump(meta, f, indent=2)
    print(f"  Installed: {pkg_name} v{pkg_info.get('version','?')}")
    if pkg_info.get("description"):
        print(f"  {pkg_info['description']}")
    print(f"\n  Add to your .ntch file:")
    for line in pkg_info.get("usage", [f"importpkg {pkg_name}"]):
        print(f"      {line}")
    print()

def remove(pkg_name):
    banner()
    pkg_dir = os.path.join(PACKAGES_DIR, pkg_name)
    if not os.path.exists(pkg_dir):
        print(f"  Package \"{pkg_name}\" is not installed.")
        return
    shutil.rmtree(pkg_dir)
    print(f"  Removed: {pkg_name}")

def list_packages():
    banner()
    installed = [d for d in os.listdir(PACKAGES_DIR)
                 if os.path.isdir(os.path.join(PACKAGES_DIR, d))]
    if not installed:
        print("  No packages installed.")
        print("  Try: python netch_pkg.py install customwindowtitle")
    else:
        print(f"  Installed packages ({len(installed)}):")
        for pkg in installed:
            meta_path = os.path.join(PACKAGES_DIR, pkg, "package.json")
            if os.path.exists(meta_path):
                with open(meta_path) as f:
                    meta = json.load(f)
                print(f"    {pkg} v{meta.get('version','?')} - {meta.get('description','')}")
            else:
                print(f"    {pkg}")
    print()

def info(pkg_name):
    banner()
    index = fetch_index()
    if pkg_name not in index:
        print(f"  Package \"{pkg_name}\" not found.")
        return
    pkg = index[pkg_name]
    print(f"  {pkg_name}")
    print(f"  Version:     {pkg.get('version','?')}")
    print(f"  Description: {pkg.get('description','')}")
    print(f"  Author:      {pkg.get('author','')}")
    installed = os.path.exists(os.path.join(PACKAGES_DIR, pkg_name))
    print(f"  Installed:   {'Yes' if installed else 'No'}")
    print()

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(0)
    cmd = sys.argv[1].lower()
    if cmd == 'install':
        if len(sys.argv) < 3: print("Usage: netch_pkg.py install <name>"); sys.exit(1)
        install(sys.argv[2])
    elif cmd == 'remove':
        if len(sys.argv) < 3: print("Usage: netch_pkg.py remove <name>"); sys.exit(1)
        remove(sys.argv[2])
    elif cmd == 'list':
        list_packages()
    elif cmd == 'info':
        if len(sys.argv) < 3: print("Usage: netch_pkg.py info <name>"); sys.exit(1)
        info(sys.argv[2])
    else:
        print(f"  Unknown command: {cmd}")
        print("  Commands: install, remove, list, info")

if __name__ == '__main__':
    main()
