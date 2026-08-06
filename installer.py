import os
import sys
import urllib.request
import subprocess

GITHUB_RAW = "https://raw.githubusercontent.com/netchcodelang/netchcodinglang/main/interpreter.py"
INSTALL_DIR = os.path.join(os.path.expanduser("~"), "Netch2")
INTERPRETER_PATH = os.path.join(INSTALL_DIR, "interpreter.py")
RUNNER_PATH = os.path.join(INSTALL_DIR, "runnetch.bat")

def print_banner():
    print("=" * 50)
    print("   Netch 2 Installer - An Aerotion Production")
    print("=" * 50)
    print()

def check_python():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERROR: Netch 2 requires Python 3.8 or later.")
        print("Please update Python from https://python.org and try again.")
        input("Press Enter to exit...")
        sys.exit(1)
    print(f"Python {version.major}.{version.minor} detected. Good to go!")

def install_dependencies():
    print("Checking dependencies...")
    try:
        import tkinter
        print("tkinter: OK")
    except ImportError:
        print("tkinter not found. Please reinstall Python with tkinter support.")
        print("Download from https://python.org and check 'tcl/tk' during install.")
        input("Press Enter to exit...")
        sys.exit(1)

def download_interpreter():
    print(f"Downloading Netch 2 interpreter...")
    os.makedirs(INSTALL_DIR, exist_ok=True)
    try:
        urllib.request.urlretrieve(GITHUB_RAW, INTERPRETER_PATH)
        print("Download complete!")
    except Exception as e:
        print(f"Download failed: {e}")
        print("Please check your internet connection.")
        print("You can also manually download interpreter.py from:")
        print("https://github.com/netchcodelang/netchcodinglang")
        input("Press Enter to exit...")
        sys.exit(1)

def create_runner():
    # Download netch.bat CLI
    netch_bat_url = "https://raw.githubusercontent.com/netchcodelang/netchcodinglang/main/netch.bat"
    netch_bat_path = os.path.join(INSTALL_DIR, "netch.bat")
    try:
        urllib.request.urlretrieve(netch_bat_url, netch_bat_path)
        print("netch CLI installed!")
    except Exception:
        # fallback: write a basic one
        bat_content = f'@echo off\nif "%1"=="run" (python "{INTERPRETER_PATH}" %2) else (python "{INTERPRETER_PATH}" %2)'
        with open(netch_bat_path, "w") as f:
            f.write(bat_content)
        print("netch CLI created (basic fallback)!")

def add_to_path():
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Environment", 0, winreg.KEY_ALL_ACCESS)
        current_path, _ = winreg.QueryValueEx(key, "PATH")
        if INSTALL_DIR not in current_path:
            new_path = current_path + ";" + INSTALL_DIR
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            print("Added Netch to PATH!")
        else:
            print("Netch already in PATH.")
    except Exception as e:
        print(f"Could not add to PATH automatically: {e}")
        print(f"You can manually add {INSTALL_DIR} to your PATH.")

def run_test():
    test_file = os.path.join(INSTALL_DIR, "hello.ntch")
    with open(test_file, 'w') as f:
        f.write('<using.ntch>\nprint("Netch 2 is working!")\n')
    result = subprocess.run([sys.executable, INTERPRETER_PATH, test_file],
                            capture_output=True, text=True)
    if "Netch 2 is working!" in result.stdout:
        print("Test passed! Netch 2 is installed correctly.")
    else:
        print("Test failed. Something went wrong.")
        print(result.stderr)

def main():
    print_banner()
    print("Installing Netch 2...\n")
    check_python()
    install_dependencies()
    download_interpreter()
    create_runner()
    add_to_path()
    run_test()
    print()
    print("=" * 50)
    print("   Netch 2 installed successfully!")
    print(f"   Location: {INSTALL_DIR}")
    print()
    print("   To run a .ntch file:")
    print('   python interpreter.py yourfile.ntch')
    print()
    print("   Join the community: reddit.com/r/netchcoding2")
    print("=" * 50)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
