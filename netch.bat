@echo off
:: Netch 2 CLI - An Aerotion Production
setlocal EnableDelayedExpansion

set NETCH_DIR=%USERPROFILE%\Netch2
set NETCH_PKG=%NETCH_DIR%\netch_pkg.py
set NETCH_INT=%NETCH_DIR%\interpreter.py

if "%1"=="" goto help

:: ── netch list pkgs all ──
if /i "%1"=="list" (
    if /i "%2"=="pkgs" (
        if /i "%3"=="all" (
            echo.
            echo  [Netch] Fetching all packages from GitHub...
            python -c "
import urllib.request, json
try:
    req = urllib.request.Request(
        'https://raw.githubusercontent.com/netchcodelang/netchcodinglang/main/packages/index.json',
        headers={'User-Agent':'netch2'})
    with urllib.request.urlopen(req, timeout=8) as r:
        index = json.loads(r.read())
    print()
    print('  All Official Netch Packages')
    print('  ============================')
    for name, info in index.items():
        print(f'  {name} v{info.get(chr(118)+chr(101)+chr(114)+chr(115)+chr(105)+chr(111)+chr(110),"?")}'
              f' - {info.get("description","")}')
    print()
    print(f'  Total: {len(index)} package(s)')
    print('  Install any with: netch pkg install <name>')
    print()
except Exception as e:
    print(f'  Could not fetch package list: {e}')
    print('  Check your internet connection.')
"
            exit /b
        )
        echo.
        python "%NETCH_PKG%" list
        exit /b
    )
)

:: ── netch run <file.ntch> ──
if /i "%1"=="run" (
    if "%2"=="" (
        echo.
        echo  [Netch] No file specified.
        echo  Usage:  netch run yourfile.ntch
        echo.
        exit /b 1
    )
    if not exist "%2" (
        echo.
        echo  [Netch] File not found: %2
        echo  Make sure the file exists and you spelled it correctly.
        echo.
        exit /b 1
    )
    python "%NETCH_INT%" %2
    exit /b
)

:: ── netch pkg <command> ──
if /i "%1"=="pkg" (
    if "%2"=="" (
        echo.
        echo  [Netch] Package Manager
        echo  Usage:
        echo    netch pkg install ^<name^>    Install a package
        echo    netch pkg remove  ^<name^>    Uninstall a package
        echo    netch pkg list              List installed packages
        echo    netch pkg info    ^<name^>    Info about a package
        echo.
        exit /b 1
    )
    python "%NETCH_PKG%" %2 %3 %4
    exit /b
)

:: ── netch new <filename> ──
if /i "%1"=="new" (
    if "%2"=="" (
        echo.
        echo  [Netch] Usage: netch new yourfile
        echo  This creates a new blank .ntch script.
        echo.
        exit /b 1
    )
    set NEWFILE=%2
    echo !NEWFILE! | findstr /i "\.ntch" >nul || set NEWFILE=!NEWFILE!.ntch
    if exist "!NEWFILE!" (
        echo.
        echo  [Netch] File already exists: !NEWFILE!
        echo.
        exit /b 1
    )
    (
        echo ^<using.ntch^>
        echo.
        echo print^("Hello from Netch 2!"^)
    ) > "!NEWFILE!"
    echo.
    echo  [Netch] Created: !NEWFILE!
    echo  Run it with: netch run !NEWFILE!
    echo.
    exit /b
)

:: ── netch create-pkg ──
if /i "%1"=="create-pkg" (
    python "%NETCH_DIR%\netch_package_creator.py"
    exit /b
)

:: ── netch version ──
if /i "%1"=="version" (
    echo.
    python "%NETCH_INT%" --version 2>nul || (
        python -c "
import re
try:
    src = open(r'%NETCH_INT%').read()
    v = re.search(r'NETCH_VERSION\s*=\s*\"([^\"]+)\"', src)
    print('  Netch 2 v' + (v.group(1) if v else '?'))
    print('  An Aerotion Production')
    print('  github.com/netchcodelang/netchcodinglang')
except Exception as e:
    print('  Could not read version:', e)
"
    )
    echo.
    exit /b
)

:: ── netch update ──
if /i "%1"=="update" (
    echo.
    echo  [Netch] Checking for updates...
    python -c "
import urllib.request, json, re
try:
    src = open(r'%NETCH_INT%').read()
    vm  = re.search(r'NETCH_VERSION\s*=\s*\"([^\"]+)\"', src)
    cur = vm.group(1) if vm else '?'
    req = urllib.request.Request(
        'https://api.github.com/repos/netchcodelang/netchcodinglang/releases/latest',
        headers={'User-Agent':'netch2'})
    with urllib.request.urlopen(req, timeout=5) as r:
        data   = json.loads(r.read())
        latest = data.get('tag_name','').lstrip('v')
    if latest and latest != cur:
        print(f'  Update available! v{cur} -> v{latest}')
        print(f'  Download: https://github.com/netchcodelang/netchcodinglang')
    elif latest:
        print(f'  You are up to date! (v{cur})')
    else:
        print('  Could not determine latest version.')
except Exception as e:
    print(f'  Could not check for updates: {e}')
    print('  Check your internet connection.')
"
    echo.
    exit /b
)

:: ── netch help ──
if /i "%1"=="help" goto help

:: unknown command
echo.
echo  [Netch] Unknown command: %1
echo  Type "netch help" for a list of commands.
echo.
exit /b 1

:: ── HELP ──
:help
echo.
echo  ==========================================
echo   Netch 2 CLI  -  An Aerotion Production
echo  ==========================================
echo.
echo  Commands:
echo.
echo    netch run ^<file.ntch^>           Run a Netch 2 script
echo    netch new ^<name^>               Create a new blank .ntch script
echo.
echo    netch list pkgs all             List ALL packages on GitHub
echo    netch list pkgs                List installed packages
echo.
echo    netch pkg install ^<name^>       Install a package
echo    netch pkg remove  ^<name^>       Uninstall a package
echo    netch pkg list                 List installed packages
echo    netch pkg info    ^<name^>       Info about a package
echo.
echo    netch create-pkg               Open the Package Creator GUI
echo    netch version                  Show installed Netch version
echo    netch update                   Check for updates
echo    netch help                     Show this help screen
echo.
echo  Examples:
echo    netch run myapp.ntch
echo    netch new myapp
echo    netch pkg install customwindowtitle
echo    netch pkg install controllocalapps
echo.
echo  Community:  reddit.com/r/netchcoding2
echo  GitHub:     github.com/netchcodelang/netchcodinglang
echo.
exit /b

:: ── netch compiletoexe ──
if /i "%1"=="compiletoexe" (
    if "%2"=="" (
        echo.
        echo  [Netch] Usage: netch compiletoexe yourfile.ntch
        echo          Usage: netch compiletoexe yourfile.ntch --name "My App"
        echo          Usage: netch compiletoexe yourfile.ntch --output C:/releases
        echo          Usage: netch compiletoexe yourfile.ntch --icon myapp.ico
        echo          Usage: netch compiletoexe yourfile.ntch --folder
        echo.
        exit /b 1
    )
    python "%NETCH_DIR%\netch_compile.py" %2 %3 %4 %5 %6 %7
    exit /b
)

:: ── netch pkg update (auto-update all packages) ──
if /i "%1"=="pkg" if /i "%2"=="update" (
    echo.
    echo  [Netch] Checking for package updates...
    python -c "
import urllib.request, json, os, zipfile, shutil

NETCH_DIR    = os.path.join(os.path.expanduser('~'), 'Netch2')
PACKAGES_DIR = os.path.join(NETCH_DIR, 'packages')
INDEX_URL    = 'https://raw.githubusercontent.com/netchcodelang/netchcodinglang/main/packages/index.json'
PKG_BASE     = 'https://raw.githubusercontent.com/netchcodelang/netchcodinglang/main/packages/'

try:
    req = urllib.request.Request(INDEX_URL, headers={'User-Agent':'netch2'})
    with urllib.request.urlopen(req, timeout=10) as r:
        index = json.loads(r.read())
except Exception as e:
    print(f'  Could not reach package registry: {e}'); exit()

updated = 0
for pkg_name, pkg_info in index.items():
    pkg_dir  = os.path.join(PACKAGES_DIR, pkg_name)
    meta_path= os.path.join(pkg_dir, 'package.json')
    if not os.path.exists(meta_path): continue
    with open(meta_path) as f: local = json.load(f)
    local_v  = local.get('version','0.0.0')
    remote_v = pkg_info.get('version','0.0.0')
    if local_v != remote_v:
        print(f'  Updating {pkg_name}: v{local_v} -> v{remote_v}')
        url  = PKG_BASE + pkg_info['file']
        dest = os.path.join(pkg_dir, pkg_info['file'])
        urllib.request.urlretrieve(url, dest)
        try:
            with zipfile.ZipFile(dest,'r') as z: z.extractall(pkg_dir)
            os.remove(dest)
        except: pass
        local['version'] = remote_v
        with open(meta_path,'w') as f: json.dump(local,f,indent=2)
        updated += 1
    else:
        print(f'  {pkg_name}: up to date (v{local_v})')

print(f'\n  {updated} package(s) updated.')
"
    echo.
    exit /b
)

:: ── netch android (basic APK via buildozer) ──
if /i "%1"=="android" (
    if "%2"=="" (
        echo.
        echo  [Netch] Usage: netch android yourfile.ntch
        echo  [Netch] Requires: buildozer (pip install buildozer)
        echo  [Netch] Note: Android build works on Linux/WSL only.
        echo.
        exit /b 1
    )
    python "%NETCH_DIR%\netch_android.py" %2
    exit /b
)
