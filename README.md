# SmartCapture Pro 📸

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/basecore/SmartCapture-Pro)
[![AI Generated](https://img.shields.io/badge/AI_Generated-Gemini_3.1_Pro-20B8D9?style=for-the-badge&logo=google)](https://gemini.google.com/)
[![License: MIT](https://img.shields.io/badge/License-Testing_Only-yellow.svg?style=for-the-badge)](https://github.com/basecore/SmartCapture-Pro)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-v25.5-0078D7?style=for-the-badge)](https://github.com/basecore/SmartCapture-Pro)

> **⚠️ Disclaimer: For testing purposes only! (Nur zu Testzwecken verwenden!)**

SmartCapture Pro is a modern Python-based desktop application designed specifically for capturing screen regions and extracting text in real-time. It is highly optimized for capturing live transcripts from **Microsoft Teams meetings** using Optical Character Recognition (OCR).

Created by [@basecore](https://github.com/basecore)

---

## 📸 Screenshots

### The Application (GUI)
![SmartCapture Pro GUI](https://raw.githubusercontent.com/basecore/SmartCapture-Pro/main/assets/screenshot_teams1.png)

### Capturing MS Teams Transcripts
![Teams Capture](https://raw.githubusercontent.com/basecore/SmartCapture-Pro/main/assets/screenshot_teams2.png)

---

## 🆕 Changelog

### v25.5 – 18.06.2026
- 📸 **Screenshots**: Dateiname enthält jetzt automatisch den Meeting-Titel (aus dem "AI Context"-Tab)
  - Neu: `screen_Projekt_Update_2026-06-18_09-30-00.png`
  - Alt: `screen_2026-06-18_09-30-00.png`
- 📄 **Export-TXT Dateiname**: Enthält jetzt Meeting-Titel + Aufnahme-Beginn (erster Screenshot)
  - Neu: `Export_Projekt_Update_Beginn-2026-06-18_09-30_2026-06-18_09-45.txt`
  - Alt: `Export_2026-06-18_09-45.txt`
- 📋 **Export-TXT Kopfzeile**: Zeigt im Dokument direkt Meeting-Titel und Aufnahme-Beginn an
  ```
  === ORIGINAL OCR DATA START ===
  Meeting: Projekt Update Q2
  Aufnahme-Beginn: 18.06.2026 09:30:00
  Export erstellt: 2026-06-18_09-45 | Settings: jpn+eng, --psm 6, scale2x
  ```
- 🕐 **Aufnahme-Startzeitstempel**: Wird automatisch beim ersten gespeicherten Screenshot der Sitzung gesetzt

### v25.4 – 08.06.2026
- Hintergrund-Capture (verdeckte Fenster)
- Konfigurierbarer AI-Chat URL und Browser
- Automatische Tesseract-Installation ohne Admin-Rechte
- Bilinguales UI (DE/EN Toggle)

---

## ✨ Features
- 🎯 **Präzise Bereichsauswahl:** Zeichne einen Rahmen über das MS Teams Transkript oder jeden anderen Text
- 📝 **Live OCR:** Automatische Texterkennung aus dem gewählten Bereich via Tesseract OCR
- 🏷️ **Smarte Dateinamen:** Screenshots und Exports werden automatisch mit Meeting-Titel und Zeitstempel benannt
- 🌍 **Bilingual:** Schneller Wechsel zwischen Deutsch (DE) und Englisch (EN)
- 🤖 **AI Integration:** Extrahierte Texte direkt an ChatGPT, Gemini, Claude etc. weiterleiten
- ⚙️ **Konfigurierbar:** Browser, AI-URL, OCR-Sprache und Layout-Modus einstellbar
- 🔄 **Auto-Install:** Alle Abhängigkeiten (inkl. Tesseract OCR) werden beim ersten Start automatisch installiert

---

## 🚀 Schnellstart (Windows)

### Einfachste Methode – Per Doppelklick starten:
1. Lade beide Dateien in denselben Ordner herunter:
   - [`SmartCapture_Pro_255_2026-06-18.py`](https://github.com/basecore/SmartCapture-Pro/blob/main/SmartCapture_Pro_255_2026-06-18.py)
   - [`SmartCapture_Pro_255_Start.bat`](https://github.com/basecore/SmartCapture-Pro/blob/main/SmartCapture_Pro_255_Start.bat)
2. **Doppelklick auf `SmartCapture_Pro_255_Start.bat`** → fertig!

> Die `.bat`-Datei prüft Python, installiert alle Libraries automatisch und startet das Tool.

### Voraussetzungen
- **Python 3.8+** (mit `tcl/tk and IDLE` Option, ist standardmäßig aktiviert)
- Windows 10 / 11

### Via Terminal
```bash
git clone https://github.com/basecore/SmartCapture-Pro.git
cd SmartCapture-Pro
py SmartCapture_Pro_255_2026-06-18.py
```

---

## 🛠️ Benutzung
1. **Meeting-Titel setzen** im Tab "🤖 AI Context" → Feld "Meeting Titel" (z.B. `Projekt Update Q2`)
2. **Aufnahmebereich definieren**: Blauen Rahmen über das Teams-Transkript ziehen
3. **Aufnahme starten** → Screenshots werden automatisch mit Meeting-Titel im Dateinamen gespeichert
4. **OCR & Export**: Im Tab "📝 OCR & Export" die Texterkennung starten
5. **AI Chat**: Extrahierten Text direkt in ChatGPT/Gemini etc. einfügen

---

## 🤝 Contributing
Beiträge, Issues und Feature-Requests sind willkommen! → [Issues-Seite](https://github.com/basecore/SmartCapture-Pro/issues)

## 📜 Lizenz
Dieses Projekt ist ausschließlich für Test- und Demonstrationszwecke.
