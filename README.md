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

Starting with **v25.7**, SmartCapture Pro includes an integrated **privacy module** to raise the data protection standard of transcript capture workflows and make retention and transparency easier to manage in practice. The module was added because transcript-related workflows in meetings require not only technical safeguards, but also clear participant information, controlled retention periods, and an explicit privacy-by-design approach. [web:11][web:12][web:16]

The implementation is based on three practical principles:
1. **Transparency before capture** — users can display a meeting-ready privacy notice before recording starts. [web:12]
2. **Data minimization and retention control** — screenshots and transcript text files can be deleted automatically after configurable retention periods. [web:12][web:16]
3. **Respect for participant choice** — Microsoft Teams allows users to hide their identity in captions and transcripts by disabling automatic identification in the accessibility settings. [web:11]

This does **not** replace legal review for a specific company or use case. It is a practical support layer for internal documentation workflows and privacy-conscious operation.

---

## 📘 Why this was added

In many organizations, teams want the efficiency benefits of transcript-based note-taking, action-item extraction, and internal documentation, but they also need stronger safeguards around storage duration, participant notice, and local-only processing. The privacy module was introduced to close exactly that gap in SmartCapture Pro. [web:12][web:16]

The broader background is that meeting transcription can be discussed in practice under **legitimate interest** in certain internal business contexts, provided transparency, balancing of interests, and safeguards are in place. The article you referenced discusses this specifically for Microsoft Teams transcription, and public commentary also points to the BayLDA 2025 report as recognizing Article 6(1)(f) GDPR as a possible legal basis in appropriate constellations. [web:12][web:16][web:17]

At the same time, Microsoft Teams itself provides a built-in identity protection option: users can turn off **“Automatically identify me in live captions and live transcripts”** in **Settings → Accessibility → Captions and transcripts**. This is one reason why SmartCapture Pro now includes explicit participant notice text in German and English. [web:11]

---

## 🔐 What the privacy module does

The privacy module adds the following capabilities to SmartCapture Pro:

### Consent / Notice Reminder
- A **privacy reminder window** appears before recording starts
- The reminder contains a **German and English** privacy notice
- The default tab follows the app language (**DE / EN**)
- The user can copy a ready-to-paste notice text directly into the meeting chat
- If the reminder window is closed or cancelled, recording **does not start**

### Retention & Auto-Deletion
- Automatic deletion can be enabled in **Settings**
- Screenshots and transcript text files can have **separate retention periods**
- A manual **“run deletion now”** button is included
- Deletion checks are performed locally and only affect local files in the configured output folder

### Multilingual Privacy UI
- The entire privacy section in **Settings** switches together with the app language
- Reminder texts, labels, buttons, and helper texts adapt to **German / English**

### Local-Only Privacy Controls
- All privacy settings are stored locally on the device
- No retention metadata or notice data is transmitted externally
- Clipboard copy actions are explicit user actions only

---

## ⚖️ Legal / Practical Background

SmartCapture Pro itself is a **local OCR screenshot utility**, not a cloud transcription platform. That distinction matters: the tool captures only a selected screen region and extracts text locally via OCR, without automatic uploading or server-side speech analysis. This supports a more privacy-conscious setup than cloud-native transcription pipelines. [web:12][web:16]

Still, any use in real meetings should be assessed in the context of company policy, labor law, internal transparency duties, and the concrete meeting scenario. The privacy module is designed to support a more defensible and transparent workflow by combining local processing, configurable retention, and participant notice. [web:12][web:16]

For Microsoft Teams users, note that speaker identification in captions and live transcripts can be disabled individually in Teams settings under **Accessibility → Captions and transcripts**. SmartCapture Pro therefore includes this information in its privacy notice templates. [web:11]

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
