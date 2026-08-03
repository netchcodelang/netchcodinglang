@echo off
setlocal enabledelayedexpansion
title netch installer

:: ---- Re-launch elevated (as Administrator) if not already ----
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This needs to run as Administrator - requesting that now...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo ================================================
echo   netch installer
echo ================================================
echo.

:: ---- Check for Python ----
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo Python wasn't found on this PC. Downloading and installing it now...
    echo ^(this is a one-time thing^)
    echo.
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe' -OutFile '%TEMP%\python-setup.exe'"
    if not exist "%TEMP%\python-setup.exe" (
        echo [error] couldn't download Python. Check your internet connection and try again.
        goto :failure
    )
    echo Installing Python ^(this can take a minute^)...
    "%TEMP%\python-setup.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del "%TEMP%\python-setup.exe"
    echo.
    echo Python is installed. Please close this window and double-click
    echo install.bat again to finish setting up netch.
    echo ^(Windows needs a fresh window to pick up the new Python install.^)
    pause
    exit /b
)

echo Python found, continuing...
echo.

:: ---- Download the netch installer ----
echo Downloading netch installer...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cutestcookie9-cmd/netch.dot/releases/download/1.1/installer.py' -OutFile '%TEMP%\netch_installer.py'"
if not exist "%TEMP%\netch_installer.py" (
    echo [error] couldn't download the netch installer. Check your internet connection and try again.
    goto :failure
)

:: ---- Run it ----
echo Running netch installer...
python "%TEMP%\netch_installer.py"
if %errorLevel% neq 0 goto :failure

:: ---- Self-test: create and run a tiny test app ----
echo.
echo Testing the install with a sample app...
(
echo ^<using.netch^>
echo ^<window.using^>
echo(
echo window.title^("netch test"^)
echo window.text^("netch installed correctly!"^)
) > "%TEMP%\netch_install_test.netch"

if not exist "C:\netch\interpreter.py" (
    echo [error] the netch installer ran, but C:\netch\interpreter.py is missing.
    goto :failure
)

python "C:\netch\interpreter.py" "%TEMP%\netch_install_test.netch"
if %errorLevel% neq 0 goto :failure

echo.
echo ================================================
echo   All done! netch is installed and working.
echo   Close and reopen any Command Prompt window,
echo   then run:  netch yourfile.netch
echo ================================================
pause
exit /b

:failure
echo.
echo ================================================
echo   Something went wrong during setup.
echo.
echo   Please report this in the netch Discord server,
echo   or DM itz_night_fall on Discord for help.
echo ================================================
pause
exit /b
