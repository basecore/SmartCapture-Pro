# SmartCapture Pro 📸

**⚠️ Disclaimer: Nur zu Testzwecken verwenden! (For testing purposes only!)**

SmartCapture Pro is a modern Python-based desktop application designed specifically for capturing screen regions and extracting text in real-time. It is highly optimized for capturing live transcripts from **Microsoft Teams meetings** using Optical Character Recognition (OCR).

Created by [@basecore](https://github.com/basecore)

## ✨ Features
- 🎯 **Region Selection:** Draw a precise frame around your MS Teams transcript or any other text.
- 📝 **Live OCR:** Instantly extracts text from the selected region using Tesseract OCR.
- 🌓 **Modern UI:** Sleek Dark Mode interface utilizing `sv_ttk` for a native, modern look.
- 🌍 **Bilingual:** Quick toggle between German (DE) and English (EN) prompts.
- 🤖 **AI Integration:** Seamlessly copy extracted texts and forward them to AI Chats.
- 📋 **Clipboard Management:** Auto-copies results for quick pasting.

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
2. Define the capture area by clicking and dragging a box (e.g., over the MS Teams transcript).
3. The tool will capture the area, perform OCR, and display the extracted text.
4. Review the text, edit if necessary, and use the quick action buttons to copy or send to an AI Chat.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/basecore/SmartCapture-Pro/issues).

## 📜 License
This project is for testing and demonstration purposes only.
