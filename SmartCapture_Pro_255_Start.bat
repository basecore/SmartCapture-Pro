@echo off
title SmartCapture Pro v25.5 - Launcher
color 0A

echo ========================================================
echo   SmartCapture Pro v25.5 - Startvorgang / Startup
echo   Datum / Date: 18.06.2026
echo ========================================================
echo.
echo [INFO] DE: Hinweis zur Texterkennung (OCR):
echo            Dieses Tool nutzt 'Tesseract OCR', eine sichere und 
echo            weltweit bewaehrte Open-Source-Software, die von der 
echo            Universitaet Mannheim bereitgestellt wird.
echo            Falls nicht vorhanden, erfolgt eine stille Installation.
echo.
echo [INFO] EN: Notice regarding Text Recognition (OCR):
echo            This tool uses 'Tesseract OCR', a secure and globally 
echo            proven open-source software provided by the University 
echo            of Mannheim.
echo            If not present, it will be installed silently.
echo.
echo [NEU v25.5 / NEW v25.5]:
echo   - Screenshots: Dateiname enthaelt jetzt den Meeting-Titel
echo     Bsp: screen_Projekt_Update_2026-06-18_09-30-00.png
echo   - Export-TXT: Dateiname enthaelt Titel + Aufnahme-Beginn
echo     Bsp: Export_Projekt_Update_Beginn-2026-06-18_09-30_..._..txt
echo   - Export-TXT: Kopfzeile zeigt Meeting-Titel und Aufnahme-Beginn
echo.

:: --- PYTHON PRUEFUNG ---
where py >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo ========================================================
    echo [FEHLER] Es wurde kein Python auf diesem System gefunden!
    echo          Bitte fordere ueber die IT Python an.
    echo          Empfohlene Version: Python 3.11.5
    echo.
    echo [ERROR]  No Python installation found on this system!
    echo          Please request Python from IT.
    echo          Recommended version: Python 3.11.5
    echo ========================================================
    pause
    exit /b
)

echo [INFO] DE: Setze Arbeitsverzeichnis...
echo [INFO] EN: Setting working directory...
cd /d "%~dp0"

echo [INFO] DE: Pruefe und installiere Python-Bibliotheken...
echo [INFO] EN: Checking and installing Python libraries...
py -m pip install pytesseract Pillow natsort mss pywin32 --disable-pip-version-check

echo.
echo [START] DE: Starte SmartCapture Pro v25.5...
echo [START] EN: Starting SmartCapture Pro v25.5...
echo.

:: Startet das Hauptskript v25.5
py "SmartCapture_Pro_255_2026-06-18.py"

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo ========================================================
    echo [FEHLER / ERROR] Das Programm wurde unerwartet beendet.
    echo                  The program terminated unexpectedly.
    echo ========================================================
    pause
)
