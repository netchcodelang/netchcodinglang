@echo off
:: Netch CLI - An Aerotion Production
setlocal

set NETCH_DIR=%USERPROFILE%\Netch2
set NETCH_PKG=%NETCH_DIR%\netch_pkg.py
set NETCH_INT=%NETCH_DIR%\interpreter.py

if "%1"=="" goto help

:: netch run yourfile.ntch
if /i "%1"=="run" (
    if "%2"=="" (
        echo [Netch] Usage: netch run yourfile.ntch
        exit /b 1
    )
    python "%NETCH_INT%" %2
    exit /b
)

:: netch pkg install/remove/list/info
if /i "%1"=="pkg" (
    if "%2"=="" (
        echo [Netch] Usage: netch pkg install ^<name^>
        echo         Usage: netch pkg remove  ^<name^>
        echo         Usage: netch pkg list
        echo         Usage: netch pkg info    ^<name^>
        exit /b 1
    )
    python "%NETCH_PKG%" %2 %3 %4
    exit /b
)

:: netch version
if /i "%1"=="version" (
    python -c "exec(open('%NETCH_INT%').read().split('if __name__')[0]); print('Netch 2 v' + NETCH_VERSION)"
    exit /b
)

:: netch new myapp.ntch
if /i "%1"=="new" (
    if "%2"=="" (
        echo [Netch] Usage: netch new yourfile.ntch
        exit /b 1
    )
    set NEWFILE=%2
    if not "%NEWFILE:~-5%"==".ntch" set NEWFILE=%NEWFILE%.ntch
    if exist "%NEWFILE%" (
        echo [Netch] File already exists: %NEWFILE%
        exit /b 1
    )
    (
        echo ^<using.ntch^>
        echo.
        echo print^("Hello from Netch 2!"^)
    ) > "%NEWFILE%"
    echo [Netch] Created: %NEWFILE%
    exit /b
)

:: netch update
if /i "%1"=="update" (
    echo [Netch] Checking for updates...
    python -c "
import urllib.request, json
try:
    req = urllib.request.Request('https://api.github.com/repos/netchcodelang/netchcodinglang/releases/latest', headers={'User-Agent':'netch2'})
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.loads(r.read())
        latest = data.get('tag_name','').lstrip('v')
        print(f'Latest version: v{latest}')
        print(f'Download: https://github.com/netchcodelang/netchcodinglang')
except:
    print('Could not check for updates. Check your internet connection.')
"
    exit /b
)

:: netch help
:help
echo.
echo  Netch 2 CLI - An Aerotion Production
echo  =====================================
echo.
echo  Commands:
echo    netch run ^<file.ntch^>          Run a Netch 2 script
echo    netch new ^<file.ntch^>          Create a new Netch 2 script
echo    netch pkg install ^<name^>       Install a package
echo    netch pkg remove  ^<name^>       Uninstall a package
echo    netch pkg list                 List installed packages
echo    netch pkg info    ^<name^>       Info about a package
echo    netch version                  Show Netch version
echo    netch update                   Check for updates
echo    netch help                     Show this message
echo.
echo  Examples:
echo    netch run myapp.ntch
echo    netch pkg install customwindowtitle
echo    netch new myapp
echo.
echo  Community: reddit.com/r/netchcoding2
echo  GitHub:    github.com/netchcodelang/netchcodinglang
echo.
exit /b
