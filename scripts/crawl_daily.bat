@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
REM Miru Election Intel — Daily Crawler
REM Scheduled: 11:00 KST (02:00 UTC) daily via Windows Task Scheduler
REM Manual run: double-click or: scripts\crawl_daily.bat

set REPO=C:\Users\KIM\Downloads\miru-election-intel
set PYTHON=C:\Users\KIM\AppData\Local\Python\bin\python.exe
set LOG=%REPO%\logs\crawl_%date:~0,4%%date:~5,2%%date:~8,2%.log

REM Load .env if it exists
if exist "%REPO%\.env" (
    for /f "usebackq tokens=1,2 delims==" %%A in ("%REPO%\.env") do (
        set %%A=%%B
    )
)

REM Create logs directory
if not exist "%REPO%\logs" mkdir "%REPO%\logs"

echo [%date% %time%] === Miru Election Intel Daily Crawl === >> "%LOG%"

REM Step 1: Static portals
echo [%date% %time%] Running static parsers... >> "%LOG%"
"%PYTHON%" "%REPO%\crawler\crawl.py" --mode static --delay 2.0 >> "%LOG%" 2>&1

REM Step 2: Playwright portals
echo [%date% %time%] Running playwright parsers... >> "%LOG%"
"%PYTHON%" "%REPO%\crawler\crawl.py" --mode playwright --delay 3.0 >> "%LOG%" 2>&1

REM Step 3: Generate JS data file for search UI
echo [%date% %time%] Generating tenders_data.js... >> "%LOG%"
"%PYTHON%" "%REPO%\scripts\gen_tenders_js.py" >> "%LOG%" 2>&1

echo [%date% %time%] Done. >> "%LOG%"
