# SmartCapture Pro 📸

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/basecore/SmartCapture-Pro)
[![AI Generated](https://img.shields.io/badge/AI_Generated-Gemini_3.1_Pro-20B8D9?style=for-the-badge&logo=google)](https://gemini.google.com/)
[![License: MIT](https://img.shields.io/badge/License-Testing_Only-yellow.svg?style=for-the-badge)](https://github.com/basecore/SmartCapture-Pro)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://www.python.org/)

> **⚠️ Disclaimer: Nur zu Testzwecken verwenden! (For testing purposes only!)**

SmartCapture Pro is a modern Python-based desktop application designed specifically for capturing screen regions and extracting text in real-time. It is highly optimized for capturing live transcripts from **Microsoft Teams meetings** using Optical Character Recognition (OCR).

Created by [@basecore](https://github.com/basecore)

---

## 📸 Screenshot

![SmartCapture Pro Screenshot](https://raw.githubusercontent.com/basecore/SmartCapture-Pro/main/assets/screenshot.png)

---

## ✨ Features
- 🎯 **Region Selection:** Draw a precise frame around your MS Teams transcript or any other text.
- 📝 **Live OCR:** Instantly extracts text from the selected region using Tesseract OCR.
- 🌓 **Modern UI:** Sleek Dark Mode interface utilizing `sv_ttk` for a native, modern look.
- 🌍 **Bilingual:** Quick toggle between German (DE) and English (EN) prompts.
- 🤖 **AI Integration:** Seamlessly copy extracted texts and forward them to any AI Chat (e.g. ChatGPT, Gemini, Claude).
- 📋 **Clipboard Management:** Auto-copies results for quick pasting.
- ⚙️ **Configurable:** Select your preferred browser and AI chat platform directly in the settings.

## 🚀 Installation

### 1. Prerequisites
- **Python 3.8+** installed.
- **Tesseract OCR** installed on your system:
  - *Windows:* Download the installer from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and ensure `tesseract.exe` is in your system's PATH.

### 2. Clone the Repository
```bash
git clone https://github.com/basecore/SmartCapture-Pro.git
cd SmartCapture-Pro
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python SmartCapture_Pro.py
```

## 🛠️ Usage
1. Start the tool via terminal or command prompt.
2. Define the capture area by clicking and dragging a blue box (e.g., over the MS Teams transcript).
3. The tool will capture the area, perform OCR, and display the extracted text.
4. Review the text, edit if necessary, and use the quick action buttons to copy or send to an AI Chat.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/basecore/SmartCapture-Pro/issues).

## 📜 License
This project is for testing and demonstration purposes only.
