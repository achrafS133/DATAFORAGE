@echo off
cls
echo ========================================
echo        DATAFORAGE QUICK START        
echo ========================================
echo.
echo 1. Start Main TUI Application (DB Seeder)
echo 2. Start Universal Data Generator (CSV)
echo 3. Run Setup (Install Deps)
echo 4. Reset Database
echo 5. Exit
echo.
set /p choice="Select an option (1-5): "

if "%choice%"=="1" (
    python main.py
) else if "%choice%"=="2" (
    python universal_generator.py
) else if "%choice%"=="3" (
    pip install -r requirements.txt
) else if "%choice%"=="4" (
    python setup_db.py
) else if "%choice%"=="5" (
    exit
) else (
    echo Invalid choice.
    pause
    goto start
)

:start
@echo off
cls
echo ========================================
echo        DATAFORAGE QUICK START        
echo ========================================
echo.
echo 1. Start Main TUI Application (DB Seeder)
echo 2. Start Universal Data Generator (CSV)
echo 3. Run Setup (Install Deps)
echo 4. Reset Database
echo 5. Exit
echo.
set /p choice="Select an option (1-5): "

if "%choice%"=="1" (
    python main.py
) else if "%choice%"=="2" (
    python universal_generator.py
) else if "%choice%"=="3" (
    pip install -r requirements.txt
) else if "%choice%"=="4" (
    python setup_db.py
) else if "%choice%"=="5" (
    exit
) else (
    echo Invalid choice.
    pause
    goto start
)
