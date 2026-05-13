import sys
import subprocess
import os
import time
import datetime
import textwrap
# --- NEU: TKINTER INSTALLATIONS-PRÜFUNG ---
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError:
    print("\n" + "="*60)
    print("[FEHLER] Das Modul 'tkinter' fehlt in deiner Python-Installation.")
    print("         Dieses wird zwingend fuer die Benutzeroberflaeche benoetigt.")
    print("\nLÖSUNG (Ohne Admin-Rechte moeglich):")
    print("1. Gehe in den Windows-Einstellungen zu 'Installierte Apps'.")
    print("2. Suche nach deiner Python-Installation und klicke auf 'Aendern' (Modify).")
    print("3. Klicke im Setup-Fenster auf 'Modify'.")
    print("4. Setze das Haeckchen bei 'tcl/tk and IDLE' und klicke auf 'Next'.")
    print("="*60 + "\n")
    sys.exit(1) # Beendet das Skript sofort mit einem Fehlercode für die .bat
    
import webbrowser
import urllib.request
import tempfile
from shutil import which
import ssl

# --- 0. HIGH DPI FIX ---
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# --- INSTALL CHECK ---
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = {
    'pytesseract': 'pytesseract', 
    'Pillow': 'PIL', 
    'natsort': 'natsort', 
    'mss': 'mss',
    'pywin32': 'win32gui' 
}

for package, import_name in required_packages.items():
    try:
        __import__(import_name)
    except ImportError:
        install(package)

import pytesseract
import win32gui
import win32ui
from ctypes import windll
from PIL import Image, ImageTk, ImageChops, ImageStat, ImageOps, ImageEnhance
import mss
import mss.tools
from natsort import natsorted

# --- TESSERACT AUTO-INSTALLER ---
# --- TESSERACT AUTO-INSTALLER ---
# --- TESSERACT AUTO-INSTALLER ---
def ensure_tesseract_installed():
    """
    Prüft auf Tesseract und installiert es inkl. Sprachpaketen (DE, JP) 
    ohne Admin-Rechte in das lokale AppData Verzeichnis.
    """
    # --- SSL BYPASS FÜR FIRMENNETZWERKE (PROXY) ---
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    # ----------------------------------------------

    local_app_data = os.getenv('LOCALAPPDATA')
    if not local_app_data:
        local_app_data = os.path.expanduser('~\\AppData\\Local')
        
    install_dir = os.path.join(local_app_data, r"Programs\Tesseract-OCR")
    tess_exe = os.path.join(install_dir, "tesseract.exe")
    tessdata_dir = os.path.join(install_dir, "tessdata")
    
    tess_found = False
    if which('tesseract'):
        tess_found = True
    elif os.path.exists(tess_exe):
        tess_found = True
    elif os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        tess_found = True
        tessdata_dir = r'C:\Program Files\Tesseract-OCR\tessdata'
    
    # 1. Tesseract installieren, falls nicht vorhanden
    if not tess_found:
        print("\n[INFO] DE: Tesseract OCR wurde nicht auf diesem System gefunden.")
        print("[INFO] EN: Tesseract OCR was not found on this system.")
        print("\n[INFO] DE: Hinweis: Tesseract ist ein sicheres, weltweit bewaehrtes Open-Source-Tool")
        print("           zur Texterkennung, das von der Universitaet Mannheim bereitgestellt wird.")
        print("[INFO] EN: Notice: Tesseract is a secure, globally proven open-source text")
        print("           recognition tool provided by the University of Mannheim.")
        print("\n[INFO] DE: Lade Tesseract herunter und installiere im Hintergrund (dies kann einen Moment dauern)...")
        print("[INFO] EN: Downloading and installing Tesseract in the background (this may take a moment)...")
        
        tess_url = "https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe"
        temp_exe = os.path.join(tempfile.gettempdir(), "tesseract_installer.exe")
        
        try:
            urllib.request.urlretrieve(tess_url, temp_exe)
            
            # Nullsoft (NSIS) Silent Installation Flags
            install_cmd = [
                temp_exe,
                "/S",
                f"/D={install_dir}"
            ]
            subprocess.run(install_cmd, check=True)
            print("[INFO] DE: Tesseract (Uni Mannheim) wurde erfolgreich installiert!")
            print("[INFO] EN: Tesseract (Uni Mannheim) was installed successfully!")
        except Exception as e:
            print(f"[FEHLER / ERROR] Installation fehlgeschlagen / Installation failed: {e}")
        finally:
            if os.path.exists(temp_exe):
                try: os.remove(temp_exe)
                except: pass

    # 2. Sprachpakete prüfen und ggf. herunterladen
    os.makedirs(tessdata_dir, exist_ok=True)
    lang_packs = {
        "deu.traineddata": "https://github.com/tesseract-ocr/tessdata_fast/raw/main/deu.traineddata",
        "jpn.traineddata": "https://github.com/tesseract-ocr/tessdata_fast/raw/main/jpn.traineddata"
    }
    
    if os.access(tessdata_dir, os.W_OK):
        for lang_file, url in lang_packs.items():
            lang_path = os.path.join(tessdata_dir, lang_file)
            if not os.path.exists(lang_path):
                print(f"[INFO] DE: Lade Sprachpaket {lang_file} herunter...")
                print(f"[INFO] EN: Downloading language pack {lang_file}...")
                try:
                    urllib.request.urlretrieve(url, lang_path)
                    print(f"[INFO] DE: {lang_file} erfolgreich installiert.")
                    print(f"[INFO] EN: {lang_file} installed successfully.")
                except Exception as e:
                    print(f"[WARNUNG / WARNING] Konnte / Could not download {lang_file}: {e}")

# Direkt ausführen
ensure_tesseract_installed()

# --- KONFIGURATION ---
ACCENT_COLOR = "#0078D7"
DARK_COLOR = "#1E1E1E"
EDGE_BLUE = "#0078D7"
BG_COLOR = "#ffffff"
TRANSPARENT_KEY = "#ff00ff"

# VERSION INFO
TOOL_NAME = "SmartCapture Pro"
TOOL_VER = "v23.3 | Stand: 13.05.2026"

# --- AI CHAT SETTINGS (change defaults here) ---
AI_CHAT_URL = "https://chatgpt.com/"  # e.g. https://gemini.google.com or https://claude.ai
AI_BROWSER  = "default"               # "default", "msedge", "chrome", "firefox"

# PSM MODES
PSM_MAPPING = {
    "auto": "--psm 3",
    "block": "--psm 6",
    "line": "--psm 7"
}

# PRE-PROCESSING
PREPROC_KEYS = ["none", "scale2x", "gray_contrast"]

# PROMPT TEMPLATES
PROMPT_TEMPLATE_DE = """Du bist ein erfahrener technischer Projektassistent und Experte für die Strukturierung von unaufgeräumten Meeting-Transkripten.

Ich arbeite als {job} bei {comp} im Bereich {dept}.
Dies ist ein durch OCR (Texterkennung) generierter Export eines Meetings mit dem Titel '{title}'.

{trans_note}
Das Transkript besteht aus Screenshots, die alle paar Sekunden aufgenommen wurden. Daher gibt es massive Textüberschneidungen, Fehler und statische Hintergrundtexte (z.B. Präsentationsfolien).

Bitte verarbeite den Text nach folgenden Regeln:

1. REKONSTRUKTION (Interner Schritt):
Filtere wiederkehrende statische Hintergrundtexte (Folien) heraus. Verbinde die sich ständig ändernden Untertitel/Gesprochenes zu einem fließenden, chronologischen Verlauf ohne Duplikate. Korrigiere offensichtliche OCR-Fehler, aber behalte technische Fachbegriffe aus meinem Bereich exakt bei.

2. AUSGABEFORMAT:
Erstelle aus dem rekonstruierten Verlauf ein strukturiertes Meeting-Protokoll in folgendem Format:

## 👥 Teilnehmer
(Liste der erkannten Sprecher/Teilnehmer)

## 📌 Kern-Themen & Diskussionen
(Kurze, prägnante Zusammenfassung der wichtigsten besprochenen Punkte)

## 🎯 Entscheidungen
(Klare Liste der getroffenen Entscheidungen. Falls keine getroffen wurden, schreibe "Keine expliziten Entscheidungen dokumentiert")

## 🚀 Maßnahmen / Action Items
(Wer macht was bis wann? Als Checkliste formatieren)

## ❓ Offene Fragen
(Punkte, die im Meeting nicht abschließend geklärt wurden)

Hier ist der OCR-Text:
"""

PROMPT_TEMPLATE_EN = """You are an experienced technical project assistant and an expert in structuring messy meeting transcripts.

I work as a {job} at {comp} in the {dept} department.
This is an OCR-generated transcript export of a meeting titled '{title}'.

{trans_note}
The transcript consists of screenshots taken every few seconds. Therefore, there are massive text overlaps, errors, and static background texts (e.g., presentation slides).

Please process the text using the following rules:

1. RECONSTRUCTION (Internal Step):
Filter out recurring static background texts (slides). Merge the constantly changing subtitles/spoken words into a fluid, chronological flow without duplicates. Correct obvious OCR errors, but exactly maintain technical terms from my field.

2. OUTPUT FORMAT:
Create a structured meeting protocol from the reconstructed flow in the following format:

## 👥 Participants
(List of recognized speakers/participants)

## 📌 Core Topics & Discussions
(Short, concise summary of the main points discussed)

## 🎯 Decisions
(Clear list of decisions made. If none were made, write "No explicit decisions documented")

## 🚀 Measures / Action Items
(Who does what by when? Format as a checklist)

## ❓ Open Questions
(Points that were not finally resolved in the meeting)

Here is the OCR text:
"""

# TEXTE
TEXTS = {
    "tab_rec": {"DE": " 📸 Aufnahme ", "EN": " 📸 Recording "},
    "tab_ai":  {"DE": " 🤖 AI Context ", "EN": " 🤖 AI Context "},
    "tab_ocr": {"DE": " 📝 OCR & Export ", "EN": " 📝 OCR & Export "},
    "tab_set": {"DE": " ⚙️ Einstellungen ", "EN": " ⚙️ Settings "},
    
    # Rec
    "sec_area": {"DE": "1. Aufnahmebereich definieren", "EN": "1. Define Capture Area"},
    "instr_area": {"DE": "Klicke 'Rahmen definieren'. Ein blauer Rahmen erscheint.\nZiehe ihn über den Bereich.", "EN": "Click 'Define Frame'. A blue frame appears.\nDrag it over the area."},
    "btn_frame": {"DE": "🔍 Rahmen definieren", "EN": "🔍 Define Frame"},
    "btn_lock": {"DE": "✔️ Bereich übernehmen", "EN": "✔️ Confirm Area"},
    "lbl_no_area": {"DE": "Kein Bereich gewählt.", "EN": "No area selected."},
    "lbl_area_ok": {"DE": "✓ Fixiert: {w}x{h} px (Monitor {mon})", "EN": "✓ Locked: {w}x{h} px (Monitor {mon})"},
    "lbl_area_ok_win": {"DE": "✓ Fixiert: {w}x{h} px (Monitor {mon})\n🪟 {title}", "EN": "✓ Locked: {w}x{h} px (Monitor {mon})\n🪟 {title}"},
    "sec_proc": {"DE": "2. Automatisierung", "EN": "2. Automation"},
    "lbl_interval": {"DE": "Wartezeit zwischen Screenshots:", "EN": "Wait time between screenshots:"},
    "btn_start": {"DE": "▶ AUFNAHME STARTEN", "EN": "▶ START RECORDING"},
    "btn_stop": {"DE": "⏹ STOPP", "EN": "⏹ STOP"},
    "status_ready": {"DE": "Bereit.", "EN": "Ready."},
    "status_rec": {"DE": "🔴 Aufnahme läuft...", "EN": "🔴 Recording..."},
    "status_stop": {"DE": "Gestoppt. ({n} Bilder)", "EN": "Stopped. ({n} images)"},
    "status_wait": {"DE": "⏳ Überwache... (Keine Änderung)", "EN": "⏳ Monitoring... (No change)"},
    "status_saved": {"DE": "🔴 Gespeichert: {fn}", "EN": "🔴 Saved: {fn}"},
    "preview_ph": {"DE": "[Vorschau]", "EN": "[Preview]"},
    "lbl_prev": {"DE": "Vorheriger Screenshot", "EN": "Previous Screenshot"},
    "lbl_curr": {"DE": "Aktueller Screenshot", "EN": "Current Screenshot"},
    "btn_folder": {"DE": "📂 Speicherordner öffnen", "EN": "📂 Open Output Folder"},
    
    # OCR
    "sec_ocr_opts": {"DE": "Export-Optionen", "EN": "Export Options"},
    "lbl_lang": {"DE": "Sprache:", "EN": "Language:"},
    "lbl_preproc": {"DE": "Bild-Optimierung:", "EN": "Image Optimization:"},
    "lbl_psm": {"DE": "Layout-Modus:", "EN": "Layout Mode:"},
    "grp_content": {"DE": "Inhalt des Exports", "EN": "Export Content"},
    "chk_date": {"DE": "Datum/Uhrzeit einfügen", "EN": "Include Date/Time"},
    "chk_file": {"DE": "Dateiname einfügen", "EN": "Include Filename"},
    "sec_ocr_run": {"DE": "Verarbeitung", "EN": "Processing"},
    "btn_ocr": {"DE": "Texterkennung starten & Exportieren", "EN": "Start OCR & Export"},
    
    # Auto-Files Checkbox
    "chk_auto_files": {"DE": "Bilder der aktuellen Sitzung verwenden ({n} Bilder)", "EN": "Use images from current session ({n} images)"},
    "btn_clear_session": {"DE": "🗑️ Leeren", "EN": "🗑️ Clear"},

    # Chat Integration
    "info_chat": {"DE": "Text in Zwischenablage kopieren und Browser starten.\nDort einfach mit Strg+V einfügen.", "EN": "Copy generated text to clipboard and open browser.\nJust paste it there using Ctrl+V."},
        "tab_info": {"DE": "Info", "EN": "Info"},
    "lbl_about_title": {"DE": "Über dieses Tool", "EN": "About this Tool"},
    "lbl_about_text": {"DE": "Generiert mit Gemini 3.1 Pro.\nSmartCapture Pro ist ein Tool zur Automatisierung von OCR-Erfassung für Live-Transkripte.", "EN": "Generated with Gemini 3.1 Pro.\nSmartCapture Pro is a tool for automating OCR capture of live transcripts."},
    "lbl_trans_lang": {"DE": "⚠️ Abweichende Transkription? (z.B. gespr.: EN, Text: DE):", "EN": "⚠️ Transcript mismatch? (e.g. spoken: EN, transcript: DE):"},
    "lbl_frame_pull": {"DE": " RAHMEN ZIEHEN ", "EN": " DRAW FRAME "},
"btn_chat": {"DE": "🌐 AI Chat öffnen & Text kopieren", "EN": "🌐 Open AI Chat & Copy Text"},
    "err_no_export": {"DE": "Bitte starte zuerst die OCR-Verarbeitung und den Export!", "EN": "Please run OCR processing and export first!"},
    "msg_chat_copied": {"DE": "Text erfolgreich kopiert!\n\nBrowser wird geöffnet...\nFüge den Text einfach in das Chat-Feld ein (Strg+V).", "EN": "Text successfully copied!\n\nOpening browser...\nJust paste the text into the chat field (Ctrl+V)."},

    # AI Tab
    "sec_ai_ctx": {"DE": "Kontext & Rolle", "EN": "Context & Role"},
    "lbl_job": {"DE": "Beruf / Rolle:", "EN": "Job Title / Role:"},
    "lbl_comp": {"DE": "Firma:", "EN": "Company:"},
    "lbl_dept": {"DE": "Bereich / Abteilung:", "EN": "Department:"},
    "lbl_title": {"DE": "Meeting Titel:", "EN": "Meeting Title:"},
    "sec_ai_gen": {"DE": "Generierter Prompt (für KI-Chat)", "EN": "Generated Prompt (for AI Chat)"},
    "btn_gen_prompt": {"DE": "🔄 Prompt aktualisieren", "EN": "🔄 Update Prompt"},
    "btn_copy": {"DE": "📋 Prompt kopieren", "EN": "📋 Copy Prompt"},
    "msg_copied": {"DE": "Prompt kopiert!", "EN": "Prompt copied!"},

    # Settings Tab
    "sec_cap_mode": {"DE": "Aufnahmemethode (Engine)", "EN": "Capture Engine"},
    "rb_screen": {"DE": "Normal (Bildschirm abfotografieren)", "EN": "Standard (Capture Screen directly)"},
    "rb_window": {"DE": "Hintergrund (Verdeckte Fenster abgreifen)", "EN": "Background (Capture covered windows)"},
    "lbl_win_title": {"DE": "Erkanntes Ziel-Fenster:", "EN": "Detected Target Window:"},
    
    "sec_paths": {"DE": "Systempfade", "EN": "System Paths"},
    "lbl_tess_path": {"DE": "Pfad zur tesseract.exe:", "EN": "Path to tesseract.exe:"},
    "lbl_out_dir": {"DE": "Speicherordner:", "EN": "Output Folder:"},
    "btn_browse": {"DE": "Durchsuchen...", "EN": "Browse..."},
    "sec_info": {"DE": "Hilfe & Info", "EN": "Help & Info"},
    "info_text": {"DE": "Tesseract OCR wird benötigt.", "EN": "Tesseract OCR is required."},
    "link_text": {"DE": "🔗 Tesseract Download (GitHub)", "EN": "🔗 Download Tesseract (GitHub)"},
    
    # Dropdowns
    "dd_preproc_none": {"DE": "Keine (Original)", "EN": "None (Original)"},
    "dd_preproc_scale2x": {"DE": "2x Skalierung (Scharf)", "EN": "2x Scaling (Sharp)"},
    "dd_preproc_gray_contrast": {"DE": "Graustufen + Kontrast", "EN": "Grayscale + Contrast"},
    "dd_psm_auto": {"DE": "Auto (Standard)", "EN": "Auto (Default)"},
    "dd_psm_block": {"DE": "Block (Chat/Text)", "EN": "Block (Chat/Text)"},
    "dd_psm_line": {"DE": "Einzelne Zeile", "EN": "Single Line"},

    # Errors
    "err_title": {"DE": "Fehler", "EN": "Error"},
    "err_no_frame": {"DE": "Bitte erst den 'Rahmen definieren' (und das grüne Fenster nicht manuell schließen)!", "EN": "Please 'Define Frame' first (and do not close the green window manually)!"},
    "err_not_locked": {"DE": "Bereich noch nicht bestätigt!", "EN": "Area not confirmed!"},
    "err_tess": {"DE": "Tesseract.exe nicht gefunden!", "EN": "Tesseract.exe not found!"},
    "err_win_not_found": {"DE": "Ziel-Fenster konnte nicht fokussiert werden!\nIst es offen und nicht minimiert?", "EN": "Target Window could not be focused!\nIs it open and not minimized?"},
    "progress_title": {"DE": "Verarbeite...", "EN": "Processing..."},
    "progress_init": {"DE": "Initialisiere...", "EN": "Initializing..."},
    "progress_step": {"DE": "Bild {i} / {n}", "EN": "Image {i} / {n}"}
}

OCR_LANGS = {
    "Automatisch (Jap/Eng/Deu)": "jpn+eng+deu",
    "Japanisch (+Englisch)": "jpn+eng",
    "Deutsch": "deu",
    "Englisch": "eng"
}

# --- KLASSEN ---

class ResizableSelectionWindow(tk.Toplevel):
    def __init__(self, master, label_text=" RAHMEN ZIEHEN "):
        super().__init__(master)
        self.title("Selector")
        self.geometry("700x450+100+100")
        self.attributes("-topmost", True)
        self.config(bg=ACCENT_COLOR)
        self.wm_attributes("-transparentcolor", TRANSPARENT_KEY)

        self.inner_frame = tk.Frame(self, bg=TRANSPARENT_KEY)
        self.inner_frame.pack(fill="both", expand=True, padx=10, pady=10) 

        lbl = tk.Label(self, text=label_text, bg=ACCENT_COLOR, fg="white", font=("Arial", 9, "bold"))
        lbl.place(x=0, y=0)

        ttk.Sizegrip(self).place(relx=1.0, rely=1.0, anchor="se")

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_content = tk.Frame(self.canvas, bg=BG_COLOR)
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        
        self.scrollable_content.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

class SmartCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{TOOL_NAME} {TOOL_VER}")
        self.root.geometry("700x950")
        self.root.configure(bg=BG_COLOR)
        
        self.current_lang = "DE"
        self.selector_win = None
        self.last_frame_geo = None
        
        # Capture Logic Vars
        self.var_cap_mode = tk.StringVar(value="window")
        self.var_win_title = tk.StringVar(value="-- Automatische Erkennung --")
        self.window_hwnd = None
        self.rel_area = None
        self.monitor_area = {'top': 0, 'left': 0, 'width': 0, 'height': 0}
        
        self.area_locked = False
        self.is_recording = False
        self.last_img = None
        self.img_counter = 0
        self.last_export_text = ""
        self.preview_mode = "horizontal"
        
        # Session Tracker für automatische Dateiauswahl
        self.session_files = []
        self.var_auto_files = tk.BooleanVar(value=True)
        
        # Paths - Output dynamisch im Home-Verzeichnis des Nutzers
        self.var_tess_path = tk.StringVar()
        user_home = os.path.expanduser('~')
        self.var_out_dir = tk.StringVar(value=os.path.join(user_home, "captured_screens"))
        
        tess = self.find_tesseract_auto()
        self.var_tess_path.set(tess if tess else "C:/Program Files/Tesseract-OCR/tesseract.exe")
        
        # OCR Vars
        self.var_ocr_date = tk.BooleanVar(value=True) 
        self.var_ocr_file = tk.BooleanVar(value=True)
        self.var_preproc = tk.StringVar(value="scale2x")
        self.var_psm = tk.StringVar(value="block")

        # Context Vars
        self.var_job = tk.StringVar(value="Software Developer")
        self.var_comp = tk.StringVar(value="MyCompany")
        self.var_dept = tk.StringVar(value="Software Engineering")
        self.var_title = tk.StringVar(value="Project Updates")
        self.var_trans_lang = tk.StringVar(value="")
        self.var_ai_url     = tk.StringVar(value=AI_CHAT_URL)
        self.var_ai_browser = tk.StringVar(value=AI_BROWSER)

        # --- HEADER ---
        header = tk.Frame(root, bg=ACCENT_COLOR) 
        header.pack(fill="x")
        
        self.btn_lang = tk.Button(header, text="🇩🇪 DE / 🇺🇸 EN", command=self.toggle_language, bg="#1E1E1E", fg="white", relief="flat", font=("Arial", 8, "bold"))
        self.btn_lang.pack(side="right", padx=10, pady=10, anchor="ne")
        
        tk.Label(header, text=TOOL_NAME, bg=ACCENT_COLOR, fg="white", font=("Segoe UI", 16, "bold")).pack(pady=(10,0))
        tk.Label(header, text=TOOL_VER, bg=ACCENT_COLOR, fg="#eeeeee", font=("Segoe UI", 9)).pack(pady=(0,10))
        
        # --- TABS ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=BG_COLOR, borderwidth=0)
        style.configure('TNotebook.Tab', padding=[12, 6], font=('Segoe UI', 10, 'bold'))
        style.map("TNotebook.Tab", background=[("selected", "white"), ("!selected", "#f0f0f0")], foreground=[("selected", ACCENT_COLOR)])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)
        
        # TABS INITIALIZATION
        self.tab_rec = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_rec, text="Recording")
        self.setup_rec_tab()
        
        self.tab_ai = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_ai, text="AI Context")
        self.setup_ai_tab()
        
        self.tab_ocr = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_ocr, text="OCR")
        self.setup_ocr_tab()

        self.tab_set = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_set, text="Einstellungen")
        self.setup_settings_tab()
        self.tab_info = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_info, text="Info")
        self.setup_info_tab()

        
        self.update_texts()
        self.update_session_file_count()

    # --- SETUP TABS ---
    def setup_rec_tab(self):
        sf = ScrollableFrame(self.tab_rec, bg=BG_COLOR)
        sf.pack(fill="both", expand=True)
        content = sf.scrollable_content
        pad = tk.Frame(content, bg=BG_COLOR, padx=15, pady=10)
        pad.pack(fill="both", expand=True)

        self.lbl_sec_area = self.create_header(pad, "")
        self.lbl_instr_area = tk.Label(pad, text="", bg=BG_COLOR, justify="left", wraplength=600)
        self.lbl_instr_area.pack(anchor="w", pady=(0, 5))
        
        btn_box = tk.Frame(pad, bg=BG_COLOR)
        btn_box.pack(fill="x", pady=2)
        self.btn_show = self.styled_btn(btn_box, "", self.open_selector, "#dddddd", "black")
        self.btn_show.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_lock = self.styled_btn(btn_box, "", self.lock_selector, ACCENT_COLOR, "white")
        self.btn_lock.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        self.lbl_info = tk.Label(pad, text="", bg=BG_COLOR, fg="gray", font=("Consolas", 9), justify="center")
        self.lbl_info.pack(pady=5)

        self.lbl_sec_proc = self.create_header(pad, "")
        
        interval_frame = tk.Frame(pad, bg=BG_COLOR)
        interval_frame.pack(fill="x")
        self.lbl_interval = tk.Label(interval_frame, text="", bg=BG_COLOR)
        self.lbl_interval.pack(side="left")
        self.lbl_interval_val = tk.Label(interval_frame, text="5.0s", bg=BG_COLOR, fg=ACCENT_COLOR, font=("Segoe UI", 10, "bold"))
        self.lbl_interval_val.pack(side="right")

        self.interval_var = tk.DoubleVar(value=5.0) 
        tk.Scale(pad, from_=1.0, to=60.0, orient="horizontal", variable=self.interval_var, resolution=1.0, bg=BG_COLOR, highlightthickness=0, command=self.update_interval_label).pack(fill="x", pady=2)
        
        rec_btns = tk.Frame(pad, bg=BG_COLOR)
        rec_btns.pack(fill="x", pady=5)
        self.btn_start = self.styled_btn(rec_btns, "", self.start_recording, ACCENT_COLOR, "white")
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_stop = self.styled_btn(rec_btns, "", self.stop_recording, "#888888", "white")
        self.btn_stop.config(state="disabled")
        self.btn_stop.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        self.lbl_status = tk.Label(pad, text="", bg=BG_COLOR, font=("Segoe UI", 10, "bold"), fg="#ffffff")
        self.lbl_status.pack(pady=2)
        
        self.preview_frame = tk.Frame(pad, bg=BG_COLOR)
        self.preview_frame.pack(fill="x", pady=2)
        
        self.frame_prev = tk.Frame(self.preview_frame, bg=BG_COLOR)
        self.lbl_title_prev = tk.Label(self.frame_prev, text="", bg=BG_COLOR, font=("Segoe UI", 8, "bold"), fg="#ffffff")
        self.lbl_title_prev.pack(anchor="w", pady=(0, 2))
        self.lbl_preview_prev = tk.Label(self.frame_prev, text="", bg="#f0f0f0")
        self.lbl_preview_prev.pack(fill="x")

        self.frame_curr = tk.Frame(self.preview_frame, bg=BG_COLOR)
        self.lbl_title_curr = tk.Label(self.frame_curr, text="", bg=BG_COLOR, font=("Segoe UI", 8, "bold"), fg="#ffffff")
        self.lbl_title_curr.pack(anchor="w", pady=(0, 2))
        self.lbl_preview_curr = tk.Label(self.frame_curr, text="", bg="#f0f0f0")
        self.lbl_preview_curr.pack(fill="x")
        
        self.frame_prev.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.frame_curr.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        self.btn_folder_1 = tk.Button(pad, text="", command=self.open_folder, relief="flat", bg=BG_COLOR, fg=ACCENT_COLOR, cursor="hand2", font=("Segoe UI", 9, "underline"))
        self.btn_folder_1.pack(pady=5)

    def adjust_preview_layout(self, w, h):
        self.frame_prev.pack_forget()
        self.frame_curr.pack_forget()
        
        if w > h * 1.2:
            self.preview_mode = "vertical"
            self.frame_prev.pack(side="top", fill="x", expand=True, pady=(0, 5))
            self.frame_curr.pack(side="top", fill="x", expand=True, pady=(5, 0))
        else:
            self.preview_mode = "horizontal"
            self.frame_prev.pack(side="left", fill="both", expand=True, padx=(0, 5))
            self.frame_curr.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        self.root.update_idletasks()

    def setup_ai_tab(self):
        sf = ScrollableFrame(self.tab_ai, bg=BG_COLOR)
        sf.pack(fill="both", expand=True)
        content = sf.scrollable_content
        pad = tk.Frame(content, bg=BG_COLOR, padx=20, pady=10)
        pad.pack(fill="both", expand=True)

        self.lbl_sec_ai_ctx = self.create_header(pad, "")
        
        self.lbl_job = tk.Label(pad, text="", bg=BG_COLOR)
        self.lbl_job.pack(anchor="w")
        tk.Entry(pad, textvariable=self.var_job, bg="#f0f0f0").pack(fill="x", pady=2)
        
        self.lbl_comp = tk.Label(pad, text="", bg=BG_COLOR)
        self.lbl_comp.pack(anchor="w")
        tk.Entry(pad, textvariable=self.var_comp, bg="#f0f0f0").pack(fill="x", pady=2)
        
        self.lbl_dept = tk.Label(pad, text="", bg=BG_COLOR)
        self.lbl_dept.pack(anchor="w")
        tk.Entry(pad, textvariable=self.var_dept, bg="#f0f0f0").pack(fill="x", pady=2)
        
        self.lbl_title = tk.Label(pad, text="", bg=BG_COLOR)
        self.lbl_title.pack(anchor="w")
        tk.Entry(pad, textvariable=self.var_title, bg="#f0f0f0").pack(fill="x", pady=2)
        self.lbl_trans_lang = tk.Label(pad, text="", bg=BG_COLOR)
        self.lbl_trans_lang.pack(anchor="w", pady=(5,0))
        tk.Entry(pad, textvariable=self.var_trans_lang, bg="#f0f0f0").pack(fill="x", pady=2)


        self.btn_gen_prompt = tk.Button(pad, text="🔄 Update Prompt", command=self.update_ai_prompt_text, bg="#e0e0e0", relief="flat")
        self.btn_gen_prompt.pack(fill="x", pady=8)

        self.lbl_sec_ai_gen = self.create_header(pad, "")
        self.txt_prompt = tk.Text(pad, height=14, bg="#f5f5f5", font=("Segoe UI", 9), wrap="word", relief="flat")
        self.txt_prompt.pack(fill="x", pady=5)

        self.btn_copy_prompt = self.styled_btn(pad, "", self.copy_prompt, ACCENT_COLOR, "white")
        self.btn_copy_prompt.pack(fill="x", pady=10)

    def setup_ocr_tab(self):
        sf = ScrollableFrame(self.tab_ocr, bg=BG_COLOR)
        sf.pack(fill="both", expand=True)
        content = sf.scrollable_content
        pad = tk.Frame(content, bg=BG_COLOR, padx=20, pady=10)
        pad.pack(fill="both", expand=True)

        self.lbl_sec_ocr_opts = self.create_header(pad, "")
        
        self.lbl_lang = tk.Label(pad, text="", bg=BG_COLOR)
        self.lbl_lang.pack(anchor="w", pady=(5,0))
        self.combo_ocr = ttk.Combobox(pad, values=list(OCR_LANGS.keys()), state="readonly")
        self.combo_ocr.current(0)
        self.combo_ocr.pack(fill="x", pady=5)

        self.lbl_preproc = tk.Label(pad, text="", bg=BG_COLOR)
        self.lbl_preproc.pack(anchor="w", pady=(5,0))
        self.combo_preproc = ttk.Combobox(pad, values=list(PREPROC_KEYS), state="readonly")
        self.combo_preproc.current(1) 
        self.combo_preproc.pack(fill="x", pady=5)

        self.lbl_psm = tk.Label(pad, text="", bg=BG_COLOR)
        self.lbl_psm.pack(anchor="w", pady=(5,0))
        self.combo_psm = ttk.Combobox(pad, values=list(PSM_MAPPING.keys()), state="readonly")
        self.combo_psm.current(1)
        self.combo_psm.pack(fill="x", pady=5)

        self.grp_content = tk.LabelFrame(pad, text="", bg=BG_COLOR, padx=10, pady=5)
        self.grp_content.pack(fill="x", pady=10)
        self.chk_date = tk.Checkbutton(self.grp_content, text="", variable=self.var_ocr_date, bg=BG_COLOR, activebackground=BG_COLOR)
        self.chk_date.pack(anchor="w")
        self.chk_file = tk.Checkbutton(self.grp_content, text="", variable=self.var_ocr_file, bg=BG_COLOR, activebackground=BG_COLOR)
        self.chk_file.pack(anchor="w")

        self.lbl_sec_ocr_run = self.create_header(pad, "")
        
        fr_auto = tk.Frame(pad, bg=BG_COLOR)
        fr_auto.pack(fill="x", pady=(0, 10))
        
        self.chk_auto_files = tk.Checkbutton(fr_auto, text="", variable=self.var_auto_files, bg=BG_COLOR, activebackground=BG_COLOR, font=("Segoe UI", 9, "bold"), fg=DARK_COLOR)
        self.chk_auto_files.pack(side="left")
        
        self.btn_clear_session = tk.Button(fr_auto, text="🗑️", command=self.clear_session_files, relief="flat", bg="#f0f0f0", cursor="hand2")
        self.btn_clear_session.pack(side="left", padx=10)

        
        self.fr_progress = tk.Frame(pad, bg=BG_COLOR)
        self.lbl_progress = tk.Label(self.fr_progress, text="0 / 0", bg=BG_COLOR, font=("Segoe UI", 9))
        self.lbl_progress.pack(side="top", pady=2)
        self.progress_bar = ttk.Progressbar(self.fr_progress, orient="horizontal", mode="determinate")
        self.progress_bar.pack(side="top", fill="x", pady=2)
        # Hidden by default
        # self.fr_progress.pack(fill="x", pady=(5, 5))

        self.btn_ocr = self.styled_btn(pad, "", self.start_ocr, DARK_COLOR, "white")
        self.btn_ocr.pack(fill="x", pady=(5, 10))
        
        self.lbl_chat_info = tk.Label(pad, text="", bg=BG_COLOR, fg="#dddddd", justify="center", font=("Segoe UI", 9))
        self.lbl_chat_info.pack(fill="x", pady=(5, 2))
        self.btn_chat = self.styled_btn(pad, "", self.open_ai_chat, EDGE_BLUE, "white")
        self.btn_chat.pack(fill="x", pady=(0, 10))

    def setup_settings_tab(self):
        sf = ScrollableFrame(self.tab_set, bg=BG_COLOR)
        sf.pack(fill="both", expand=True)
        content = sf.scrollable_content
        pad = tk.Frame(content, bg=BG_COLOR, padx=20, pady=10)
        pad.pack(fill="both", expand=True)

        self.lbl_sec_cap_mode = self.create_header(pad, "")
        
        self.rb_screen = tk.Radiobutton(pad, text="", variable=self.var_cap_mode, value="screen", bg=BG_COLOR, font=("Segoe UI", 9, "bold"))
        self.rb_screen.pack(anchor="w", pady=(5,0))
        
        self.rb_window = tk.Radiobutton(pad, text="", variable=self.var_cap_mode, value="window", bg=BG_COLOR, font=("Segoe UI", 9, "bold"))
        self.rb_window.pack(anchor="w", pady=(5,0))
        
        fr_win = tk.Frame(pad, bg=BG_COLOR)
        fr_win.pack(fill="x", pady=(5,10), padx=(25, 0))
        self.lbl_win_title = tk.Label(fr_win, text="", bg=BG_COLOR)
        self.lbl_win_title.pack(side="left")
        
        self.entry_win_title = tk.Entry(fr_win, textvariable=self.var_win_title, bg="#e0e0e0", width=40, state="readonly", font=("Consolas", 9))
        self.entry_win_title.pack(side="left", padx=10)

        self.lbl_sec_paths = self.create_header(pad, "")
        self.lbl_tess_path = tk.Label(pad, text="", bg=BG_COLOR, anchor="w", font=("Segoe UI", 9, "bold"))
        self.lbl_tess_path.pack(fill="x", pady=(5, 0))
        fr_tess = tk.Frame(pad, bg=BG_COLOR)
        fr_tess.pack(fill="x", pady=2)
        tk.Entry(fr_tess, textvariable=self.var_tess_path, bg="#f0f0f0").pack(side="left", fill="x", expand=True, padx=(0,5))
        self.btn_browse_tess = tk.Button(fr_tess, text="...", command=self.browse_tess)
        self.btn_browse_tess.pack(side="right")
        
        self.lbl_out_dir = tk.Label(pad, text="", bg=BG_COLOR, anchor="w", font=("Segoe UI", 9, "bold"))
        self.lbl_out_dir.pack(fill="x", pady=(10, 0))
        fr_out = tk.Frame(pad, bg=BG_COLOR)
        fr_out.pack(fill="x", pady=2)
        tk.Entry(fr_out, textvariable=self.var_out_dir, bg="#f0f0f0").pack(side="left", fill="x", expand=True, padx=(0,5))
        self.btn_browse_out = tk.Button(fr_out, text="...", command=self.browse_out)
        self.btn_browse_out.pack(side="right")
        
        self.lbl_sec_info = self.create_header(pad, "")
        self.lbl_info_text = tk.Label(pad, text="", bg=BG_COLOR, justify="left", fg="#dddddd")
        self.lbl_info_text.pack(anchor="w", pady=5)
        self.lbl_link = tk.Label(pad, text="", bg=BG_COLOR, fg="blue", cursor="hand2", font=("Segoe UI", 10, "underline"))
        self.lbl_link.pack(anchor="w", pady=(0, 10))
        self.lbl_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/UB-Mannheim/tesseract/wiki"))


        # ── AI Chat Settings ──────────────────────────────────────────────
        tk.Frame(pad, bg=ACCENT_COLOR, height=2).pack(fill="x", pady=(14, 4))
        tk.Label(pad, text="🌐 AI Chat Einstellungen / AI Chat Settings",
                 bg=BG_COLOR, fg=ACCENT_COLOR, font=("Segoe UI", 11, "bold")).pack(anchor="w")

        tk.Label(pad, text="URL (z.B. https://claude.ai  |  https://gemini.google.com)",
                 bg=BG_COLOR, font=("Segoe UI", 8), fg="#666666").pack(anchor="w", pady=(6, 0))
        tk.Entry(pad, textvariable=self.var_ai_url, bg="#f0f0f0",
                 font=("Segoe UI", 9)).pack(fill="x", pady=2)

        tk.Label(pad, text="Browser", bg=BG_COLOR, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8, 2))
        browser_frame = tk.Frame(pad, bg=BG_COLOR)
        browser_frame.pack(fill="x")
        for label, val in [("Standard (Default)", "default"), ("Microsoft Edge", "msedge"),
                           ("Google Chrome", "chrome"), ("Mozilla Firefox", "firefox")]:
            tk.Radiobutton(browser_frame, text=label, variable=self.var_ai_browser,
                           value=val, bg=BG_COLOR, activebackground=BG_COLOR,
                           selectcolor="#d0e8ff", font=("Segoe UI", 9)
                           ).pack(side="left", padx=6)


    def setup_info_tab(self):
        pad = tk.Frame(self.tab_info, bg=BG_COLOR)
        pad.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(pad, text="SmartCapture Pro", font=("Segoe UI", 16, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR).pack(anchor="w")
        tk.Label(pad, text="Version: v23.3 | Stand: 13.05.2026", font=("Segoe UI", 10), bg=BG_COLOR, fg=DARK_COLOR).pack(anchor="w", pady=(0, 15))

        info_frame = tk.Frame(pad, bg="#f0f0f0", padx=15, pady=15)
        info_frame.pack(fill="x", pady=10)

        tk.Label(info_frame, text="Developer:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0", fg=ACCENT_COLOR).grid(row=0, column=0, sticky="w", pady=2)
        tk.Label(info_frame, text="basecore", font=("Segoe UI", 10), bg="#f0f0f0", fg=DARK_COLOR).grid(row=0, column=1, sticky="w", padx=10, pady=2)

        tk.Label(info_frame, text="Email:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0", fg=ACCENT_COLOR).grid(row=1, column=0, sticky="w", pady=2)
        lbl_email = tk.Label(info_frame, text="basecore@gmx.de", font=("Segoe UI", 10, "underline"), bg="#f0f0f0", fg="#0055cc", cursor="hand2")
        lbl_email.grid(row=1, column=1, sticky="w", padx=10, pady=2)
        lbl_email.bind("<Button-1>", lambda e: webbrowser.open("mailto:basecore@gmx.de"))

        tk.Label(info_frame, text="GitHub:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0", fg=ACCENT_COLOR).grid(row=2, column=0, sticky="w", pady=2)
        lbl_gh = tk.Label(info_frame, text="github.com/basecore/SmartCapture-Pro", font=("Segoe UI", 10, "underline"), bg="#f0f0f0", fg="#0055cc", cursor="hand2")
        lbl_gh.grid(row=2, column=1, sticky="w", padx=10, pady=2)
        lbl_gh.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/basecore/SmartCapture-Pro"))

        tk.Label(info_frame, text="Issues:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0", fg=ACCENT_COLOR).grid(row=3, column=0, sticky="w", pady=2)
        lbl_issues = tk.Label(info_frame, text="Report an Issue", font=("Segoe UI", 10, "underline"), bg="#f0f0f0", fg="#0055cc", cursor="hand2")
        lbl_issues.grid(row=3, column=1, sticky="w", padx=10, pady=2)
        lbl_issues.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/basecore/SmartCapture-Pro/issues"))

        tk.Frame(pad, height=2, bg=ACCENT_COLOR).pack(fill="x", pady=15)

        self.lbl_about_title = tk.Label(pad, text="Über dieses Tool", font=("Segoe UI", 12, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR)
        self.lbl_about_title.pack(anchor="w")

        self.lbl_about_text = tk.Label(pad, text="Generiert mit Gemini 3.1 Pro.\nSmartCapture Pro ist ein Tool zur Automatisierung von OCR-Erfassung für Live-Transkripte.", 
                 font=("Segoe UI", 10), bg=BG_COLOR, fg=DARK_COLOR, justify="left", wraplength=600)
        self.lbl_about_text.pack(anchor="w", pady=(5, 0))

    # --- LOGIK ---

    def update_interval_label(self, val):
        self.lbl_interval_val.config(text=f"{float(val):.1f}s")

    def get_ai_prompt_string(self):
        tmpl = PROMPT_TEMPLATE_DE if self.current_lang == "DE" else PROMPT_TEMPLATE_EN

        trans_note = ""
        if hasattr(self, 'var_trans_lang') and self.var_trans_lang.get().strip():
            trans_note = "\n[WICHTIGER HINWEIS ZUR TRANSKRIPTION]: " + self.var_trans_lang.get().strip() + "\n" if self.current_lang == "DE" else "\n[IMPORTANT TRANSCRIPT NOTE]: " + self.var_trans_lang.get().strip() + "\n"

        return tmpl.format(
            job=self.var_job.get(),
            comp=self.var_comp.get(),
            dept=self.var_dept.get(),
            title=self.var_title.get(),
            trans_note=trans_note
        )
    def update_ai_prompt_text(self):
        txt = self.get_ai_prompt_string()
        self.txt_prompt.config(state="normal")
        self.txt_prompt.delete("1.0", tk.END)
        self.txt_prompt.insert("1.0", txt)
        self.txt_prompt.config(state="disabled")

    def copy_prompt(self):
        self.update_ai_prompt_text()
        txt = self.txt_prompt.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(txt)
        messagebox.showinfo("Info", self.t("msg_copied"))

    def open_ai_chat(self):
        if not self.last_export_text:
            messagebox.showwarning(self.t("err_title"), self.t("err_no_export"))
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_export_text)
        self.root.update()

        url     = self.var_ai_url.get().strip() or AI_CHAT_URL
        browser = self.var_ai_browser.get().strip()

        messagebox.showinfo("Info", self.t("msg_chat_copied"))

        try:
            if browser in ("default", ""):
                webbrowser.open(url)
            elif browser == "msedge":
                subprocess.Popen(["cmd", "/c", "start", "msedge", url])
            elif browser == "chrome":
                subprocess.Popen(["cmd", "/c", "start", "chrome", url])
            elif browser == "firefox":
                subprocess.Popen(["cmd", "/c", "start", "firefox", url])
            else:
                webbrowser.open(url)
        except Exception:
            webbrowser.open(url)

    def browse_tess(self):
        f = filedialog.askopenfilename(filetypes=[("Executable", "*.exe")], title="Select tesseract.exe")
        if f: self.var_tess_path.set(f)

    def browse_out(self):
        d = filedialog.askdirectory(title="Select Output Folder")
        if d: self.var_out_dir.set(d)

    def find_tesseract_auto(self):
        local = os.getenv('LOCALAPPDATA', '')
        if not local:
            local = os.path.expanduser('~\\AppData\\Local')
            
        paths = [
            os.path.join(local, r'Programs\Tesseract-OCR\tesseract.exe'),
            r'C:\Program Files\Tesseract-OCR\tesseract.exe', 
            os.path.join(local, r'Tesseract-OCR\tesseract.exe')
        ]
        from shutil import which
        if which('tesseract'): return 'tesseract'
        for p in paths:
            if os.path.exists(p): return p
        return None

    def toggle_language(self):
        self.current_lang = "EN" if self.current_lang == "DE" else "DE"
        self.update_texts()
        self.update_session_file_count()

    def t(self, key): return TEXTS[key][self.current_lang]

    def update_texts(self):
        self.notebook.tab(self.tab_rec, text=self.t("tab_rec"))
        self.notebook.tab(self.tab_ai, text=self.t("tab_ai"))
        self.notebook.tab(self.tab_ocr, text=self.t("tab_ocr"))
        self.notebook.tab(self.tab_set, text=self.t("tab_set"))
        
        pre_vals = [TEXTS[f"dd_preproc_{k}"][self.current_lang] for k in PREPROC_KEYS]
        self.combo_preproc['values'] = pre_vals
        if self.combo_preproc.current() == -1: self.combo_preproc.current(1)
        
        psm_keys = list(PSM_MAPPING.keys())
        psm_vals = [TEXTS[f"dd_psm_{k}"][self.current_lang] for k in psm_keys]
        self.combo_psm['values'] = psm_vals
        if self.combo_psm.current() == -1: self.combo_psm.current(1)

        # TAB REC
        self.lbl_sec_area.config(text=self.t("sec_area"))
        self.lbl_instr_area.config(text=self.t("instr_area"))
        self.btn_show.config(text=self.t("btn_frame"))
        self.btn_lock.config(text=self.t("btn_lock"))
        if not self.area_locked: self.lbl_info.config(text=self.t("lbl_no_area"))
        self.lbl_sec_proc.config(text=self.t("sec_proc"))
        self.lbl_interval.config(text=self.t("lbl_interval"))
        self.btn_start.config(text=self.t("btn_start"))
        self.btn_stop.config(text=self.t("btn_stop"))
        if not self.is_recording: self.lbl_status.config(text=self.t("status_ready"))
        
        if not self.last_img:
            self.lbl_preview_prev.config(text=self.t("preview_ph"))
            self.lbl_preview_curr.config(text=self.t("preview_ph"))
        self.lbl_title_prev.config(text=self.t("lbl_prev"))
        self.lbl_title_curr.config(text=self.t("lbl_curr"))
            
        self.btn_folder_1.config(text=self.t("btn_folder"))
        
        # TAB OCR
        self.lbl_sec_ocr_opts.config(text=self.t("sec_ocr_opts"))
        self.lbl_lang.config(text=self.t("lbl_lang"))
        self.lbl_preproc.config(text=self.t("lbl_preproc"))
        self.lbl_psm.config(text=self.t("lbl_psm"))
        self.grp_content.config(text=self.t("grp_content"))
        self.chk_date.config(text=self.t("chk_date"))
        self.chk_file.config(text=self.t("chk_file"))
        self.lbl_sec_ocr_run.config(text=self.t("sec_ocr_run"))
        self.btn_ocr.config(text=self.t("btn_ocr"))
        self.btn_clear_session.config(text=self.t("btn_clear_session"))
        self.lbl_chat_info.config(text=self.t("info_chat"))
        self.btn_chat.config(text=self.t("btn_chat"))

        # TAB AI
        self.lbl_sec_ai_ctx.config(text=self.t("sec_ai_ctx"))
        self.lbl_job.config(text=self.t("lbl_job"))
        self.lbl_comp.config(text=self.t("lbl_comp"))
        self.lbl_dept.config(text=self.t("lbl_dept"))
        self.lbl_title.config(text=self.t("lbl_title"))
        self.lbl_sec_ai_gen.config(text=self.t("sec_ai_gen"))
        self.btn_gen_prompt.config(text=self.t("btn_gen_prompt"))
        self.btn_copy_prompt.config(text=self.t("btn_copy"))
        self.update_ai_prompt_text()
        
        # TAB SETTINGS
        self.lbl_sec_cap_mode.config(text=self.t("sec_cap_mode"))
        self.rb_screen.config(text=self.t("rb_screen"))
        self.rb_window.config(text=self.t("rb_window"))
        self.lbl_win_title.config(text=self.t("lbl_win_title"))
        
        self.lbl_sec_paths.config(text=self.t("sec_paths"))
        self.lbl_tess_path.config(text=self.t("lbl_tess_path"))
        self.lbl_out_dir.config(text=self.t("lbl_out_dir"))
        self.btn_browse_tess.config(text=self.t("btn_browse"))
        self.btn_browse_out.config(text=self.t("btn_browse"))
        self.lbl_sec_info.config(text=self.t("sec_info"))
        self.lbl_info_text.config(text=self.t("info_text"))
        self.lbl_link.config(text=self.t("link_text"))

        
        if hasattr(self, 'lbl_about_title'):
            self.lbl_about_title.config(text=self.t("lbl_about_title"))
        if hasattr(self, 'lbl_about_text'):
            self.lbl_about_text.config(text=self.t("lbl_about_text"))

        if hasattr(self, 'tab_set'):
            # In update_texts, we update the tab text:
            idx = self.notebook.index(self.tab_set)
            self.notebook.tab(idx, text="Settings" if self.current_lang == "EN" else "Einstellungen")
        if hasattr(self, 'tab_info'):
            idx = self.notebook.index(self.tab_info)
            self.notebook.tab(idx, text="Info")

        if hasattr(self, 'lbl_trans_lang'):
            self.lbl_trans_lang.config(text=self.t("lbl_trans_lang"))

    def update_session_file_count(self):
        if hasattr(self, 'chk_auto_files'):
            txt = self.t("chk_auto_files").format(n=len(self.session_files))
            self.chk_auto_files.config(text=txt)

    def clear_session_files(self):
        self.session_files.clear()
        self.update_session_file_count()

    def open_selector(self):
        if self.selector_win and self.selector_win.winfo_exists():
            self.selector_win.destroy()
            
        self.selector_win = ResizableSelectionWindow(self.root, self.t("lbl_frame_pull"))
        if self.last_frame_geo:
            self.selector_win.geometry(self.last_frame_geo)
            
        self.area_locked = False
        self.lbl_info.config(text=self.t("lbl_no_area"), fg="gray")

    def lock_selector(self):
        if not self.selector_win or not self.selector_win.winfo_exists():
            messagebox.showerror(self.t("err_title"), self.t("err_no_frame"))
            self.selector_win = None 
            return
            
        self.root.update_idletasks()

        # Speichere die exakte Fenster-Geometrie zum Wiederherstellen
        self.last_frame_geo = self.selector_win.geometry()

        # Hole die absoluten inneren Koordinaten für den Screenshot
        wx, wy = self.selector_win.winfo_rootx(), self.selector_win.winfo_rooty()
        ww, wh = self.selector_win.winfo_width(), self.selector_win.winfo_height()

        BORDER = 10
        self.selector_win.destroy()
        self.selector_win = None
        self.root.update()
        
        m_left = int(wx + BORDER)
        m_top = int(wy + BORDER)
        m_width = int(ww - 2*BORDER)
        m_height = int(wh - 2*BORDER)
        self.monitor_area = { "top": m_top, "left": m_left, "width": m_width, "height": m_height, "mon": -1 }
        
        self.adjust_preview_layout(m_width, m_height)
        
        center_x = m_left + (m_width // 2)
        center_y = m_top + (m_height // 2)
        
        mon_idx = 1
        with mss.mss() as sct:
            for i, m in enumerate(sct.monitors[1:], 1):
                if m["left"] <= center_x <= m["left"] + m["width"] and m["top"] <= center_y <= m["top"] + m["height"]:
                    mon_idx = i
                    break
        
        hwnd_at_point = win32gui.WindowFromPoint((center_x, center_y))
        root_hwnd = windll.user32.GetAncestor(hwnd_at_point, 2)
        
        detected_title = "Desktop / Unbekannt"
        if root_hwnd:
            t = win32gui.GetWindowText(root_hwnd)
            if t: detected_title = t
            
            self.window_hwnd = root_hwnd
            self.var_win_title.set(detected_title)
            
            if detected_title != "Desktop / Unbekannt":
                clean_title = detected_title
                if " | " in clean_title: clean_title = clean_title.split(" | ")[0].strip()
                elif " - " in clean_title: clean_title = clean_title.split(" - ")[0].strip()
                self.var_title.set(clean_title)
                self.update_ai_prompt_text()

            win_left, win_top, win_right, win_bottom = win32gui.GetWindowRect(root_hwnd)
            win_w = win_right - win_left
            win_h = win_bottom - win_top
            
            self.rel_area = {
                "left": m_left - win_left,
                "top": m_top - win_top,
                "width": m_width,
                "height": m_height,
                "p_left": (m_left - win_left) / win_w if win_w > 0 else 0,
                "p_top": (m_top - win_top) / win_h if win_h > 0 else 0,
                "p_width": m_width / win_w if win_w > 0 else 0,
                "p_height": m_height / win_h if win_h > 0 else 0
            }
        
        self.area_locked = True
        wrapped_title = textwrap.fill(detected_title, width=60)
        
        if self.var_cap_mode.get() == "window" and detected_title != "Desktop / Unbekannt":
            txt = self.t("lbl_area_ok_win").format(w=m_width, h=m_height, mon=mon_idx, title=wrapped_title)
        else:
            txt = self.t("lbl_area_ok").format(w=m_width, h=m_height, mon=mon_idx)
            
        self.lbl_info.config(text=txt, fg=ACCENT_COLOR)
        self.update_preview_once()

    def capture_screen(self):
        if self.var_cap_mode.get() == "screen":
            if self.monitor_area['width'] < 10: return None
            try:
                with mss.mss() as sct: 
                    return Image.frombytes("RGB", sct.grab(self.monitor_area).size, sct.grab(self.monitor_area).bgra, "raw", "BGRX")
            except: 
                return None
        else:
            if not self.window_hwnd or not self.rel_area: 
                return None
            return self.capture_specific_window(self.window_hwnd, self.rel_area)

    def capture_specific_window(self, hwnd, rel_area):
        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            if width <= 0 or height <= 0: return None

            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)

            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            
            img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            if result == 1:
                r_l = int(rel_area["p_left"] * width)
                r_t = int(rel_area["p_top"] * height)
                r_w = int(rel_area["p_width"] * width)
                r_h = int(rel_area["p_height"] * height)
                
                r_r = r_l + r_w
                r_b = r_t + r_h
                
                r_l = max(0, r_l)
                r_t = max(0, r_t)
                r_r = min(width, r_r)
                r_b = min(height, r_b)
                
                if r_r <= r_l or r_b <= r_t:
                    return None
                    
                return img.crop((r_l, r_t, r_r, r_b))
            return None
        except Exception as e:
            print("Capture Error:", e)
            return None

    def update_preview_once(self):
        img = self.capture_screen()
        if img:
            self.adjust_preview_layout(img.width, img.height)
            self.show_preview(self.lbl_preview_prev, None)
            self.show_preview(self.lbl_preview_curr, img)

    def show_preview(self, label, img):
        if img is None:
            label.config(image="", text=self.t("preview_ph"))
            label.photo = None
            return
            
        if getattr(self, "preview_mode", "horizontal") == "vertical":
            target_w = self.root.winfo_width() - 100
            max_h = 350
        else:
            target_w = 120
            max_h = 80
            
        if target_w < 100: target_w = 120
        
        w_p = (target_w / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_p)))
        
        if h_size > max_h: h_size = max_h
        
        thumb = img.copy()
        thumb = thumb.resize((int(target_w), int(h_size)), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(thumb)
        
        label.config(image=photo, width=target_w, height=h_size, text="")
        label.photo = photo

    def start_recording(self):
        if not self.area_locked or self.monitor_area['width'] < 10:
            messagebox.showwarning(self.t("err_title"), self.t("err_not_locked"))
            return
        out_d = self.var_out_dir.get()
        if not os.path.exists(out_d): os.makedirs(out_d)
        
        self.is_recording = True
        self.btn_start.config(state="disabled", bg="#cccccc")
        self.btn_stop.config(state="normal", bg="#d9534f")
        self.lbl_status.config(text=self.t("status_rec"), fg="red")
        
        self.img_counter = 0
        self.last_img = None
        self.show_preview(self.lbl_preview_prev, None)
        self.show_preview(self.lbl_preview_curr, None)
        
        self.record_loop()

    def stop_recording(self):
        self.is_recording = False
        self.btn_start.config(state="normal", bg=ACCENT_COLOR)
        self.btn_stop.config(state="disabled", bg="#888888")
        txt = self.t("status_stop").format(n=self.img_counter)
        self.lbl_status.config(text=txt, fg="#ffffff")

    def record_loop(self):
        if not self.is_recording: return
        curr = self.capture_screen()
        if curr:
            is_diff = True
            if self.last_img and curr.size == self.last_img.size:
                diff = ImageStat.Stat(ImageChops.difference(self.last_img, curr))
                if sum(diff.mean) < 2.0: is_diff = False
            
            if is_diff:
                ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                fn = os.path.join(self.var_out_dir.get(), f"screen_{ts}.png")
                curr.save(fn)
                
                self.show_preview(self.lbl_preview_prev, self.last_img)
                self.show_preview(self.lbl_preview_curr, curr)
                
                self.last_img = curr
                self.img_counter += 1
                
                self.session_files.append(fn)
                self.update_session_file_count()
                
                txt = self.t("status_saved").format(fn=os.path.basename(fn))
                self.lbl_status.config(text=txt, fg=ACCENT_COLOR)
            else:
                self.lbl_status.config(text=self.t("status_wait"), fg="#aaaaaa")
        
        wait_ms = int(self.interval_var.get() * 1000)
        self.root.after(wait_ms, self.record_loop)

    def open_folder(self):
        out_d = self.var_out_dir.get()
        if not os.path.exists(out_d): os.makedirs(out_d)
        os.startfile(os.path.abspath(out_d))

    def preprocess_image(self, img, mode_key):
        if mode_key not in PREPROC_KEYS: mode_key = "none"
        if mode_key == "none": return img
        if mode_key == "gray_contrast":
            img = ImageOps.grayscale(img)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
        if mode_key == "scale2x":
            w, h = img.size
            img = img.resize((w*2, h*2), Image.Resampling.LANCZOS)
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
        return img

    def start_ocr(self):
        tess = self.var_tess_path.get()
        if not os.path.exists(tess):
            messagebox.showerror(self.t("err_title"), self.t("err_tess"))
            return
        pytesseract.pytesseract.tesseract_cmd = tess
        
        if self.var_auto_files.get() and len(self.session_files) > 0:
            fps = self.session_files
        else:
            out_d = self.var_out_dir.get()
            if not os.path.exists(out_d): os.makedirs(out_d)
            fps = filedialog.askopenfilenames(initialdir=out_d, filetypes=[("Images", "*.png *.jpg")])
            
        if not fps: return
        
        lang_key = self.combo_ocr.get()
        lang_code = OCR_LANGS.get(lang_key, "jpn+eng")
        
        curr_psm_val = self.combo_psm.get()
        psm_key = "block"
        for k in PSM_MAPPING.keys():
            if TEXTS[f"dd_psm_{k}"][self.current_lang] == curr_psm_val:
                psm_key = k
                break
        psm_arg = PSM_MAPPING[psm_key]

        curr_pre_val = self.combo_preproc.get()
        preproc_key = "scale2x"
        for k in PREPROC_KEYS:
            if TEXTS[f"dd_preproc_{k}"][self.current_lang] == curr_pre_val:
                preproc_key = k
                break
        
        inc_date = self.var_ocr_date.get()
        inc_file = self.var_ocr_file.get()
        
        files = natsorted(list(fps))
        pw = tk.Toplevel(self.root)
        pw.title(self.t("progress_title"))
        lbl = tk.Label(pw, text=self.t("progress_init"), padx=20, pady=20)
        lbl.pack()
        self.root.update()
        
        now_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
        
        prompt_txt = self.get_ai_prompt_string()
        full_text = f"{prompt_txt}\n\n"
        full_text += f"=== ORIGINAL OCR DATA START ===\n"
        full_text += f"Created: {now_str} | Settings: {lang_code}, {psm_arg}, {preproc_key}\n"
        
        for i, f in enumerate(files):
            pw.update()
            try:
                img = Image.open(f)
                img = self.preprocess_image(img, preproc_key)
                ocr_txt = pytesseract.image_to_string(img, lang=lang_code, config=psm_arg)
                
                if ocr_txt.strip() or inc_date or inc_file:
                    full_text += f"\n{'='*60}\n"
                    if inc_date:
                        mtime = os.path.getmtime(f)
                        dt = datetime.datetime.fromtimestamp(mtime)
                        full_text += f"📅 DATE: {dt.strftime('%d.%m.%Y')} | 🕒 TIME: {dt.strftime('%H:%M:%S')}\n"
                    if inc_file:
                        full_text += f"📄 FILE: {os.path.basename(f)}\n"
                    full_text += f"{'-'*60}\n{ocr_txt}\n"
            except Exception as e: print(e)
        
        pw.destroy()
        
        self.last_export_text = full_text
        fname = os.path.join(self.var_out_dir.get(), f"Export_{now_str}.txt")
        with open(fname, "w", encoding="utf-8") as f: f.write(full_text)
        os.startfile(fname)

    def create_header(self, parent, text):
        f = tk.Frame(parent, bg=BG_COLOR)
        f.pack(fill="x", pady=(5, 2))
        lbl = tk.Label(f, text=text, bg=BG_COLOR, fg=ACCENT_COLOR, font=("Segoe UI", 12, "bold"))
        lbl.pack(anchor="w")
        tk.Frame(f, bg=ACCENT_COLOR, height=2).pack(fill="x")
        return lbl

    def styled_btn(self, parent, text, cmd, bg, fg):
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, font=("Segoe UI", 10, "bold"), relief="flat", pady=4, cursor="hand2")

if __name__ == "__main__":
    
    root = tk.Tk()
    try:
        import sv_ttk
        sv_ttk.set_theme("dark")
    except ImportError:
        pass

    app = SmartCaptureApp(root)
    root.mainloop()
