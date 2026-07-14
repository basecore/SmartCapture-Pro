# SmartCapture Pro 📸

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/basecore/SmartCapture-Pro)
[![License: Testing Only](https://img.shields.io/badge/License-Testing_Only-yellow.svg?style=for-the-badge)](https://github.com/basecore/SmartCapture-Pro)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows_10%2F11-0078D7?style=for-the-badge&logo=windows)](https://www.microsoft.com/windows)
[![Version](https://img.shields.io/badge/Version-v25.7-0078D7?style=for-the-badge)](https://github.com/basecore/SmartCapture-Pro)

> **⚠️ Disclaimer: For testing and demonstration purposes only.**

**SmartCapture Pro** is a Windows desktop tool built in Python that automatically captures screen regions at a configurable interval, extracts text via OCR (Optical Character Recognition), and exports everything into a structured text file — optimized for live transcripts from **Microsoft Teams meetings**.

Created by [@basecore](https://github.com/basecore)

---

## 🔒 Privacy First — 100% Local Processing

> **No data ever leaves your computer automatically.**

All screenshots and OCR-extracted texts are processed **exclusively on your local machine**. Nothing is uploaded, transmitted, or sent anywhere in the background. SmartCapture Pro does **not** connect to any cloud service, AI API, or external server during capture or OCR.

The workflow is:
1. **Capture** → screenshots saved locally to your chosen folder
2. **OCR** → text extracted locally using [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (runs on-device)
3. **Export** → a structured `.txt` file is generated locally
4. **Optional AI step** → you manually copy the export text and paste it into an AI chat of your choice (e.g. your company's internal AI, ChatGPT, Gemini, Claude) to summarize and clean up the transcript

**The AI step is always manual and opt-in.** You decide what you share and with whom. For corporate environments, using an internal/on-premise AI is strongly recommended.

---

## 🛡️ Privacy Module / GDPR Layer

Starting with **v25.7**, SmartCapture Pro includes an integrated **privacy module** to raise the data protection standard of transcript capture workflows and make retention and transparency easier to manage in practice. The module was added because transcript-related workflows in meetings require not only technical safeguards, but also clear participant information, controlled retention periods, and an explicit privacy-by-design approach. 

The implementation is based on three practical principles:
1. **Transparency before capture** — users can display a meeting-ready privacy notice before recording starts. 
2. **Data minimization and retention control** — screenshots and transcript text files can be deleted automatically after configurable retention periods. 
3. **Respect for participant choice** — Microsoft Teams allows users to hide their identity in captions and transcripts by disabling automatic identification in the accessibility settings. 

This does **not** replace legal review for a specific company or use case. It is a practical support layer for internal documentation workflows and privacy-conscious operation. 

### Why this was added

In many organizations, teams want the efficiency benefits of transcript-based note-taking, action-item extraction, and internal documentation, but they also need stronger safeguards around storage duration, participant notice, and local-only processing. The privacy module was introduced to close exactly that gap in SmartCapture Pro. 

The broader background is that meeting transcription can be discussed in practice under **legitimate interest** in certain internal business contexts, provided transparency, balancing of interests, and safeguards are in place. The article you referenced discusses this specifically for Microsoft Teams transcription, and public commentary also points to the BayLDA 2025 report as recognizing Article 6(1)(f) GDPR as a possible legal basis in appropriate constellations. 

At the same time, Microsoft Teams itself provides a built-in identity protection option: users can turn off **“Automatically identify me in live captions and live transcripts”** in **Settings → Accessibility → Captions and transcripts**. This is one reason why SmartCapture Pro now includes explicit participant notice text in German and English.

### What the privacy module does

The privacy module adds the following capabilities to SmartCapture Pro:

- **Privacy reminder before recording starts**
- **German and English meeting notice texts** that can be copied directly into the meeting chat
- **Recording cancel protection** — if the notice window is closed or cancelled, recording does not start
- **Automatic deletion settings** for screenshots and transcript text files
- **Separate retention periods** for screenshots and transcript exports
- **Manual local deletion run** from the Settings tab
- **Privacy settings integrated into the Settings tab**
- **Privacy UI follows the DE / EN language toggle**
- **Local-only storage of privacy settings** in a separate `privacy_settings.json`

---

## 📸 Screenshots

### Application GUI
![SmartCapture Pro GUI](https://raw.githubusercontent.com/basecore/SmartCapture-Pro/main/assets/screenshot_teams1.png)

### Capturing MS Teams Transcripts
![Teams Capture](https://raw.githubusercontent.com/basecore/SmartCapture-Pro/main/assets/screenshot_teams2.png)

---

## ✨ Features

### 📸 Screen Capture
- **Flexible region selection** — draw a resizable, draggable frame over any screen area (e.g. the Teams transcript panel)
- **Configurable interval** — screenshots taken every 1–60 seconds (adjustable via slider)
- **Two capture engines:**
  - **Standard** — captures the visible screen region directly (fast, reliable)
  - **Background** — captures a specific window even when it is covered by other windows (uses `PrintWindow` API)
- **Live preview** — side-by-side view of the previous and current screenshot in the UI
- **Smart filenames** — screenshots are automatically named with the meeting title and timestamp:
  `screen_ProjectUpdate_2026-06-18_09-30-00.png`
- **Session folders** — each recording session is saved into its own folder using date and meeting title:
  `captured_screens/2026-07-14_Project_Update_Q2/`

### 📝 OCR & Text Export
- **Tesseract OCR** integration — automatic installation on first run, no admin rights required
- **Multi-language support** — Auto (Japanese/English/German), German, English, Japanese+English
- **Image pre-processing** options — None, 2× upscaling (sharp), Grayscale + Contrast boost
- **Layout modes (PSM)** — Auto, Block (ideal for chat/transcript text), Single Line
- **Smart export filename** — includes meeting title, recording start time, and export time:
  `Export_ProjectUpdate_Start-2026-06-18_09-30-00_2026-06-18_09-45-00.txt`
- **Export header** — the generated `.txt` file contains a metadata header:
  ```
  Meeting Title: Project Update Q2
  Recording Start: 18.06.2026 09:30:00
  Export Created: 2026-06-18_09-45-00 | Settings: eng, --psm 6, scale2x
  ```
- **Session file tracking** — automatically uses images from the current recording session for OCR; session can be cleared or images deleted with one click
- **Manual OCR title detection** — if you select image files manually, SmartCapture Pro can derive the meeting title from the first filename and reuse it for the AI context and export naming

### 🤖 AI Context & Prompt Generator
- **Context fields** — enter your job title, company, department, and meeting title to provide the AI with relevant context
- **Automatic prompt generation** — a structured, ready-to-use AI prompt is generated from your inputs and OCR text, in German or English
- **One-click copy** — copies the full prompt to the clipboard; then open your AI of choice and paste with Ctrl+V
- **Configurable AI URL** — set the URL of any AI chat (ChatGPT, Gemini, Claude, or your company's internal AI)
- **Configurable browser** — choose between Default, Microsoft Edge, Chrome, or Firefox

### 🛡️ Privacy & Retention
- **Integrated privacy module** for GDPR-conscious operation
- **Privacy reminder before recording starts**
- **Ready-to-paste privacy notices** in German and English for meeting chat use
- **Recording abort if notice window is closed or cancelled**
- **Automatic deletion settings** for screenshots and transcript text files
- **Separate retention periods** for screenshots and transcript exports
- **Manual local deletion run** from the Settings tab
- **Privacy UI follows DE / EN app language**
- **Participant identity hint for Teams** included in the notice text, referencing the Teams accessibility option to disable automatic identification [cite:11]

### 🌍 Multilingual UI
- Full **German / English** toggle — switch the entire interface language with one click
- Setting is saved and restored on next launch
- Privacy reminder and privacy settings follow the selected UI language

### ⚙️ Configuration & Settings
- **Persistent config** — all settings (paths, AI URL, context fields, language) are saved automatically to `config.json`
- **Persistent privacy settings** — privacy retention and reminder options are stored locally in `privacy_settings.json`
- **Custom output folder** — choose any local folder for screenshots and exports
- **Custom Tesseract path** — point to an existing Tesseract installation or let the tool install it automatically

### 🔧 Auto-Installer
- Automatically installs all required Python packages on first run (`pytesseract`, `Pillow`, `mss`, `pywin32`, `natsort`)
- Automatically downloads and installs **Tesseract OCR** (University of Mannheim build) without admin rights
- Automatically downloads required language packs (German, Japanese) into the Tesseract data folder
- SSL bypass support for corporate proxy environments

---

## 🚀 Quick Start (Windows)

### Easiest Method — Double-click to run

1. Download the files into the **same folder**:
   - [`SmartCapture_Pro_257_2026-07-14.py`](https://github.com/basecore/SmartCapture-Pro/blob/main/SmartCapture_Pro_257_2026-07-14.py)
   - [`SmartCapture_Pro_257_Start.bat`](https://github.com/basecore/SmartCapture-Pro/blob/main/SmartCapture_Pro_257_Start.bat)
   - [`privacy_module.py`](https://github.com/basecore/SmartCapture-Pro/blob/main/privacy_module.py)
2. **Double-click `SmartCapture_Pro_257_Start.bat`** — done!

The `.bat` file checks for Python, installs all required libraries automatically, and launches the tool. On first run, Tesseract OCR is downloaded and installed silently in the background.

### Requirements

| Requirement | Details |
|---|---|
| **OS** | Windows 10 or Windows 11 |
| **Python** | 3.8 or newer — [Download](https://www.python.org/downloads/) |
| **Python option** | `tcl/tk and IDLE` must be enabled during Python installation (it is by default) |
| **Internet** | Required on first run only (to download Tesseract and language packs) |
| **Admin rights** | **Only needed for the Python installation itself.** Everything else — Tesseract OCR, all Python packages, and language packs — installs without admin rights, directly into your user profile (`%LOCALAPPDATA%`). |

> **Note:** If `tcl/tk` is missing, the tool will display a clear error message with step-by-step fix instructions.

### Via Terminal / Git

```bash
git clone https://github.com/basecore/SmartCapture-Pro.git
cd SmartCapture-Pro
py SmartCapture_Pro_257_2026-07-14.py
```

---

## 🛠️ How to Use

### Step 1 — Set the Meeting Title
Open the **🤖 AI Context** tab. The tool can automatically detect and update the meeting title from the captured screen region while the recording runs. You can also set or override the title manually in the **"Meeting Title"** field (e.g. `Project Update Q2`). The title is used in screenshot names, session folder names, export filenames, and embedded in the AI prompt for better context.

- Optional: also fill in Job Title, Company, and Department to further enrich the AI prompt

### Step 2 — Define the Capture Area
1. Go to the **📸 Recording** tab
2. Click **"🔍 Define Frame"** — a resizable blue frame appears on screen
3. Drag and resize it over the MS Teams transcript panel (or any text region)
4. Click **"✔️ Confirm Area"** — the region is locked in

### Step 3 — Review Privacy Notice
1. Click **"▶ START RECORDING"**
2. The privacy reminder window opens first
3. Optionally copy the German or English notice text into the meeting chat
4. Click **"Understood - Start Recording"** or the German equivalent to continue
5. If the window is cancelled or closed, recording will not start

### Step 4 — Start Recording
- Screenshots are taken automatically at your chosen interval
- The live preview shows the previous and current screenshot side by side
- Click **"⏹ STOP"** to end the session

> Screenshots are saved to your output folder immediately, grouped in a dedicated session folder with date and meeting title.

### Step 5 — Run OCR & Export
1. Go to the **📝 OCR & Export** tab
2. Select OCR language, image optimization mode, and layout mode
3. Click **"Start OCR & Export"**
4. A `.txt` file is generated locally and opened automatically

If no current session images are used and you manually select screenshots instead, the tool can parse the first selected image filename and automatically restore the meeting title into the AI Context tab.

### Step 6 — (Optional) Send to AI for Cleanup
1. Click **"🌐 Open AI Chat & Copy Text"**
2. The generated prompt (with full OCR text) is copied to your clipboard
3. Your configured browser opens the AI chat URL
4. Paste with **Ctrl+V** and let the AI summarize and clean the transcript

> ⚠️ **Recommendation for corporate environments:** Use your company's internal or on-premise AI to ensure no meeting content leaves your organization's infrastructure.

---

## 📁 Output File Structure

```text
captured_screens/
└── 2026-07-14_ProjectUpdate_Q2/
    ├── screen_ProjectUpdate_Q2_2026-07-14_09-30-00.png
    ├── screen_ProjectUpdate_Q2_2026-07-14_09-30-05.png
    ├── screen_ProjectUpdate_Q2_2026-07-14_09-30-10.png
    └── Export_ProjectUpdate_Q2_Start-2026-07-14_09-30-00_2026-07-14_09-45-00.txt
```

The export `.txt` contains:
- A structured AI prompt header (with your context)
- A metadata block (meeting title, recording start, export time, settings)
- The raw OCR text from all captured images, in chronological order

---

## 📂 Local Files and Settings

SmartCapture Pro stores data locally in user space. The main application configuration is saved locally, and the privacy module keeps its own local settings file for retention and reminder options.

Typical local files:
- `config.json` — main app settings
- `privacy_settings.json` — privacy module settings
- Session folders with screenshots and OCR export files

---

## 🆕 Changelog

### v25.7 — 2026-07-14
- 🛡️ **Integrated privacy module** — adds a dedicated GDPR-conscious privacy layer for local transcript capture workflows
- 🔔 **Privacy reminder before recording** — a notice window opens before recording starts
- 🌍 **German / English privacy notices** — ready-to-paste meeting chat text in both languages
- ❌ **Safe cancel behavior** — recording does not start if the reminder window is closed or cancelled
- ⚙️ **Privacy settings in the Settings tab** — dedicated section for retention and reminder controls
- 🧹 **Automatic deletion** — configurable retention periods for screenshots and transcript text files
- 🗑️ **Manual deletion run** — one-click local cleanup from the Settings tab
- 🌐 **Privacy UI follows app language** — privacy reminder and privacy settings now follow the DE / EN selection
- 📁 **Persistent local privacy settings** — stored in `privacy_settings.json`

### v25.6 — 2026-07-14
- 📁 **Session folders per recording** — each recording now creates its own output folder in the format `YYYY-MM-DD_MeetingTitle`
- 🖼️ **Screenshots and exports stored together** — all images and export files of a recording session are grouped inside the same session folder
- 🏷️ **Manual OCR filename title extraction** — when selecting screenshots manually for OCR, the tool can derive the meeting title from the first filename and populate the AI Context tab automatically
- 🔁 **Consistent session folder usage** — recording, export, folder opening, and session cleanup now all use the same tracked session directory
- 🧱 **Fullbase release** — v25.6 is based on the full original codebase with all methods intact

### v25.5 — 2026-06-18
- 🛡️ **Fixed: `GetWindowRect` crash** — `(1400, 'GetWindowRect', 'Invalid window handle')` error eliminated. A new `_safe_get_window_rect()` helper validates the window handle with `IsWindow()` before calling the Win32 API. Invalid handles (e.g. after Teams reloads or the window is closed) are now silently skipped — no more terminal error spam.
- 📸 **Screenshot filenames** now include the meeting title (from the AI Context tab):
  - Before: `screen_2026-06-18_09-30-00.png`
  - After: `screen_ProjectUpdate_2026-06-18_09-30-00.png`
- 📄 **Export `.txt` filenames** now include the meeting title and recording start timestamp:
  - Before: `Export_2026-06-18_09-45.txt`
  - After: `Export_ProjectUpdate_Start-2026-06-18_09-30-00_2026-06-18_09-45-00.txt`
- 📋 **Export file header** now contains meeting title and recording start time as metadata
- 🕐 **Recording start timestamp** is captured automatically when the first screenshot is saved

### v25.4 — 2026-06-08
- 🪟 **Background capture engine** — capture a Teams window even when it is covered by other applications (using `PrintWindow` Win32 API)
- 🌐 **Configurable AI Chat URL** — set any AI chat URL (ChatGPT, Gemini, Claude, internal AI)
- 🌐 **Browser selection** — choose between Default, Edge, Chrome, or Firefox for the AI chat
- 🔧 **Auto Tesseract installer** — silent installation without admin rights to `%LOCALAPPDATA%`
- 🌍 **Bilingual UI** — full German / English toggle, setting persists across restarts
- 💾 **Persistent configuration** — all settings saved to `config.json`

### v16.6 — 2026-03-12
- Initial public release
- Basic region capture with MSS
- Tesseract OCR integration
- Export to `.txt`
- Live screenshot preview

---

## 🧩 Dependencies

All dependencies are installed automatically on first run.

| Package | Purpose |
|---|---|
| `pytesseract` | Python wrapper for Tesseract OCR |
| `Pillow` | Image loading, processing, and display |
| `mss` | Fast multi-monitor screen capture |
| `pywin32` | Windows API access (window handles, `PrintWindow`) |
| `natsort` | Natural-order file sorting for OCR processing |
| `tkinter` | GUI framework (built into Python, must be enabled) |

**External tool:** [Tesseract OCR 5.5](https://github.com/UB-Mannheim/tesseract/wiki) — auto-installed on first run.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
→ [Open an Issue](https://github.com/basecore/SmartCapture-Pro/issues)

---

## 📜 License

This project is provided for testing and demonstration purposes only.
