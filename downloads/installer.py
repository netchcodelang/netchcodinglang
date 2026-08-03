"""
netch installer
----------------
Run this ONCE on your PC (as Administrator) to set up netch so you can
just double-click a .netch file, or type its name in Command Prompt,
and it runs automatically. No more "python interpreter.py file.netch".

This installer downloads interpreter.py straight from the netch GitHub
repo, so you don't need to have it saved locally first.

HOW TO USE:
1. Right-click Command Prompt -> "Run as Administrator"
2. Run: python installer.py
   (or just double-click this file if Python is set to run .py files)
"""

import os
import subprocess
import sys
import ctypes
import json
import urllib.request

GITHUB_REPO = "cutestcookie9-cmd/netch.dot"
GITHUB_BRANCH = "main"
GITHUB_FILE_PATH = "interpreter.py"
INTERPRETER_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_FILE_PATH}"


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def download_interpreter(dest_path):
    print(f"Downloading interpreter.py from {INTERPRETER_URL} ...")
    try:
        urllib.request.urlretrieve(INTERPRETER_URL, dest_path)
        print("Downloaded interpreter.py")
        return True
    except Exception as e:
        print(f"[error] couldn't download interpreter.py: {e}")
        print("Check your internet connection, or that the repo/link is still correct.")
        return False


def log_commit_date(install_dir):
    """Records which version of interpreter.py we just installed, so the interpreter
    can later tell if a newer one has been pushed to GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/commits?path={GITHUB_FILE_PATH}&sha={GITHUB_BRANCH}&per_page=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "netch-installer"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        commit_date = data[0]["commit"]["committer"]["date"]
        with open(os.path.join(install_dir, "version.txt"), "w") as f:
            f.write(commit_date)
        print(f"Logged installed version date: {commit_date}")
    except Exception as e:
        print(f"[warning] couldn't log the commit date: {e}")
        print("netch will still work, it just won't be able to auto-detect updates until you reinstall.")


def install_windows():
    if not is_admin():
        print("Please re-run this as Administrator (needed to edit PATH and file associations).")
        print("Right-click Command Prompt -> 'Run as Administrator', then run this again.")
        return

    install_dir = r"C:\netch"
    print(f"Installing netch to {install_dir} ...")

    os.makedirs(install_dir, exist_ok=True)

    dest_interpreter = os.path.join(install_dir, "interpreter.py")

    if not download_interpreter(dest_interpreter):
        return

    log_commit_date(install_dir)

    # create the launcher .bat
    launcher_path = os.path.join(install_dir, "netch.bat")
    with open(launcher_path, "w") as f:
        f.write('@echo off\n')
        f.write(f'python "{dest_interpreter}" %1\n')
        f.write('pause\n')
    print("Created launcher (netch.bat)")

    # add to PATH (current user, persists across restarts)
    try:
        subprocess.run(
            ["setx", "PATH", f"%PATH%;{install_dir}"],
            shell=True, check=True, capture_output=True
        )
        print("Added netch to PATH")
    except Exception as e:
        print(f"[warning] couldn't update PATH automatically: {e}")
        print(f"You can add it manually: {install_dir}")

    # associate .netch files with the launcher
    try:
        subprocess.run(["cmd", "/c", "assoc", ".netch=netchfile"], check=True)
        subprocess.run(["cmd", "/c", f'ftype netchfile="{launcher_path}" "%1"'], check=True)
        print("Associated .netch files with netch")
    except Exception as e:
        print(f"[warning] couldn't set file association automatically: {e}")

    print("\nDone! Restart Command Prompt (or your PC) for PATH changes to fully apply.")
    print("From now on you can just double-click any .netch file, or run:")
    print("  yourfile.netch")
    print("from any Command Prompt window.")
    print("\nnetch will now automatically check GitHub for newer versions each time you")
    print("run a .netch file, and offer to auto-update itself if one is found.")


def install_unix():
    # Installs to the user's home folder — no sudo/admin needed, since that's
    # often locked down (e.g. no apt/root access) even when Python itself works fine.
    install_dir = os.path.expanduser("~/.netch")
    print(f"Installing netch to {install_dir} ...")
    os.makedirs(install_dir, exist_ok=True)

    dest_interpreter = os.path.join(install_dir, "interpreter.py")
    if not download_interpreter(dest_interpreter):
        return

    log_commit_date(install_dir)

    # create the launcher shell script
    launcher_path = os.path.join(install_dir, "netch")
    with open(launcher_path, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write(f'python3 "{dest_interpreter}" "$@"\n')
    os.chmod(launcher_path, 0o755)
    print("Created launcher (netch)")

    # add ~/.netch to PATH by appending to whichever shell rc file exists
    path_line = f'\n# added by netch installer\nexport PATH="$PATH:{install_dir}"\n'
    rc_candidates = ["~/.bashrc", "~/.zshrc", "~/.profile"]
    updated_any = False
    for rc in rc_candidates:
        rc_path = os.path.expanduser(rc)
        if os.path.exists(rc_path):
            try:
                with open(rc_path, "r") as f:
                    already_there = install_dir in f.read()
                if not already_there:
                    with open(rc_path, "a") as f:
                        f.write(path_line)
                    print(f"Added netch to PATH in {rc}")
                updated_any = True
            except Exception as e:
                print(f"[warning] couldn't update {rc}: {e}")

    if not updated_any:
        print(f"[warning] couldn't find a shell rc file to update automatically.")
        print(f"Add this line to your shell's config file yourself:")
        print(f'  export PATH="$PATH:{install_dir}"')

    print("\nDone! Close and reopen your terminal (or run 'source ~/.bashrc') for PATH changes to apply.")
    print("From now on you can just run:")
    print("  netch yourfile.netch")
    print("from any terminal window.")
    print("\nnetch will now automatically check GitHub for newer versions each time you")
    print("run a .netch file, and offer to auto-update itself if one is found.")


def main():
    if os.name == "nt":
        install_windows()
    else:
        install_unix()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[error] something went wrong: {e}")
    input("\nPress Enter to close this window...")
