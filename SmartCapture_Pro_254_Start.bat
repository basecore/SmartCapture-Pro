@echo off
title Schaeffler SmartCapture Pro - Launcher
color 0A

echo ========================================================
echo   SCHAEFFLER SmartCapture Pro - Startvorgang / Startup
echo   Datum / Date: 08.06.2026
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

:: --- NEU: PYTHON PRUEFUNG ---
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
echo [START] DE: Starte SmartCapture Pro...
echo [START] EN: Starting SmartCapture Pro...
echo.

:: Startet das Hauptskript
py "SmartCapture_Pro_254_2026-06-08.py"

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo ========================================================
    echo [FEHLER / ERROR] Das Programm wurde unerwartet beendet.
    echo                  The program terminated unexpectedly.
    echo ========================================================
    pause
)
