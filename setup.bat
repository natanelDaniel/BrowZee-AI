@echo off
:: הגדרת משתנים
set PYTHON_URL=https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
set PYTHON_INSTALL_PATH=C:\BrowZeeAI\Python
set BROWZEE_DIR=%USERPROFILE%\BrowZeeAI
set SERVER_SCRIPT=%BROWZEE_DIR%\ai_server.py

:: בדיקה אם Python כבר מותקן
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing Python...
    mkdir %PYTHON_INSTALL_PATH%
    powershell -command "(New-Object Net.WebClient).DownloadFile('%PYTHON_URL%', '%TEMP%\python_installer.exe')"
    start /wait %TEMP%\python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 TargetDir=%PYTHON_INSTALL_PATH%
    del %TEMP%\python_installer.exe
)

:: יצירת תיקיית ההתקנה
mkdir %BROWZEE_DIR%

:: התקנת חבילות נדרשות
echo Installing requirements...
%PYTHON_INSTALL_PATH%\python -m pip install --upgrade pip
%PYTHON_INSTALL_PATH%\python -m pip install fastapi uvicorn langchain_openai browser_use python-dotenv

:: הוספת שרת AI לסטארטאפ (כדי שירוץ ברקע)
echo Creating startup task...
schtasks /create /tn "BrowZeeAI_Server" /tr "\"%PYTHON_INSTALL_PATH%\python\" %SERVER_SCRIPT%" /sc onlogon /rl highest /f

:: סיום
echo Setup completed! Now you can start BrowZee AI.
pause
