import sys
import re
import subprocess
import os
import time
import datetime
import textwrap
import json  # ADDED: For config saving

# --- NEU: TKINTER INSTALLATIONS-PRÜFUNG ---
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError:
    print("=" * 60)
    print("FEHLER: Das Modul 'tkinter' fehlt in deiner Python-Installation.")
    print("Dieses wird zwingend fuer die Benutzeroberflaeche benoetigt.")
    print("LÖSUNG (Ohne Admin-Rechte möglich):")
    print("1. Gehe in den Windows-Einstellungen zu 'Installierte Apps'.")
    print("2. Suche nach deiner Python-Installation und klicke auf 'Ändern' / 'Modify'.")
    print("3. Klicke im Setup-Fenster auf 'Modify'.")
    print("4. Setze das Häkchen bei 'tcl/tk and IDLE' und klicke auf 'Next'.")
    print("=" * 60)
    sys.exit(1)  # Beendet das Skript sofort mit einem Fehlercode für die .bat
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
    "pytesseract": "pytesseract",
    "Pillow": "PIL",
    "natsort": "natsort",
    "mss": "mss",
    "pywin32": "win32gui"
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
def ensure_tesseract_installed():
    """Prüft auf Tesseract und installiert es inkl. Sprachpaketen (DE, JP) ohne Admin-Rechte in das lokale AppData Verzeichnis."""
    # --- SSL BYPASS FÜR FIRMENNETZWERKE / PROXY ---
    try:
        _create_unverified_https_context = ssl.create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    local_app_data = os.getenv("LOCALAPPDATA")
    if not local_app_data:
        local_app_data = os.path.expanduser("~")
    install_dir = os.path.join(local_app_data, r"Programs\Tesseract-OCR")
    tess_exe = os.path.join(install_dir, "tesseract.exe")
    tessdata_dir = os.path.join(install_dir, "tessdata")
    tess_found = False
    if which("tesseract"):
        tess_found = True
    elif os.path.exists(tess_exe):
        tess_found = True
    elif os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
        tess_found = True
        tessdata_dir = r"C:\Program Files\Tesseract-OCR\tessdata"

    if not tess_found:
        print("INFO DE: Tesseract OCR wurde nicht auf diesem System gefunden.")
        print("INFO EN: Tesseract OCR was not found on this system.")
        print("INFO DE: Hinweis: Tesseract ist ein sicheres, weltweit bewährtes Open-Source-Tool")
        print("         zur Texterkennung, das von der Universität Mannheim bereitgestellt wird.")
        print("INFO EN: Notice: Tesseract is a secure, globally proven open-source text")
        print("         recognition tool provided by the University of Mannheim.")
        print("INFO DE: Lade Tesseract herunter und installiere im Hintergrund (dies kann einen Moment dauern)...")
        print("INFO EN: Downloading and installing Tesseract in the background (this may take a moment)...")
        tess_url = "https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe"
        temp_exe = os.path.join(tempfile.gettempdir(), "tesseract_installer.exe")
        try:
            urllib.request.urlretrieve(tess_url, temp_exe)
            # Nullsoft NSIS Silent Installation Flags
            install_cmd = [temp_exe, "/S", f"/D={install_dir}"]
            subprocess.run(install_cmd, check=True)
            print("INFO DE: Tesseract (Uni Mannheim) wurde erfolgreich installiert!")
            print("INFO EN: Tesseract (Uni Mannheim) was installed successfully!")
        except Exception as e:
            print(f"FEHLER / ERROR: Installation fehlgeschlagen / Installation failed: {e}")
        finally:
            if os.path.exists(temp_exe):
                try:
                    os.remove(temp_exe)
                except:
                    pass

    os.makedirs(tessdata_dir, exist_ok=True)
    lang_packs = {
        "deu.traineddata": "https://github.com/tesseract-ocr/tessdata_fast/raw/main/deu.traineddata",
        "jpn.traineddata": "https://github.com/tesseract-ocr/tessdata_fast/raw/main/jpn.traineddata",
    }
    if os.access(tessdata_dir, os.W_OK):
        for lang_file, url in lang_packs.items():
            lang_path = os.path.join(tessdata_dir, lang_file)
            if not os.path.exists(lang_path):
                print(f"INFO DE: Lade Sprachpaket {lang_file} herunter...")
                print(f"INFO EN: Downloading language pack {lang_file}...")
                try:
                    urllib.request.urlretrieve(url, lang_path)
                    print(f"INFO DE: {lang_file} erfolgreich installiert.")
                    print(f"INFO EN: {lang_file} installed successfully.")
                except Exception as e:
                    print(f"WARNUNG / WARNING: Konnte / Could not download {lang_file}: {e}")

ensure_tesseract_installed()  # Direkt ausführen

# --- KONFIGURATION ---
SCHAEFFLER_GREEN = "#00893d"
SCHAEFFLER_DARK  = "#2c3e50"
EDGE_BLUE        = "#0078D7"
BG_COLOR         = "#ffffff"
TRANSPARENT_KEY  = "#ff00ff"
ACCENT_COLOR     = SCHAEFFLER_GREEN

# VERSION INFO
TOOL_NAME = "Schaeffler SmartCapture Pro"
TOOL_VER  = "v25.6 | Stand 18.06.2026"

# PSM MODES
PSM_MAPPING = {
    "auto":  "--psm 3",
    "block": "--psm 6",
    "line":  "--psm 7",
}

# PRE-PROCESSING
PREPROC_KEYS = ["none", "scale2x", "gray_contrast"]

PROMPT_TEMPLATE_DE = (
    "Ich arbeite als {job} bei {comp} im Bereich {dept}. "
    "Dies ist ein Transkript-Export eines Meetings mit dem Titel \"{title}\".\n"
    "Bitte verarbeite den folgenden OCR-Text nach diesen Regeln:\n"
    "1. DUPLIKATE: Da alle paar Sekunden ein Screenshot gemacht wurde, gibt es viele Überlappungen. "
    "Füge den Text zu einem einzigen Verlauf zusammen.\n"
    "2. KONTEXT: Behalte Fachbegriffe aus meinem Bereich bei.\n"
    "3. KORREKTUR: Korrigiere offensichtliche OCR-Fehler.\n"
    "4. ZUSAMMENFASSUNG: Extrahiere und strukturiere Entscheidungen, Diskussionspunkte, offene Fragen "
    "und daraus abgeleitete Maßnahmen/Aufgaben sowie die Teilnehmer aus dem zusammengefassten Transkript.\n"
    "5. STATISCHER HINTERGRUND / UNTERTITEL: Oft gibt es wiederkehrenden Hintergrundtext (z. B. Präsentationsfolien) "
    "und sich verändernde Untertitel im Vordergrund. Ignoriere den repetitiven Hintergrundtext über die Bilder hinweg "
    "und fokussiere dich auf den fließenden Text der Untertitel, um diese korrekt zu einem Verlauf zu verbinden.\n\n"
    "Hier ist der Text:\n"
)

PROMPT_TEMPLATE_EN = (
    "I work as a {job} at {comp} in the {dept} department. "
    "This is a transcript export of a meeting titled \"{title}\".\n"
    "Please process the following OCR text using these rules:\n"
    "1. DUPLICATES: Since screenshots were taken every few seconds, there are overlaps. "
    "Merge the text into a single flow.\n"
    "2. CONTEXT: Maintain technical terms relevant to my field.\n"
    "3. CORRECTION: Fix obvious OCR errors.\n"
    "4. SUMMARY: Extract and structure the following points from the consolidated transcript: "
    "Participants, decisions, discussion points, open issues, and action items/tasks.\n"
    "5. STATIC BACKGROUND / SUBTITLES: There is often recurring background text (e.g., presentation slides) "
    "and changing subtitles in the foreground. Ignore the repetitive background text across the images "
    "and focus on merging the flowing subtitle text into a continuous transcript.\n\n"
    "Here is the text:\n"
)

TEXTS = {
    "tab_rec":   {"DE": "Aufnahme 📷",        "EN": "Recording 📷"},
    "tab_ai":    {"DE": "AI Content 🤖",       "EN": "AI Content 🤖"},
    "tab_ocr":   {"DE": "OCR Export 📄",       "EN": "OCR Export 📄"},
    "tab_set":   {"DE": "Einstellungen ⚙️",    "EN": "Settings ⚙️"},
    "sec_area":  {"DE": "1. Aufnahmebereich definieren", "EN": "1. Define Capture Area"},
    "instr_area":{"DE": "Klicke 'Rahmen definieren'. Ein grüner Rahmen erscheint. Ziehe ihn über den Bereich.",
                  "EN": "Click 'Define Frame'. A green frame appears. Drag it over the area."},
    "btn_frame": {"DE": "Rahmen definieren",  "EN": "Define Frame"},
    "btn_lock":  {"DE": "Bereich übernehmen", "EN": "Confirm Area"},
    "lbl_no_area":{"DE": "Kein Bereich gewählt.", "EN": "No area selected."},
    "lbl_area_ok":{"DE": "✅ Fixiert {w}×{h} px | Monitor {mon}",
                   "EN": "✅ Locked {w}×{h} px | Monitor {mon}"},
    "lbl_area_ok_win":{"DE": "✅ Fixiert {w}×{h} px | Monitor {mon} | {title}",
                       "EN": "✅ Locked {w}×{h} px | Monitor {mon} | {title}"},
    "sec_proc":  {"DE": "2. Automatisierung",  "EN": "2. Automation"},
    "lbl_interval":{"DE": "Wartezeit zwischen Screenshots:", "EN": "Wait time between screenshots:"},
    "btn_start": {"DE": "▶ AUFNAHME STARTEN", "EN": "▶ START RECORDING"},
    "btn_stop":  {"DE": "⏹ STOPP",            "EN": "⏹ STOP"},
    "status_ready":{"DE": "Bereit.",           "EN": "Ready."},
    "status_rec":{"DE": "🔴 Aufnahme läuft...", "EN": "🔴 Recording..."},
    "status_stop":{"DE": "⏹ Gestoppt. {n} Bilder", "EN": "⏹ Stopped. {n} images"},
    "status_wait":{"DE": "👀 Überwache... Keine Änderung", "EN": "👀 Monitoring... No change"},
    "status_saved":{"DE": "💾 Gespeichert: {fn}", "EN": "💾 Saved: {fn}"},
    "preview_ph":{"DE": "Vorschau",            "EN": "Preview"},
    "lbl_prev":  {"DE": "Vorheriger Screenshot","EN": "Previous Screenshot"},
    "lbl_curr":  {"DE": "Aktueller Screenshot", "EN": "Current Screenshot"},
    "btn_folder":{"DE": "📂 Speicherordner öffnen", "EN": "📂 Open Output Folder"},
    "sec_ocr_opts":{"DE": "Export-Optionen",   "EN": "Export Options"},
    "lbl_lang":  {"DE": "Sprache:",            "EN": "Language:"},
    "lbl_preproc":{"DE": "Bild-Optimierung:",  "EN": "Image Optimization:"},
    "lbl_psm":   {"DE": "Layout-Modus:",       "EN": "Layout Mode:"},
    "grp_content":{"DE": "Inhalt des Exports", "EN": "Export Content"},
    "chk_date":  {"DE": "Datum/Uhrzeit einfügen", "EN": "Include DateTime"},
    "chk_file":  {"DE": "Dateiname einfügen",  "EN": "Include Filename"},
    "sec_ocr_run":{"DE": "Verarbeitung",       "EN": "Processing"},
    "btn_ocr":   {"DE": "🔍 Texterkennung starten & Exportieren", "EN": "🔍 Start OCR & Export"},
    "chk_auto_files":{"DE": "✅ Bilder der aktuellen Sitzung verwenden ({n} Bilder)",
                      "EN": "✅ Use images from current session ({n} images)"},
    "btn_clear_session": {"DE": "🗑️", "EN": "🗑️"},
    "btn_delete_session": {"DE": "🧨", "EN": "🧨"},
    "info_chat": {"DE": "Erzeugt Text → in Zwischenablage kopieren und Edge starten. Dort einfach mit Strg+V einfügen.",
                  "EN": "Copy generated text to clipboard and open Edge. Paste it there using Ctrl+V."},
    "btn_chat":  {"DE": "🌐 Schaeffler Chat öffnen (Edge) + Text kopieren",
                  "EN": "🌐 Open Schaeffler Chat (Edge) + Copy Text"},
    "err_no_export":{"DE": "Bitte starte zuerst die OCR-Verarbeitung und den Export!",
                     "EN": "Please run OCR processing and export first!"},
    "msg_chat_copied":{"DE": "✅ Text erfolgreich kopiert! Browser wird geöffnet...\nFüge den Text dort einfach in das Chat-Feld ein (Strg+V).",
                       "EN": "✅ Text successfully copied! Edge Browser...\nPaste the text into the chat field (Ctrl+V)."},
    "sec_ai_ctx":{"DE": "Kontext & Rolle",     "EN": "Context & Role"},
    "lbl_job":   {"DE": "Beruf / Rolle:",      "EN": "Job Title / Role:"},
    "lbl_comp":  {"DE": "Firma:",              "EN": "Company:"},
    "lbl_dept":  {"DE": "Bereich / Abteilung:","EN": "Department:"},
    "lbl_title": {"DE": "Meeting Titel:",      "EN": "Meeting Title:"},
    "sec_ai_gen":{"DE": "Generierter Prompt für ChatGPT/Copilot", "EN": "Generated Prompt for ChatGPT/Copilot"},
    "btn_gen_prompt":{"DE": "🔄 Prompt aktualisieren", "EN": "🔄 Update Prompt"},
    "btn_copy":  {"DE": "📋 Prompt kopieren",  "EN": "📋 Copy Prompt"},
    "msg_copied":{"DE": "✅ Prompt kopiert!",  "EN": "✅ Prompt copied!"},
    "sec_cap_mode":{"DE": "Aufnahmemethode (Engine)", "EN": "Capture Engine"},
    "rb_screen": {"DE": "Normal: Bildschirm abfotografieren", "EN": "Standard: Capture Screen directly"},
    "rb_window": {"DE": "Hintergrund: Verdeckte Fenster abgreifen", "EN": "Background: Capture covered windows"},
    "lbl_win_title":{"DE": "Erkanntes Ziel-Fenster:", "EN": "Detected Target Window:"},
    "sec_paths": {"DE": "Systempfade",         "EN": "System Paths"},
    "lbl_tess_path":{"DE": "Pfad zur tesseract.exe:", "EN": "Path to tesseract.exe:"},
    "lbl_out_dir":{"DE": "Speicherordner:",    "EN": "Output Folder:"},
    "btn_browse":{"DE": "Durchsuchen...",      "EN": "Browse..."},
    "sec_info":  {"DE": "Hilfe & Info",        "EN": "Help & Info"},
    "info_text": {"DE": "Tesseract OCR wird benötigt.", "EN": "Tesseract OCR is required."},
    "link_text": {"DE": "Tesseract Download (GitHub)", "EN": "Download Tesseract (GitHub)"},
    "dd_preproc_none":     {"DE": "Keine (Original)",         "EN": "None (Original)"},
    "dd_preproc_scale2x":  {"DE": "2x Skalierung (Scharf)",   "EN": "2x Scaling (Sharp)"},
    "dd_preproc_gray_contrast":{"DE": "Graustufen + Kontrast","EN": "Grayscale + Contrast"},
    "dd_psm_auto":  {"DE": "Auto (Standard)", "EN": "Auto (Default)"},
    "dd_psm_block": {"DE": "Block (Chat/Text)","EN": "Block (Chat/Text)"},
    "dd_psm_line":  {"DE": "Einzelne Zeile",  "EN": "Single Line"},
    "err_title": {"DE": "Fehler",             "EN": "Error"},
    "err_no_frame":{"DE": "Bitte erst den Rahmen definieren und das grüne Fenster nicht manuell schließen!",
                    "EN": "Please 'Define Frame' first and do not close the green window manually!"},
    "err_not_locked":{"DE": "Bereich noch nicht bestätigt!",
                      "EN": "Area not confirmed!"},
    "err_tess":  {"DE": "Tesseract.exe nicht gefunden!",
                  "EN": "Tesseract.exe not found!"},
    "err_win_not_found":{"DE": "Ziel-Fenster konnte nicht fokussiert werden! Ist es offen und nicht minimiert?",
                         "EN": "Target Window could not be focused! Is it open and not minimized?"},
    "progress_title":{"DE": "Verarbeite...",  "EN": "Processing..."},
    "progress_init": {"DE": "Initialisiere...","EN": "Initializing..."},
    "progress_step": {"DE": "Bild {i}/{n}",   "EN": "Image {i}/{n}"},
}

OCR_LANGS = {
    "Automatisch (Jap/Eng/Deu)": "jpn+eng+deu",
    "Japanisch + Englisch":       "jpn+eng",
    "Deutsch":                    "deu",
    "Englisch":                   "eng",
}


# ─────────────────────────────────────────────
# KLASSEN
# ─────────────────────────────────────────────
class ResizableSelectionWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Selector")
        self.geometry("600x400+100+100")
        self.attributes("-topmost", True)
        self.config(bg=SCHAEFFLER_GREEN)
        self.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        self.inner_frame = tk.Frame(self, bg=TRANSPARENT_KEY)
        self.inner_frame.pack(fill="both", expand=True, padx=10, pady=10)
        lbl = tk.Label(self, text=" RAHMEN ZIEHEN ", bg=SCHAEFFLER_GREEN, fg="white",
                       font=("Arial", 9, "bold"))
        lbl.place(x=0, y=0)
        ttk.Sizegrip(self).place(relx=1.0, rely=1.0, anchor="se")


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_content = tk.Frame(self.canvas, bg=BG_COLOR)
        self.canvas_window = self.canvas.create_window(0, 0, window=self.scrollable_content, anchor="nw")
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
        self.var_cap_mode = tk.StringVar(value="window")
        self.var_win_title = tk.StringVar(value="-- Automatische Erkennung --")
        self.window_hwnd = None
        self.rel_area = None
        self.monitor_area = {"top": 0, "left": 0, "width": 0, "height": 0}
        self.area_locked = False
        self.is_recording = False
        self.last_img = None
        self.img_counter = 0
        self.last_export_text = ""
        self.preview_mode = "horizontal"
        self.recording_start_dt = None
        self._session_out_d = None  # Unterordner der aktuellen Sitzung

        # Session Tracker für automatische Dateiauswahl
        self.session_files = []
        self.var_auto_files = tk.BooleanVar(value=True)

        # Paths - Output dynamisch im Home-Verzeichnis des Nutzers
        user_home = os.path.expanduser("~")
        self.var_out_dir = tk.StringVar(value=os.path.join(user_home, "captured_screens"))
        tess = self._find_tesseract_auto()
        self.var_tess_path = tk.StringVar()
        self.var_tess_path.set(tess if tess else r"C:\Program Files\Tesseract-OCR\tesseract.exe")

        # OCR Vars
        self.var_ocr_date = tk.BooleanVar(value=True)
        self.var_ocr_file = tk.BooleanVar(value=True)
        self.var_preproc  = tk.StringVar(value="scale2x")
        self.var_psm      = tk.StringVar(value="block")

        # Context Vars
        self.var_job   = tk.StringVar(value="EMC Simulation Engineer")
        self.var_comp  = tk.StringVar(value="Schaeffler AG")
        self.var_dept  = tk.StringVar(value="RD E-Mobility, Test & Validation")
        self.var_title = tk.StringVar(value="Project Updates")

        # Header
        header = tk.Frame(root, bg=SCHAEFFLER_GREEN)
        header.pack(fill="x")
        self.btn_lang = tk.Button(header, text="DE | EN", command=self.toggle_language,
                                   bg="#00662d", fg="white", relief="flat",
                                   font=("Arial", 8, "bold"))
        self.btn_lang.pack(side="right", padx=10, pady=10, anchor="ne")
        tk.Label(header, text=TOOL_NAME, bg=SCHAEFFLER_GREEN, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(pady=(10, 0))
        tk.Label(header, text=TOOL_VER, bg=SCHAEFFLER_GREEN, fg="#eeeeee",
                 font=("Segoe UI", 9)).pack(pady=(0, 10))

        # Tabs
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",     background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", padding=[12, 6], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", "white"), ("!selected", "#f0f0f0")],
                  foreground=[("selected", SCHAEFFLER_GREEN)])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

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
        self.notebook.add(self.tab_set, text="Settings")
        self.setup_settings_tab()

        self.update_texts()
        self.update_session_file_count()

        # Config laden
        self.load_config()

    # ── Config speichern/laden ─────────────────────────────────────────────
    CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".smartcapture_config.json")

    def save_config(self):
        data = {
            "job":      self.var_job.get(),
            "comp":     self.var_comp.get(),
            "dept":     self.var_dept.get(),
            "title":    self.var_title.get(),
            "out_dir":  self.var_out_dir.get(),
            "tess_path":self.var_tess_path.get(),
            "lang":     self.current_lang,
            "interval": self.interval_var.get(),
        }
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def load_config(self):
        if not os.path.exists(self.CONFIG_FILE):
            return
        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "job"   in data: self.var_job.set(data["job"])
            if "comp"  in data: self.var_comp.set(data["comp"])
            if "dept"  in data: self.var_dept.set(data["dept"])
            if "title" in data: self.var_title.set(data["title"])
            if "out_dir"   in data: self.var_out_dir.set(data["out_dir"])
            if "tess_path" in data: self.var_tess_path.set(data["tess_path"])
            if "lang"      in data:
                self.current_lang = data["lang"]
                self.update_texts()
            if "interval"  in data: self.interval_var.set(data["interval"])
        except Exception:
            pass

    # ── Hilfsfunktion: t() ────────────────────────────────────────────────
    def t(self, key):
        return TEXTS.get(key, {}).get(self.current_lang, key)

    def toggle_language(self):
        self.current_lang = "EN" if self.current_lang == "DE" else "DE"
        self.update_texts()
        self.save_config()

    def update_texts(self):
        self.notebook.tab(0, text=self.t("tab_rec"))
        self.notebook.tab(1, text=self.t("tab_ai"))
        self.notebook.tab(2, text=self.t("tab_ocr"))
        self.notebook.tab(3, text=self.t("tab_set"))

        self.lbl_sec_area.config(text=self.t("sec_area"))
        self.lbl_instr_area.config(text=self.t("instr_area"))
        self.btn_show.config(text=self.t("btn_frame"))
        self.btn_lock.config(text=self.t("btn_lock"))
        self.lbl_sec_proc.config(text=self.t("sec_proc"))
        self.lbl_interval.config(text=self.t("lbl_interval"))
        self.btn_start.config(text=self.t("btn_start"))
        self.btn_stop.config(text=self.t("btn_stop"))
        self.lbl_title_prev.config(text=self.t("lbl_prev"))
        self.lbl_title_curr.config(text=self.t("lbl_curr"))
        self.btn_folder1.config(text=self.t("btn_folder"))

        self.lbl_sec_ai_ctx.config(text=self.t("sec_ai_ctx"))
        self.lbl_job.config(text=self.t("lbl_job"))
        self.lbl_comp.config(text=self.t("lbl_comp"))
        self.lbl_dept.config(text=self.t("lbl_dept"))
        self.lbl_title.config(text=self.t("lbl_title"))
        self.btn_gen_prompt.config(text=self.t("btn_gen_prompt"))
        self.lbl_sec_ai_gen.config(text=self.t("sec_ai_gen"))
        self.btn_copy_prompt.config(text=self.t("btn_copy"))

        self.lbl_sec_ocr_opts.config(text=self.t("sec_ocr_opts"))
        self.lbl_lang.config(text=self.t("lbl_lang"))
        self.lbl_preproc.config(text=self.t("lbl_preproc"))
        self.lbl_psm.config(text=self.t("lbl_psm"))
        self.grp_content.config(text=self.t("grp_content"))
        self.chk_date.config(text=self.t("chk_date"))
        self.chk_file.config(text=self.t("chk_file"))
        self.lbl_sec_ocr_run.config(text=self.t("sec_ocr_run"))
        self.btn_ocr.config(text=self.t("btn_ocr"))
        self.lbl_chat_info.config(text=self.t("info_chat"))
        self.btn_chat.config(text=self.t("btn_chat"))

        self.lbl_sec_cap_mode.config(text=self.t("sec_cap_mode"))
        self.rb_screen.config(text=self.t("rb_screen"))
        self.rb_window.config(text=self.t("rb_window"))
        self.lbl_win_title_lbl.config(text=self.t("lbl_win_title"))
        self.lbl_sec_paths.config(text=self.t("sec_paths"))
        self.lbl_tess_path.config(text=self.t("lbl_tess_path"))
        self.lbl_out_dir.config(text=self.t("lbl_out_dir"))
        self.btn_browse_tess.config(text=self.t("btn_browse"))
        self.btn_browse_out.config(text=self.t("btn_browse"))
        self.lbl_sec_info.config(text=self.t("sec_info"))
        self.lbl_info_text.config(text=self.t("info_text"))

        # Combo boxes
        preproc_values = [TEXTS[f"dd_preproc_{k}"][self.current_lang] for k in PREPROC_KEYS]
        self.combo_preproc.config(values=preproc_values)
        psm_values = [TEXTS[f"dd_psm_{k}"][self.current_lang] for k in PSM_MAPPING.keys()]
        self.combo_psm.config(values=psm_values)

        # Restore combo selections by key
        cur_pre_key = self.var_preproc.get()
        if cur_pre_key in PREPROC_KEYS:
            self.combo_preproc.set(TEXTS[f"dd_preproc_{cur_pre_key}"][self.current_lang])
        cur_psm_key = self.var_psm.get()
        if cur_psm_key in PSM_MAPPING:
            self.combo_psm.set(TEXTS[f"dd_psm_{cur_psm_key}"][self.current_lang])

        self.update_session_file_count()
        self.update_ai_prompt_text()

    def update_session_file_count(self):
        n = len(self.session_files)
        txt = self.t("chk_auto_files").format(n=n)
        self.chk_auto_files.config(text=txt)

    def clear_session_files(self):
        self.session_files.clear()
        self._session_out_d = None
        self.update_session_file_count()

    def delete_session_files(self):
        files = [f for f in self.session_files if os.path.exists(f)]
        if not files:
            self.session_files.clear()
            self.update_session_file_count()
            return
        if messagebox.askyesno("Löschen?", f"{len(files)} Bilder wirklich löschen?"):
            for f in files:
                try:
                    os.remove(f)
                except Exception:
                    pass
            self.session_files.clear()
            self._session_out_d = None
            self.update_session_file_count()

    # ─────────────────────────────────────────────
    # SETUP TABS
    # ─────────────────────────────────────────────
    def setup_rec_tab(self):
        sf = ScrollableFrame(self.tab_rec, bg=BG_COLOR)
        sf.pack(fill="both", expand=True)
        content = sf.scrollable_content
        pad = tk.Frame(content, bg=BG_COLOR, padx=15, pady=10)
        pad.pack(fill="both", expand=True)

        self.lbl_sec_area = self.create_header(pad, "")
        self.lbl_instr_area = tk.Label(pad, text="", bg=BG_COLOR, justify="left")
        self.lbl_instr_area.pack(anchor="w", pady=(0, 5))

        btn_box = tk.Frame(pad, bg=BG_COLOR)
        btn_box.pack(fill="x", pady=2)
        self.btn_show = self.styled_btn(btn_box, "", self.open_selector, "#dddddd", "black")
        self.btn_show.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_lock = self.styled_btn(btn_box, "", self.lock_selector, SCHAEFFLER_GREEN, "white")
        self.btn_lock.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.lbl_info = tk.Label(pad, text="", bg=BG_COLOR, fg="gray",
                                  font=("Consolas", 9), justify="center")
        self.lbl_info.pack(pady=5)

        self.lbl_sec_proc = self.create_header(pad, "")

        interval_frame = tk.Frame(pad, bg=BG_COLOR)
        interval_frame.pack(fill="x")
        self.lbl_interval = tk.Label(interval_frame, text="", bg=BG_COLOR)
        self.lbl_interval.pack(side="left")
        self.lbl_interval_val = tk.Label(interval_frame, text="5.0s", bg=BG_COLOR,
                                          fg=SCHAEFFLER_GREEN, font=("Segoe UI", 10, "bold"))
        self.lbl_interval_val.pack(side="right")

        self.interval_var = tk.DoubleVar(value=5.0)
        tk.Scale(pad, from_=5.0, to=60.0, orient="horizontal",
                 variable=self.interval_var, resolution=1.0, bg=BG_COLOR,
                 highlightthickness=0,
                 command=self.update_interval_label).pack(fill="x", pady=2)

        rec_btns = tk.Frame(pad, bg=BG_COLOR)
        rec_btns.pack(fill="x", pady=5)
        self.btn_start = self.styled_btn(rec_btns, "", self.start_recording, SCHAEFFLER_GREEN, "white")
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_stop = self.styled_btn(rec_btns, "", self.stop_recording, "#888888", "white")
        self.btn_stop.config(state="disabled")
        self.btn_stop.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.lbl_status = tk.Label(pad, text="", bg=BG_COLOR,
                                    font=("Segoe UI", 10, "bold"), fg=SCHAEFFLER_DARK)
        self.lbl_status.pack(pady=2)

        self.preview_frame = tk.Frame(pad, bg=BG_COLOR)
        self.preview_frame.pack(fill="x", pady=2)

        self.frame_prev = tk.Frame(self.preview_frame, bg=BG_COLOR)
        self.lbl_title_prev = tk.Label(self.frame_prev, text="", bg=BG_COLOR,
                                        font=("Segoe UI", 8, "bold"), fg=SCHAEFFLER_DARK)
        self.lbl_title_prev.pack(anchor="w", pady=(0, 2))
        self.lbl_preview_prev = tk.Label(self.frame_prev, text="", bg="#f0f0f0")
        self.lbl_preview_prev.pack(fill="x")

        self.frame_curr = tk.Frame(self.preview_frame, bg=BG_COLOR)
        self.lbl_title_curr = tk.Label(self.frame_curr, text="", bg=BG_COLOR,
                                        font=("Segoe UI", 8, "bold"), fg=SCHAEFFLER_DARK)
        self.lbl_title_curr.pack(anchor="w", pady=(0, 2))
        self.lbl_preview_curr = tk.Label(self.frame_curr, text="", bg="#f0f0f0")
        self.lbl_preview_curr.pack(fill="x")

        self.frame_prev.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.frame_curr.pack(side="left", fill="both", expand=True, padx=(5, 0))

        self.btn_folder1 = tk.Button(pad, text="", command=self.open_folder,
                                      relief="flat", bg=BG_COLOR, fg=SCHAEFFLER_GREEN,
                                      cursor="hand2", font=("Segoe UI", 9, "underline"))
        self.btn_folder1.pack(pady=5)

    def adjust_preview_layout(self, w, h):
        self.frame_prev.pack_forget()
        self.frame_curr.pack_forget()
        if w < h * 1.2:
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

        self.btn_gen_prompt = tk.Button(pad, text="Update Prompt",
                                         command=self.update_ai_prompt_text,
                                         bg="#e0e0e0", relief="flat")
        self.btn_gen_prompt.pack(fill="x", pady=8)

        self.lbl_sec_ai_gen = self.create_header(pad, "")

        self.txt_prompt = tk.Text(pad, height=14, bg="#f5f5f5",
                                   font=("Segoe UI", 9), wrap="word", relief="flat")
        self.txt_prompt.pack(fill="x", pady=5)

        self.btn_copy_prompt = self.styled_btn(pad, "", self.copy_prompt, SCHAEFFLER_GREEN, "white")
        self.btn_copy_prompt.pack(fill="x", pady=10)

    def setup_ocr_tab(self):
        sf = ScrollableFrame(self.tab_ocr, bg=BG_COLOR)
        sf.pack(fill="both", expand=True)
        content = sf.scrollable_content
        pad = tk.Frame(content, bg=BG_COLOR, padx=20, pady=10)
        pad.pack(fill="both", expand=True)

        self.lbl_sec_ocr_opts = self.create_header(pad, "")

        self.lbl_lang = tk.Label(pad, text="", bg=BG_COLOR)
        self.lbl_lang.pack(anchor="w", pady=(5, 0))
        self.combo_ocr = ttk.Combobox(pad, values=list(OCR_LANGS.keys()), state="readonly")
        self.combo_ocr.current(0)
        self.combo_ocr.pack(fill="x", pady=5)

        self.lbl_preproc = tk.Label(pad, text="", bg=BG_COLOR)
        self.lbl_preproc.pack(anchor="w", pady=(5, 0))
        self.combo_preproc = ttk.Combobox(pad, values=list(PREPROC_KEYS), state="readonly")
        self.combo_preproc.current(1)
        self.combo_preproc.pack(fill="x", pady=5)

        self.lbl_psm = tk.Label(pad, text="", bg=BG_COLOR)
        self.lbl_psm.pack(anchor="w", pady=(5, 0))
        self.combo_psm = ttk.Combobox(pad, values=list(PSM_MAPPING.keys()), state="readonly")
        self.combo_psm.current(1)
        self.combo_psm.pack(fill="x", pady=5)

        self.grp_content = tk.LabelFrame(pad, text="", bg=BG_COLOR, padx=10, pady=5)
        self.grp_content.pack(fill="x", pady=10)
        self.chk_date = tk.Checkbutton(self.grp_content, text="", variable=self.var_ocr_date,
                                        bg=BG_COLOR, activebackground=BG_COLOR)
        self.chk_date.pack(anchor="w")
        self.chk_file = tk.Checkbutton(self.grp_content, text="", variable=self.var_ocr_file,
                                        bg=BG_COLOR, activebackground=BG_COLOR)
        self.chk_file.pack(anchor="w")

        self.lbl_sec_ocr_run = self.create_header(pad, "")

        fr_auto = tk.Frame(pad, bg=BG_COLOR)
        fr_auto.pack(fill="x", pady=(0, 10))
        self.chk_auto_files = tk.Checkbutton(fr_auto, text="", variable=self.var_auto_files,
                                              bg=BG_COLOR, activebackground=BG_COLOR,
                                              font=("Segoe UI", 9, "bold"), fg=SCHAEFFLER_DARK)
        self.chk_auto_files.pack(side="left")
        self.btn_clear_session = tk.Button(fr_auto, text=self.t("btn_clear_session"),
                                            command=self.clear_session_files,
                                            relief="flat", bg="#f0f0f0", cursor="hand2")
        self.btn_clear_session.pack(side="left", padx=10)
        self.btn_delete_session = tk.Button(fr_auto, text=self.t("btn_delete_session"),
                                             command=self.delete_session_files,
                                             relief="flat", bg="#f0f0f0", cursor="hand2")
        self.btn_delete_session.pack(side="left", padx=0)

        # Progress bar (initially hidden)
        self.fr_progress = tk.Frame(pad, bg=BG_COLOR)
        self.lbl_progress = tk.Label(self.fr_progress, text="", bg=BG_COLOR,
                                      font=("Segoe UI", 9), fg=SCHAEFFLER_DARK)
        self.lbl_progress.pack(fill="x")
        self.progress_bar = ttk.Progressbar(self.fr_progress, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", pady=2)

        self.btn_ocr = self.styled_btn(pad, "", self.start_ocr, SCHAEFFLER_DARK, "white")
        self.btn_ocr.pack(fill="x", pady=(5, 10))

        self.lbl_chat_info = tk.Label(pad, text="", bg=BG_COLOR, fg="#555555",
                                       justify="center", font=("Segoe UI", 9))
        self.lbl_chat_info.pack(fill="x", pady=(5, 2))
        self.btn_chat = self.styled_btn(pad, "", self.open_schaeffler_chat, EDGE_BLUE, "white")
        self.btn_chat.pack(fill="x", pady=(0, 10))

    def setup_settings_tab(self):
        sf = ScrollableFrame(self.tab_set, bg=BG_COLOR)
        sf.pack(fill="both", expand=True)
        content = sf.scrollable_content
        pad = tk.Frame(content, bg=BG_COLOR, padx=20, pady=10)
        pad.pack(fill="both", expand=True)

        self.lbl_sec_cap_mode = self.create_header(pad, "")
        self.rb_screen = tk.Radiobutton(pad, text="", variable=self.var_cap_mode,
                                         value="screen", bg=BG_COLOR, font=("Segoe UI", 9, "bold"))
        self.rb_screen.pack(anchor="w", pady=(5, 0))
        self.rb_window = tk.Radiobutton(pad, text="", variable=self.var_cap_mode,
                                         value="window", bg=BG_COLOR, font=("Segoe UI", 9, "bold"))
        self.rb_window.pack(anchor="w", pady=(2, 5))

        self.lbl_win_title_lbl = tk.Label(pad, text="", bg=BG_COLOR)
        self.lbl_win_title_lbl.pack(anchor="w")
        self.entry_win_title = tk.Entry(pad, textvariable=self.var_win_title, bg="#f0f0f0")
        self.entry_win_title.pack(fill="x", pady=2)

        self.lbl_sec_paths = self.create_header(pad, "")
        self.lbl_tess_path = tk.Label(pad, text="", bg=BG_COLOR,
                                       anchor="w", font=("Segoe UI", 9, "bold"))
        self.lbl_tess_path.pack(fill="x", pady=(10, 0))
        fr_tess = tk.Frame(pad, bg=BG_COLOR)
        fr_tess.pack(fill="x")
        tk.Entry(fr_tess, textvariable=self.var_tess_path, bg="#f0f0f0").pack(
            side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_browse_tess = tk.Button(fr_tess, text="", command=self.browse_tess,
                                          relief="flat", bg="#e0e0e0", cursor="hand2")
        self.btn_browse_tess.pack(side="right")

        self.lbl_out_dir = tk.Label(pad, text="", bg=BG_COLOR,
                                     anchor="w", font=("Segoe UI", 9, "bold"))
        self.lbl_out_dir.pack(fill="x", pady=(10, 0))
        fr_out = tk.Frame(pad, bg=BG_COLOR)
        fr_out.pack(fill="x")
        tk.Entry(fr_out, textvariable=self.var_out_dir, bg="#f0f0f0").pack(
            side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_browse_out = tk.Button(fr_out, text="", command=self.browse_out,
                                         relief="flat", bg="#e0e0e0", cursor="hand2")
        self.btn_browse_out.pack(side="right")

        self.lbl_sec_info = self.create_header(pad, "")
        self.lbl_info_text = tk.Label(pad, text="", bg=BG_COLOR, fg="#555555",
                                       justify="left", font=("Segoe UI", 9))
        self.lbl_info_text.pack(anchor="w", pady=5)
        link = tk.Label(pad, text="", fg=SCHAEFFLER_GREEN, bg=BG_COLOR,
                        cursor="hand2", font=("Segoe UI", 9, "underline"))
        link.pack(anchor="w")
        link.config(text=TEXTS["link_text"][self.current_lang])
        link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/tesseract-ocr/tesseract"))

    # ─────────────────────────────────────────────
    # CAPTURE LOGIC
    # ─────────────────────────────────────────────
    def _find_tesseract_auto(self):
        candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.join(os.getenv("LOCALAPPDATA", ""), r"Programs\Tesseract-OCR\tesseract.exe"),
        ]
        if which("tesseract"):
            return which("tesseract")
        for c in candidates:
            if os.path.exists(c):
                return c
        return None

    def open_selector(self):
        if self.selector_win and self.selector_win.winfo_exists():
            self.selector_win.lift()
            return
        self.selector_win = ResizableSelectionWindow(self.root)
        self.selector_win.protocol("WM_DELETE_WINDOW", self.on_selector_close)
        self.lbl_info.config(text=self.t("lbl_no_area"), fg="gray")

    def on_selector_close(self):
        if self.selector_win:
            try:
                self.selector_win.destroy()
            except:
                pass
            self.selector_win = None

    def lock_selector(self):
        if not self.selector_win or not self.selector_win.winfo_exists():
            messagebox.showwarning(self.t("err_title"), self.t("err_no_frame"))
            return

        x = self.selector_win.winfo_x() + 10
        y = self.selector_win.winfo_y() + 10
        w = self.selector_win.winfo_width() - 20
        h = self.selector_win.winfo_height() - 20

        # Monitor-Index ermitteln
        mon_idx = 1
        with mss.mss() as sct:
            for i, mon in enumerate(sct.monitors[1:], start=1):
                if (mon["left"] <= x < mon["left"] + mon["width"] and
                        mon["top"] <= y < mon["top"] + mon["height"]):
                    mon_idx = i
                    break
            if len(sct.monitors) > 1:
                base_mon = sct.monitors[mon_idx]
            else:
                base_mon = sct.monitors[1]

        self.monitor_area = {
            "top":    y,
            "left":   x,
            "width":  w,
            "height": h,
            "mon":    mon_idx,
        }

        # Relativen Bereich für Fenster-Capture ermitteln
        self.window_hwnd = None
        self.rel_area = None
        if self.var_cap_mode.get() == "window":
            try:
                hwnd = win32gui.WindowFromPoint((x + w // 2, y + h // 2))
                if hwnd:
                    self.window_hwnd = hwnd
                    wr_l, wr_t, wr_r, wr_b = win32gui.GetWindowRect(hwnd)
                    self.rel_area = {
                        "left":   x - wr_l,
                        "top":    y - wr_t,
                        "width":  w,
                        "height": h,
                    }
                    win_title = win32gui.GetWindowText(hwnd)
                    info_txt = self.t("lbl_area_ok_win").format(
                        w=w, h=h, mon=mon_idx, title=win_title[:40])
                else:
                    info_txt = self.t("lbl_area_ok").format(w=w, h=h, mon=mon_idx)
            except Exception:
                info_txt = self.t("lbl_area_ok").format(w=w, h=h, mon=mon_idx)
        else:
            info_txt = self.t("lbl_area_ok").format(w=w, h=h, mon=mon_idx)

        self.area_locked = True
        self.lbl_info.config(text=info_txt, fg=SCHAEFFLER_GREEN)

        try:
            self.selector_win.destroy()
        except:
            pass
        self.selector_win = None
        self.update_preview_once()

    def update_interval_label(self, val):
        self.lbl_interval_val.config(text=f"{float(val):.1f}s")

    def get_ai_prompt_string(self):
        tmpl = PROMPT_TEMPLATE_DE if self.current_lang == "DE" else PROMPT_TEMPLATE_EN
        return tmpl.format(
            job=self.var_job.get(),
            comp=self.var_comp.get(),
            dept=self.var_dept.get(),
            title=self.var_title.get(),
        )

    def update_ai_prompt_text(self):
        prompt = self.get_ai_prompt_string()
        self.txt_prompt.delete("1.0", tk.END)
        self.txt_prompt.insert("1.0", prompt)
        self.save_config()

    def copy_prompt(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.txt_prompt.get("1.0", tk.END))
        messagebox.showinfo("Info", self.t("msg_copied"))

    def open_schaeffler_chat(self):
        if not self.last_export_text:
            messagebox.showwarning(self.t("err_title"), self.t("err_no_export"))
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_export_text)
        messagebox.showinfo("Info", self.t("msg_chat_copied"))
        webbrowser.open("https://go.schaeffler.com/copilot", new=2)

    def browse_tess(self):
        f = filedialog.askopenfilename(filetypes=[("Executable", "*.exe")], title="Select tesseract.exe")
        if f: self.var_tess_path.set(f)

    def browse_out(self):
        d = filedialog.askdirectory(title="Select Output Folder")
        if d: self.var_out_dir.set(d)

    # ── Window-Title Auto-Detect ──────────────────────────────────────────
    def _detect_teams_window_title(self):
        """Sucht nach einem Microsoft Teams Fenster und gibt den Meeting-Titel zurück."""
        titles = []
        def enum_cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                t = win32gui.GetWindowText(hwnd)
                if t:
                    titles.append(t)
        try:
            win32gui.EnumWindows(enum_cb, None)
        except Exception:
            return None
        for t in titles:
            tl = t.lower()
            if "teams" in tl or "microsoft teams" in tl:
                # Bereinigen: " | Microsoft Teams" o.ä. entfernen
                clean_title = re.sub(r'\s*[\||\-]\s*Microsoft Teams.*$', '', t, flags=re.IGNORECASE).strip()
                if clean_title and clean_title.lower() not in ("microsoft teams", "teams"):
                    return clean_title
        return None

    def _auto_detect_window(self):
        """Versucht automatisch das Ziel-Fenster (Teams) zu finden."""
        title = self._detect_teams_window_title()
        if title:
            self.var_title.set(title)
            self.var_win_title.set(title)

    # ─────────────────────────────────────────────
    # CAPTURE SCREEN / WINDOW
    # ─────────────────────────────────────────────
    def capture_screen(self):
        mode = self.var_cap_mode.get()
        if mode == "window" and self.window_hwnd and self.rel_area:
            img = self.capture_specific_window(self.window_hwnd, self.rel_area)
            if img: return img
        # Fallback auf Screen-Capture
        return self._capture_via_mss()

    def _capture_via_mss(self):
        try:
            with mss.mss() as sct:
                area = {
                    "top":    self.monitor_area["top"],
                    "left":   self.monitor_area["left"],
                    "width":  self.monitor_area["width"],
                    "height": self.monitor_area["height"],
                }
                shot = sct.grab(area)
                img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
                return img
        except Exception as e:
            print("MSS Error:", e)
            return None

    def capture_specific_window(self, hwnd, rel_area):
        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width  = right  - left
            height = bottom - top
            if width < 1 or height < 1:
                return None

            hwnd_dc = win32gui.GetWindowDC(hwnd)
            mfc_dc  = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()

            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
            save_dc.SelectObject(save_bitmap)

            result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)
            if result == 0:
                result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 0)

            bmp_info = save_bitmap.GetInfo()
            bmp_str  = save_bitmap.GetBitmapBits(True)

            img = Image.frombuffer(
                "RGB",
                (bmp_info["bmWidth"], bmp_info["bmHeight"]),
                bmp_str, "raw", "BGRX", 0, 1
            )

            win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwnd_dc)

            # Relativen Bereich zuschneiden
            r_l = rel_area["left"]
            r_t = rel_area["top"]
            r_w = rel_area["width"]
            r_h = rel_area["height"]

            r_r = r_l + r_w
            r_b = r_t + r_h

            r_l = max(0, r_l)
            r_t = max(0, r_t)
            r_r = min(width, r_r)
            r_b = min(height, r_b)

            if r_r <= r_l or r_b <= r_t:
                return None

            return img.crop((r_l, r_t, r_r, r_b))
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
        base_d = self.var_out_dir.get()
        # Unterordner: YYYY-MM-DD_MeetingTitel
        _slug_now = self._title_slug(max_len=40)
        _date_now = datetime.datetime.now().strftime("%Y-%m-%d")
        if _slug_now:
            _sub = f"{_date_now}_{_slug_now}"
        else:
            _sub = _date_now
        out_d = os.path.join(base_d, _sub)
        if not os.path.exists(out_d): os.makedirs(out_d)
        self._session_out_d = out_d  # Merken für record_loop und open_folder

        self.is_recording = True
        self.recording_start_dt = datetime.datetime.now()   # Beginn der Aufzeichnung
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
                slug = self._title_slug(max_len=30)
                _out = getattr(self, "_session_out_d", self.var_out_dir.get())
                if slug:
                    fn = os.path.join(_out, f"screen_{slug}_{ts}.png")
                else:
                    fn = os.path.join(_out, f"screen_{ts}.png")
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
        out_d = getattr(self, "_session_out_d", None) or self.var_out_dir.get()
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
            # Meeting-Titel aus Bildnamen ableiten (Format: screen_TitelMitUnterstrichen_YYYY-MM-DD_HH-MM-SS.png)
            if fps:
                first_base = os.path.splitext(os.path.basename(fps[0]))[0]
                # Erwartet: screen_<Titel>_<YYYY-MM-DD>_<HH-MM-SS>
                m = re.match(r'^screen_(.+?)_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$', first_base)
                if m:
                    extracted_title = m.group(1).replace('_', ' ')
                    self.var_title.set(extracted_title)

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
        self.fr_progress.pack(fill="x", pady=(5, 5))
        self.btn_ocr.config(state="disabled")
        self.root.update_idletasks()
        self.root.update()

        now_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')

        prompt_txt = self.get_ai_prompt_string()
        full_text = f"{prompt_txt}\n\n"
        full_text += f"=== ORIGINAL OCR DATA START ===\n"
        _rec_start_info = self.recording_start_dt.strftime("%d.%m.%Y %H:%M:%S") if self.recording_start_dt else "unbekannt"
        full_text += f"Meeting-Titel: {self.var_title.get()} | Aufnahme-Beginn: {_rec_start_info}\n"
        full_text += f"Created: {now_str} | Settings: {lang_code}, {psm_arg}, {preproc_key}\n"

        self.progress_bar["maximum"] = len(files)
        self.progress_bar["value"] = 0
        for i, f in enumerate(files):
            self.lbl_progress.config(text=f"Texterkennung... Bild {i+1} / {len(files)}")
            self.progress_bar["value"] = i+1
            self.root.update()

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

        self.fr_progress.pack_forget()
        self.btn_ocr.config(state="normal")

        self.last_export_text = full_text
        # Dateiname: Titel + Aufnahme-Beginn + Export-Zeitstempel
        slug = self._title_slug(max_len=40)
        if self.recording_start_dt is not None:
            rec_start_str = self.recording_start_dt.strftime("%Y-%m-%d_%H-%M-%S")
        else:
            rec_start_str = now_str
        # Export-Ordner: Session-Unterordner falls vorhanden, sonst Basisordner
        _export_base = getattr(self, "_session_out_d", None) or self.var_out_dir.get()
        # Falls keine Session (manuelle Bildauswahl): Unterordner aus Titel+Datum anlegen
        if not getattr(self, "_session_out_d", None):
            _slug_ex = self._title_slug(max_len=40)
            _date_ex = now_str[:10]  # YYYY-MM-DD
            if _slug_ex:
                _export_base = os.path.join(self.var_out_dir.get(), f"{_date_ex}_{_slug_ex}")
            else:
                _export_base = os.path.join(self.var_out_dir.get(), _date_ex)
            os.makedirs(_export_base, exist_ok=True)
        if slug:
            fname = os.path.join(_export_base, f"Export_{slug}_Start-{rec_start_str}_{now_str}.txt")
        else:
            fname = os.path.join(_export_base, f"Export_{rec_start_str}_{now_str}.txt")
        with open(fname, "w", encoding="utf-8") as f: f.write(full_text)
        os.startfile(fname)


    # ── Hilfsfunktion: sicherer Dateiname-Teil aus Meeting-Titel ──────────────
    def _title_slug(self, max_len=40):
        """Gibt einen dateisicheren Kurztitel zurück (max max_len Zeichen)."""
        title = self.var_title.get().strip()
        if not title:
            return ""
        # Zeichen die in Dateinamen nicht erlaubt sind entfernen/ersetzen
        safe = re.sub(r'[\\/:*?"<>|]', '', title)
        safe = re.sub(r'\s+', '_', safe)
        safe = safe.strip('._')
        return safe[:max_len] if safe else ""

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
