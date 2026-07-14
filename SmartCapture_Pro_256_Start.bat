@echo off
title SmartCapture Pro v25.6 - Launcher
color 0A

echo ========================================================
echo   SmartCapture Pro v25.6 - Startvorgang / Startup
echo   Datum / Date: 14.07.2026
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
echo [NEU v25.6 / NEW v25.6]:
echo   - Session-Ordner pro Aufnahme mit Datum + Meeting-Titel
echo     Bsp: captured_screens\2026-07-14_Project_Update_Q2\
echo   - Screenshots und Export-TXT werden gemeinsam im Session-Ordner gespeichert
echo   - Manueller OCR-Import kann den Meeting-Titel aus Bildnamen ableiten
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
echo [START] DE: Starte SmartCapture Pro v25.6...
echo [START] EN: Starting SmartCapture Pro v25.6...
echo.

:: Startet das Hauptskript v25.6
py "SmartCapture_Pro_256_2026-07-14.py"

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo ========================================================
    echo [FEHLER / ERROR] Das Programm wurde unerwartet beendet.
    echo                  The program terminated unexpectedly.
    echo ========================================================
    pause
)
