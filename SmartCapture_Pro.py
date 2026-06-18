import sys
import subprocess
import os
import time
import datetime
import textwrap
import json # ADDED: For config saving

# --- NEU: TKINTER INSTALLATIONS-PRÜFUNG ---
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ImportError:
    print("\n" + "="*60)
    print("[FEHLER] Das Modul 'tkinter' fehlt in deiner Python-Installation.")
    print(" Dieses wird zwingend fuer die Benutzeroberflaeche benoetigt.")
    print("\nLÖSUNG (Ohne Admin-Rechte moeglich):")
    print("1. Gehe in den Windows-Einstellungen zu 'Installierte Apps'.")
    print("2. Suche nach deiner Python-Installation und klicke auf 'Aendern' (Modify).")
    print("3. Klicke im Setup-Fenster auf 'Modify'.")
    print("4. Setze das Haeckchen bei 'tcl/tk and IDLE' und klicke auf 'Next'.")
    print("="*60 + "\n")
    sys.exit(1)

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
            install_cmd = [temp_exe, "/S", f"/D={install_dir}"]
            subprocess.run(install_cmd, check=True)
            print("[INFO] DE: Tesseract (Uni Mannheim) wurde erfolgreich installiert!")
            print("[INFO] EN: Tesseract (Uni Mannheim) was installed successfully!")
        except Exception as e:
            print(f"[FEHLER / ERROR] Installation fehlgeschlagen / Installation failed: {e}")
        finally:
            if os.path.exists(temp_exe):
                try: os.remove(temp_exe)
                except: pass

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

ensure_tesseract_installed()

# --- KONFIGURATION ---
ACCENT_COLOR = "#0078D7"
DARK_COLOR = "#1E1E1E"
EDGE_BLUE = "#0078D7"
BG_COLOR = "#ffffff"
TRANSPARENT_KEY = "#ff00ff"

# VERSION INFO
TOOL_NAME = "SmartCapture Pro"
TOOL_VER = "v25.5 | Stand: 18.06.2026"

# --- AI CHAT SETTINGS ---
AI_CHAT_URL = "https://chatgpt.com/"
AI_BROWSER = "default"

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

{context_sentence}
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

{context_sentence}
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
    "tab_ai": {"DE": " 🤖 AI Context ", "EN": " 🤖 AI Context "},
    "tab_ocr": {"DE": " 📝 OCR & Export ", "EN": " 📝 OCR & Export "},
    "tab_set": {"DE": " ⚙️ Einstellungen ", "EN": " ⚙️ Settings "},
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
    "sec_ocr_opts": {"DE": "Export-Optionen", "EN": "Export Options"},
    "lbl_lang": {"DE": "Sprache:", "EN": "Language:"},
    "lbl_preproc": {"DE": "Bild-Optimierung:", "EN": "Image Optimization:"},
    "lbl_psm": {"DE": "Layout-Modus:", "EN": "Layout Mode:"},
    "grp_content": {"DE": "Inhalt des Exports", "EN": "Export Content"},
    "chk_date": {"DE": "Datum/Uhrzeit einfügen", "EN": "Include Date/Time"},
    "chk_file": {"DE": "Dateiname einfügen", "EN": "Include Filename"},
    "sec_ocr_run": {"DE": "Verarbeitung", "EN": "Processing"},
    "btn_ocr": {"DE": "Texterkennung starten & Exportieren", "EN": "Start OCR & Export"},
    "chk_auto_files": {"DE": "Bilder der aktuellen Sitzung verwenden ({n} Bilder)", "EN": "Use images from current session ({n} images)"},
    "btn_clear_session": {"DE": "🗑️ Leeren", "EN": "🗑️ Clear"},
    "info_chat": {"DE": "Text in Zwischenablage kopieren und Browser starten.\nDort einfach mit Strg+V einfügen.", "EN": "Copy generated text to clipboard and open browser.\nJust paste it there using Ctrl+V."},
    "tab_info": {"DE": "Info", "EN": "Info"},
    "lbl_about_title": {"DE": "Über dieses Tool", "EN": "About this Tool"},
    "lbl_about_text": {"DE": "Generiert mit Gemini 3.1 Pro.\nSmartCapture Pro ist ein Tool zur Automatisierung von OCR-Erfassung für Live-Transkripte.", "EN": "Generated with Gemini 3.1 Pro.\nSmartCapture Pro is a tool for automating OCR capture of live transcripts."},
    "lbl_trans_lang": {"DE": "⚠️ Abweichende Transkription? (z.B. gespr.: EN, Text: DE):", "EN": "⚠️ Transcript mismatch? (e.g. spoken: EN, transcript: DE):"},
    "lbl_frame_pull": {"DE": " RAHMEN ZIEHEN ", "EN": " DRAW FRAME "},
    "lbl_frame_confirm": {"DE": " BEREICH ÜBERNEHMEN ", "EN": " CONFIRM AREA "},
    "lbl_frame_close": {"DE": " ✕ SCHLIESSEN ", "EN": " ✕ CLOSE "},
    "btn_chat": {"DE": "🌐 AI Chat öffnen & Text kopieren", "EN": "🌐 Open AI Chat & Copy Text"},
    "err_no_export": {"DE": "Bitte starte zuerst die OCR-Verarbeitung und den Export!", "EN": "Please run OCR processing and export first!"},
    "msg_chat_copied": {"DE": "Text erfolgreich kopiert!\n\nBrowser wird geöffnet...\nFüge den Text einfach in das Chat-Feld ein (Strg+V).", "EN": "Text successfully copied!\n\nOpening browser...\nJust paste the text into the chat field (Ctrl+V)."},
    "sec_ai_ctx": {"DE": "Kontext & Rolle", "EN": "Context & Role"},
    "lbl_job": {"DE": "Beruf / Rolle:", "EN": "Job Title / Role:"},
    "lbl_comp": {"DE": "Firma:", "EN": "Company:"},
    "lbl_dept": {"DE": "Bereich / Abteilung:", "EN": "Department:"},
    "lbl_title": {"DE": "Meeting Titel:", "EN": "Meeting Title:"},
    "sec_ai_gen": {"DE": "Generierter Prompt (für KI-Chat)", "EN": "Generated Prompt (for AI Chat)"},
    "btn_gen_prompt": {"DE": "🔄 Prompt aktualisieren", "EN": "🔄 Update Prompt"},
    "btn_copy": {"DE": "📋 Prompt kopieren", "EN": "📋 Copy Prompt"},
    "msg_copied": {"DE": "Prompt kopiert!", "EN": "Prompt copied!"},
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
    "dd_preproc_none": {"DE": "Keine (Original)", "EN": "None (Original)"},
    "dd_preproc_scale2x": {"DE": "2x Skalierung (Scharf)", "EN": "2x Scaling (Sharp)"},
    "dd_preproc_gray_contrast": {"DE": "Graustufen + Kontrast", "EN": "Grayscale + Contrast"},
    "dd_psm_auto": {"DE": "Auto (Standard)", "EN": "Auto (Default)"},
    "dd_psm_block": {"DE": "Block (Chat/Text)", "EN": "Block (Chat/Text)"},
    "dd_psm_line": {"DE": "Einzelne Zeile", "EN": "Single Line"},
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
    HANDLE = 12
    MIN_W = 120
    MIN_H = 80

    def __init__(self, master, label_text=" RAHMEN ZIEHEN ", confirm_text=" BEREICH ÜBERNEHMEN ", close_text=" ✕ SCHLIESSEN ", on_confirm=None):
        super().__init__(master)
        self.on_confirm = on_confirm
        self.title("Selector")
        self.geometry("700x450+100+100")
        self.attributes("-topmost", True)
        self.config(bg=ACCENT_COLOR)
        self.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        self.overrideredirect(True)

        self._drag_mode = None
        self._drag_start = None
        self._start_geom = None

        self.outer = tk.Frame(self, bg=ACCENT_COLOR, highlightthickness=0, bd=0)
        self.outer.pack(fill="both", expand=True)

        self.inner_frame = tk.Frame(self.outer, bg=TRANSPARENT_KEY, highlightthickness=0, bd=0)
        self.inner_frame.place(x=self.HANDLE, y=self.HANDLE, relwidth=1.0, relheight=1.0,
                               width=-2*self.HANDLE, height=-2*self.HANDLE)

        lbl = tk.Label(self.outer, text=label_text, bg=ACCENT_COLOR, fg="white", font=("Arial", 9, "bold"), padx=6, pady=2, cursor="fleur")
        lbl.place(x=6, y=6)
        self.caption_label = lbl

        self.confirm_label = tk.Label(self.outer, text=confirm_text, bg=ACCENT_COLOR, fg="white", font=("Arial", 9, "bold"), padx=6, pady=2, cursor="hand2")
        self.confirm_label.place(relx=0.5, y=6, anchor="n")

        self.close_label = tk.Label(self.outer, text=close_text, bg=ACCENT_COLOR, fg="white", font=("Arial", 9, "bold"), padx=6, pady=2, cursor="hand2")
        self.close_label.place(relx=1.0, x=-6, y=6, anchor="ne")

        self._make_handles()
        self._bind_move(self.caption_label)
        self._bind_move(self.inner_frame)
        self.confirm_label.bind("<Button-1>", lambda e: self.on_confirm() if callable(self.on_confirm) else None)
        self.close_label.bind("<Button-1>", lambda e: self.destroy())
        self.bind("<Escape>", lambda e: self.destroy())

    def _make_handles(self):
        t = self.HANDLE
        specs = {
            "n":  dict(relx=0, rely=0, relwidth=1, height=t, anchor="nw", cursor="sb_v_double_arrow"),
            "s":  dict(relx=0, rely=1, relwidth=1, height=t, y=-t, anchor="nw", cursor="sb_v_double_arrow"),
            "w":  dict(relx=0, rely=0, width=t, relheight=1, anchor="nw", cursor="sb_h_double_arrow"),
            "e":  dict(relx=1, rely=0, width=t, relheight=1, x=-t, anchor="nw", cursor="sb_h_double_arrow"),
            "nw": dict(x=0, y=0, width=t, height=t, anchor="nw", cursor="size_nw_se"),
            "ne": dict(relx=1, x=-t, y=0, width=t, height=t, anchor="nw", cursor="size_ne_sw"),
            "sw": dict(x=0, rely=1, y=-t, width=t, height=t, anchor="nw", cursor="size_ne_sw"),
            "se": dict(relx=1, rely=1, x=-t, y=-t, width=t, height=t, anchor="nw", cursor="size_nw_se"),
        }
        self.handles = {}
        for mode, place_kwargs in specs.items():
            cursor = place_kwargs.pop("cursor")
            handle = tk.Frame(self.outer, bg=ACCENT_COLOR, highlightthickness=0, bd=0, cursor=cursor)
            handle.place(**place_kwargs)
            handle.bind("<ButtonPress-1>", lambda e, m=mode: self._start_resize(e, m))
            handle.bind("<B1-Motion>", self._perform_resize)
            handle.bind("<ButtonRelease-1>", self._stop_action)
            self.handles[mode] = handle

    def _bind_move(self, widget):
        widget.bind("<ButtonPress-1>", self._start_move)
        widget.bind("<B1-Motion>", self._perform_move)
        widget.bind("<ButtonRelease-1>", self._stop_action)

    def _parse_geometry(self):
        self.update_idletasks()
        return self.winfo_x(), self.winfo_y(), self.winfo_width(), self.winfo_height()

    def get_capture_box(self):
        self.update_idletasks()
        x = self.winfo_rootx() + self.HANDLE
        y = self.winfo_rooty() + self.HANDLE
        w = max(1, self.winfo_width() - 2*self.HANDLE)
        h = max(1, self.winfo_height() - 2*self.HANDLE)
        return x, y, w, h

    def _start_move(self, event):
        self._drag_mode = "move"
        self._drag_start = (event.x_root, event.y_root)
        self._start_geom = self._parse_geometry()

    def _perform_move(self, event):
        if self._drag_mode != "move" or not self._start_geom: return
        sx, sy = self._drag_start
        gx, gy, gw, gh = self._start_geom
        nx = gx + (event.x_root - sx)
        ny = gy + (event.y_root - sy)
        self.geometry(f"{gw}x{gh}+{int(nx)}+{int(ny)}")

    def _start_resize(self, event, mode):
        self._drag_mode = mode
        self._drag_start = (event.x_root, event.y_root)
        self._start_geom = self._parse_geometry()

    def _perform_resize(self, event):
        if not self._drag_mode or self._drag_mode == "move" or not self._start_geom: return
        sx, sy = self._drag_start
        dx = event.x_root - sx
        dy = event.y_root - sy
        x, y, w, h = self._start_geom
        left = x; top = y; right = x + w; bottom = y + h
        mode = self._drag_mode
        if "w" in mode: left = min(left + dx, right - self.MIN_W)
        if "e" in mode: right = max(right + dx, left + self.MIN_W)
        if "n" in mode: top = min(top + dy, bottom - self.MIN_H)
        if "s" in mode: bottom = max(bottom + dy, top + self.MIN_H)
        new_w = max(self.MIN_W, right - left)
        new_h = max(self.MIN_H, bottom - top)
        self.geometry(f"{int(new_w)}x{int(new_h)}+{int(left)}+{int(top)}")

    def _stop_action(self, _event=None):
        self._drag_mode = None
        self._drag_start = None
        self._start_geom = None


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

        # Session Tracker
        self.session_files = []
        self.var_auto_files = tk.BooleanVar(value=True)

        # Aufnahme-Startzeitpunkt (wird in record_loop gesetzt)
        self.recording_start_ts = None

        # Paths
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
        self.var_ai_url = tk.StringVar(value=AI_CHAT_URL)
        self.var_ai_browser = tk.StringVar(value=AI_BROWSER)

        # --- HEADER ---
        header = tk.Frame(root, bg=ACCENT_COLOR)
        header.pack(fill="x")

        self.btn_lang = tk.Button(header, text="🇩🇪 DE / 🇺🇸 EN", command=self.toggle_language,
                                  bg="#1E1E1E", fg="white", relief="flat", font=("Arial", 8, "bold"))
        self.btn_lang.pack(side="right", padx=10, pady=10, anchor="ne")

        tk.Label(header, text=TOOL_NAME, bg=ACCENT_COLOR, fg="white", font=("Segoe UI", 16, "bold")).pack(pady=(10, 0))
        tk.Label(header, text=TOOL_VER, bg=ACCENT_COLOR, fg="#eeeeee", font=("Segoe UI", 9)).pack(pady=(0, 10))

        # --- TABS ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=BG_COLOR, borderwidth=0)
        style.configure('TNotebook.Tab', padding=[12, 6], font=('Segoe UI', 10, 'bold'))
        style.map("TNotebook.Tab",
                  background=[("selected", "white"), ("!selected", "#f0f0f0")],
                  foreground=[("selected", ACCENT_COLOR)])

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
        self.notebook.add(self.tab_set, text="Einstellungen")
        self.setup_settings_tab()

        self.tab_info = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_info, text="Info")
        self.setup_info_tab()

        self.load_config()
        self.update_texts()
        self.update_session_file_count()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # --- CONFIG ---
    def load_config(self):
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "ai_url" in data: self.var_ai_url.set(data["ai_url"])
                if "ai_browser" in data: self.var_ai_browser.set(data["ai_browser"])
                if "job" in data: self.var_job.set(data["job"])
                if "comp" in data: self.var_comp.set(data["comp"])
                if "dept" in data: self.var_dept.set(data["dept"])
                if "title" in data: self.var_title.set(data["title"])
                if "trans_lang" in data: self.var_trans_lang.set(data["trans_lang"])
                if "tess_path" in data: self.var_tess_path.set(data["tess_path"])
                if "lang" in data: self.current_lang = data["lang"]
        except Exception as e:
            print("Could not load config:", e)

    def save_config(self):
        try:
            data = {
                "ai_url": self.var_ai_url.get(),
                "ai_browser": self.var_ai_browser.get(),
                "job": self.var_job.get(),
                "comp": self.var_comp.get(),
                "dept": self.var_dept.get(),
                "title": self.var_title.get(),
                "trans_lang": getattr(self, "var_trans_lang", tk.StringVar()).get(),
                "tess_path": self.var_tess_path.get(),
                "lang": self.current_lang
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("Could not save config:", e)

    def on_closing(self):
        self.save_config()
        self.root.destroy()

    def t(self, key):
        return TEXTS.get(key, {}).get(self.current_lang, key)

    def toggle_language(self):
        self.current_lang = "EN" if self.current_lang == "DE" else "DE"
        self.update_texts()
        self.save_config()

    def update_texts(self):
        self.notebook.tab(self.tab_rec, text=self.t("tab_rec"))
        self.notebook.tab(self.tab_ai, text=self.t("tab_ai"))
        self.notebook.tab(self.tab_ocr, text=self.t("tab_ocr"))
        self.notebook.tab(self.tab_set, text=self.t("tab_set"))
        self.notebook.tab(self.tab_info, text=self.t("tab_info"))
        self.lbl_sec_area.config(text=self.t("sec_area"))
        self.lbl_instr_area.config(text=self.t("instr_area"))
        self.btn_show.config(text=self.t("btn_frame"))
        self.btn_lock.config(text=self.t("btn_lock"))
        self.lbl_sec_proc.config(text=self.t("sec_proc"))
        self.lbl_interval.config(text=self.t("lbl_interval"))
        self.btn_start.config(text=self.t("btn_start"))
        self.btn_stop.config(text=self.t("btn_stop"))
        self.lbl_prev_label.config(text=self.t("lbl_prev"))
        self.lbl_curr_label.config(text=self.t("lbl_curr"))
        self.btn_folder.config(text=self.t("btn_folder"))
        self.lbl_sec_ocr_opts.config(text=self.t("sec_ocr_opts"))
        self.lbl_lang_ocr.config(text=self.t("lbl_lang"))
        self.lbl_preproc.config(text=self.t("lbl_preproc"))
        self.lbl_psm.config(text=self.t("lbl_psm"))
        self.lbl_grp_content.config(text=self.t("grp_content"))
        self.chk_date.config(text=self.t("chk_date"))
        self.chk_file.config(text=self.t("chk_file"))
        self.lbl_sec_ocr_run.config(text=self.t("sec_ocr_run"))
        self.btn_ocr.config(text=self.t("btn_ocr"))
        self.btn_chat.config(text=self.t("btn_chat"))
        self.lbl_sec_ai_ctx.config(text=self.t("sec_ai_ctx"))
        self.lbl_job.config(text=self.t("lbl_job"))
        self.lbl_comp.config(text=self.t("lbl_comp"))
        self.lbl_dept.config(text=self.t("lbl_dept"))
        self.lbl_title_ai.config(text=self.t("lbl_title"))
        self.lbl_sec_ai_gen.config(text=self.t("sec_ai_gen"))
        self.btn_gen_prompt.config(text=self.t("btn_gen_prompt"))
        self.btn_copy_prompt.config(text=self.t("btn_copy"))
        self.lbl_sec_cap_mode.config(text=self.t("sec_cap_mode"))
        self.rb_screen.config(text=self.t("rb_screen"))
        self.rb_window.config(text=self.t("rb_window"))
        self.lbl_win_title_label.config(text=self.t("lbl_win_title"))
        self.lbl_sec_paths.config(text=self.t("sec_paths"))
        self.lbl_tess_path.config(text=self.t("lbl_tess_path"))
        self.lbl_out_dir.config(text=self.t("lbl_out_dir"))
        self.btn_browse_tess.config(text=self.t("btn_browse"))
        self.btn_browse_out.config(text=self.t("btn_browse"))
        self.lbl_sec_info_set.config(text=self.t("sec_info"))
        self.lbl_info_tess.config(text=self.t("info_text"))
        self.lbl_tess_link.config(text=self.t("link_text"))
        self.lbl_about_title.config(text=self.t("lbl_about_title"))
        self.lbl_about_text.config(text=self.t("lbl_about_text"))
        self.lbl_trans_lang.config(text=self.t("lbl_trans_lang"))
        self.update_session_file_count()
        if self.selector_win and self.selector_win.winfo_exists():
            self.selector_win.caption_label.config(text=self.t("lbl_frame_pull"))
            self.selector_win.confirm_label.config(text=self.t("lbl_frame_confirm"))
            self.selector_win.close_label.config(text=self.t("lbl_frame_close"))
        preproc_values = [self.t(f"dd_preproc_{k}") for k in PREPROC_KEYS]
        self.combo_preproc.config(values=preproc_values)
        psm_values = [self.t(f"dd_psm_{k}") for k in PSM_MAPPING.keys()]
        self.combo_psm.config(values=psm_values)
        curr_pre = self.var_preproc.get()
        curr_psm = self.var_psm.get()
        self.combo_preproc.set(self.t(f"dd_preproc_{curr_pre}"))
        self.combo_psm.set(self.t(f"dd_psm_{curr_psm}"))

    def update_session_file_count(self):
        n = len(self.session_files)
        if hasattr(self, 'chk_auto_files_widget'):
            self.chk_auto_files_widget.config(text=self.t("chk_auto_files").format(n=n))

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
        tk.Scale(pad, from_=1.0, to=60.0, orient="horizontal", variable=self.interval_var,
                 resolution=1.0, bg=BG_COLOR, highlightthickness=0,
                 command=self.update_interval_label).pack(fill="x", pady=2)

        rec_btns = tk.Frame(pad, bg=BG_COLOR)
        rec_btns.pack(fill="x", pady=5)
        self.btn_start = self.styled_btn(rec_btns, "", self.start_recording, ACCENT_COLOR, "white")
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_stop = self.styled_btn(rec_btns, "", self.stop_recording, "#888888", "white")
        self.btn_stop.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.btn_stop.config(state="disabled")

        self.lbl_status = tk.Label(pad, text="Bereit.", bg=BG_COLOR, fg="gray", font=("Segoe UI", 9))
        self.lbl_status.pack(pady=3)

        preview_outer = tk.Frame(pad, bg=BG_COLOR)
        preview_outer.pack(fill="x", pady=5)

        prev_col = tk.Frame(preview_outer, bg=BG_COLOR)
        prev_col.pack(side="left", fill="both", expand=True)
        self.lbl_prev_label = tk.Label(prev_col, text="", bg=BG_COLOR, fg="gray", font=("Segoe UI", 8))
        self.lbl_prev_label.pack()
        self.lbl_preview_prev = tk.Label(prev_col, bg="#f0f0f0", relief="flat", bd=1)
        self.lbl_preview_prev.pack(fill="both", expand=True)

        curr_col = tk.Frame(preview_outer, bg=BG_COLOR)
        curr_col.pack(side="left", fill="both", expand=True, padx=(5, 0))
        self.lbl_curr_label = tk.Label(curr_col, text="", bg=BG_COLOR, fg="gray", font=("Segoe UI", 8))
        self.lbl_curr_label.pack()
        self.lbl_preview_curr = tk.Label(curr_col, bg="#f0f0f0", relief="flat", bd=1)
        self.lbl_preview_curr.pack(fill="both", expand=True)

        self.btn_folder = self.styled_btn(pad, "", self.open_folder, "#f0f0f0", "black")
        self.btn_folder.pack(fill="x", pady=(5, 0))

    def setup_ocr_tab(self):
        sf = ScrollableFrame(self.tab_ocr, bg=BG_COLOR)
        sf.pack(fill="both", expand=True)
        content = sf.scrollable_content
        pad = tk.Frame(content, bg=BG_COLOR, padx=15, pady=10)
        pad.pack(fill="both", expand=True)

        self.lbl_sec_ocr_opts = self.create_header(pad, "")

        row_lang = tk.Frame(pad, bg=BG_COLOR)
        row_lang.pack(fill="x", pady=2)
        self.lbl_lang_ocr = tk.Label(row_lang, text="", bg=BG_COLOR, width=20, anchor="w")
        self.lbl_lang_ocr.pack(side="left")
        self.combo_ocr = ttk.Combobox(row_lang, values=list(OCR_LANGS.keys()), state="readonly", width=30)
        self.combo_ocr.set(list(OCR_LANGS.keys())[0])
        self.combo_ocr.pack(side="left", padx=5)

        row_pre = tk.Frame(pad, bg=BG_COLOR)
        row_pre.pack(fill="x", pady=2)
        self.lbl_preproc = tk.Label(row_pre, text="", bg=BG_COLOR, width=20, anchor="w")
        self.lbl_preproc.pack(side="left")
        self.combo_preproc = ttk.Combobox(row_pre, state="readonly", width=30)
        self.combo_preproc.pack(side="left", padx=5)

        row_psm = tk.Frame(pad, bg=BG_COLOR)
        row_psm.pack(fill="x", pady=2)
        self.lbl_psm = tk.Label(row_psm, text="", bg=BG_COLOR, width=20, anchor="w")
        self.lbl_psm.pack(side="left")
        self.combo_psm = ttk.Combobox(row_psm, state="readonly", width=30)
        self.combo_psm.pack(side="left", padx=5)

        self.lbl_grp_content = self.create_header(pad, "")
        self.chk_date = tk.Checkbutton(pad, text="", variable=self.var_ocr_date, bg=BG_COLOR)
        self.chk_date.pack(anchor="w")
        self.chk_file = tk.Checkbutton(pad, text="", variable=self.var_ocr_file, bg=BG_COLOR)
        self.chk_file.pack(anchor="w")

        session_frame = tk.Frame(pad, bg=BG_COLOR)
        session_frame.pack(fill="x", pady=5)
        self.chk_auto_files_widget = tk.Checkbutton(session_frame, text="", variable=self.var_auto_files, bg=BG_COLOR)
        self.chk_auto_files_widget.pack(side="left")
        self.btn_clear_session = tk.Button(session_frame, text=self.t("btn_clear_session"),
                                           command=self.clear_session, bg="#f0f0f0", relief="flat",
                                           font=("Segoe UI", 9))
        self.btn_clear_session.pack(side="left", padx=5)

        self.lbl_sec_ocr_run = self.create_header(pad, "")
        self.btn_ocr = self.styled_btn(pad, "", self.start_ocr, ACCENT_COLOR, "white")
        self.btn_ocr.pack(fill="x", pady=3)

        self.fr_progress = tk.Frame(pad, bg=BG_COLOR)
        self.lbl_progress = tk.Label(self.fr_progress, text="", bg=BG_COLOR, fg="gray", font=("Segoe UI", 9))
        self.lbl_progress.pack(anchor="w")
        self.progress_bar = ttk.Progressbar(self.fr_progress, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x")

        tk.Frame(pad, bg="#eeeeee", height=1).pack(fill="x", pady=8)
        self.lbl_trans_lang = tk.Label(pad, text="", bg=BG_COLOR, wraplength=600, justify="left")
        self.lbl_trans_lang.pack(anchor="w")
        trans_langs = ["", "DE→EN", "EN→DE", "JA→DE", "JA→EN"]
        self.combo_trans_lang = ttk.Combobox(pad, textvariable=self.var_trans_lang, values=trans_langs, width=12)
        self.combo_trans_lang.pack(anchor="w", pady=3)

        tk.Frame(pad, bg="#eeeeee", height=1).pack(fill="x", pady=8)
        lbl_info_chat = tk.Label(pad, text=self.t("info_chat"), bg=BG_COLOR, fg="gray",
                                 font=("Segoe UI", 9), justify="left")
        lbl_info_chat.pack(anchor="w", pady=(0, 5))
        self.btn_chat = self.styled_btn(pad, "", self.open_ai_chat, "#1E1E1E", "white")
        self.btn_chat.pack(fill="x", pady=3)

    def setup_ai_tab(self):
        sf = ScrollableFrame(self.tab_ai, bg=BG_COLOR)
        sf.pack(fill="both", expand=True)
        content = sf.scrollable_content
        pad = tk.Frame(content, bg=BG_COLOR, padx=15, pady=10)
        pad.pack(fill="both", expand=True)

        self.lbl_sec_ai_ctx = self.create_header(pad, "")

        fields = [
            ("lbl_job", self.var_job),
            ("lbl_comp", self.var_comp),
            ("lbl_dept", self.var_dept),
            ("lbl_title", self.var_title),
        ]
        self.lbl_job = self.lbl_comp = self.lbl_dept = self.lbl_title_ai = None
        lbl_refs = {}
        for key, var in fields:
            row = tk.Frame(pad, bg=BG_COLOR)
            row.pack(fill="x", pady=2)
            lbl = tk.Label(row, text="", bg=BG_COLOR, width=22, anchor="w")
            lbl.pack(side="left")
            entry = tk.Entry(row, textvariable=var, width=35, relief="solid", bd=1)
            entry.pack(side="left", padx=5)
            lbl_refs[key] = lbl

        self.lbl_job = lbl_refs["lbl_job"]
        self.lbl_comp = lbl_refs["lbl_comp"]
        self.lbl_dept = lbl_refs["lbl_dept"]
        self.lbl_title_ai = lbl_refs["lbl_title"]

        self.lbl_sec_ai_gen = self.create_header(pad, "")

        btn_row = tk.Frame(pad, bg=BG_COLOR)
        btn_row.pack(fill="x", pady=3)
        self.btn_gen_prompt = self.styled_btn(btn_row, "", self.update_prompt_preview, "#f0f0f0", "black")
        self.btn_gen_prompt.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_copy_prompt = self.styled_btn(btn_row, "", self.copy_prompt, ACCENT_COLOR, "white")
        self.btn_copy_prompt.pack(side="left", fill="x", expand=True)

        self.txt_prompt = tk.Text(pad, height=18, wrap="word", font=("Consolas", 9),
                                  bg="#f9f9f9", relief="solid", bd=1)
        self.txt_prompt.pack(fill="both", expand=True, pady=5)
        self.update_prompt_preview()

    def setup_settings_tab(self):
        sf = ScrollableFrame(self.tab_set, bg=BG_COLOR)
        sf.pack(fill="both", expand=True)
        content = sf.scrollable_content
        pad = tk.Frame(content, bg=BG_COLOR, padx=15, pady=10)
        pad.pack(fill="both", expand=True)

        self.lbl_sec_cap_mode = self.create_header(pad, "")
        self.rb_screen = tk.Radiobutton(pad, text="", variable=self.var_cap_mode, value="screen", bg=BG_COLOR, command=self.on_cap_mode_change)
        self.rb_screen.pack(anchor="w")
        self.rb_window = tk.Radiobutton(pad, text="", variable=self.var_cap_mode, value="window", bg=BG_COLOR, command=self.on_cap_mode_change)
        self.rb_window.pack(anchor="w")

        win_row = tk.Frame(pad, bg=BG_COLOR)
        win_row.pack(fill="x", pady=2)
        self.lbl_win_title_label = tk.Label(win_row, text="", bg=BG_COLOR, anchor="w")
        self.lbl_win_title_label.pack(side="left")
        self.lbl_win_title_val = tk.Label(win_row, textvariable=self.var_win_title, bg=BG_COLOR,
                                          fg=ACCENT_COLOR, font=("Segoe UI", 9, "bold"))
        self.lbl_win_title_val.pack(side="left", padx=5)

        self.lbl_sec_paths = self.create_header(pad, "")

        row_tess = tk.Frame(pad, bg=BG_COLOR)
        row_tess.pack(fill="x", pady=2)
        self.lbl_tess_path = tk.Label(row_tess, text="", bg=BG_COLOR, width=18, anchor="w")
        self.lbl_tess_path.pack(side="left")
        tk.Entry(row_tess, textvariable=self.var_tess_path, width=35, relief="solid", bd=1).pack(side="left", padx=2)
        self.btn_browse_tess = tk.Button(row_tess, text="", bg="#f0f0f0", relief="flat",
                                         command=lambda: self.browse_path(self.var_tess_path, "exe"))
        self.btn_browse_tess.pack(side="left")

        row_out = tk.Frame(pad, bg=BG_COLOR)
        row_out.pack(fill="x", pady=2)
        self.lbl_out_dir = tk.Label(row_out, text="", bg=BG_COLOR, width=18, anchor="w")
        self.lbl_out_dir.pack(side="left")
        tk.Entry(row_out, textvariable=self.var_out_dir, width=35, relief="solid", bd=1).pack(side="left", padx=2)
        self.btn_browse_out = tk.Button(row_out, text="", bg="#f0f0f0", relief="flat",
                                        command=lambda: self.browse_path(self.var_out_dir, "dir"))
        self.btn_browse_out.pack(side="left")

        self.lbl_sec_info_set = self.create_header(pad, "")
        self.lbl_info_tess = tk.Label(pad, text="", bg=BG_COLOR, fg="gray", font=("Segoe UI", 9))
        self.lbl_info_tess.pack(anchor="w")
        self.lbl_tess_link = tk.Label(pad, text="", bg=BG_COLOR, fg=ACCENT_COLOR,
                                      cursor="hand2", font=("Segoe UI", 9, "underline"))
        self.lbl_tess_link.pack(anchor="w")
        self.lbl_tess_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/UB-Mannheim/tesseract/wiki"))

        ai_frame = self.create_header(pad, "AI Chat")
        row_url = tk.Frame(pad, bg=BG_COLOR)
        row_url.pack(fill="x", pady=2)
        tk.Label(row_url, text="URL:", bg=BG_COLOR, width=18, anchor="w").pack(side="left")
        tk.Entry(row_url, textvariable=self.var_ai_url, width=35, relief="solid", bd=1).pack(side="left", padx=2)

        row_browser = tk.Frame(pad, bg=BG_COLOR)
        row_browser.pack(fill="x", pady=2)
        tk.Label(row_browser, text="Browser:", bg=BG_COLOR, width=18, anchor="w").pack(side="left")
        ttk.Combobox(row_browser, textvariable=self.var_ai_browser,
                     values=["default", "msedge", "chrome", "firefox"],
                     state="readonly", width=15).pack(side="left", padx=2)

    def setup_info_tab(self):
        sf = ScrollableFrame(self.tab_info, bg=BG_COLOR)
        sf.pack(fill="both", expand=True)
        content = sf.scrollable_content
        pad = tk.Frame(content, bg=BG_COLOR, padx=15, pady=10)
        pad.pack(fill="both", expand=True)

        self.lbl_about_title = tk.Label(pad, text="", bg=BG_COLOR, font=("Segoe UI", 14, "bold"), fg=ACCENT_COLOR)
        self.lbl_about_title.pack(anchor="w", pady=(0, 5))
        self.lbl_about_text = tk.Label(pad, text="", bg=BG_COLOR, justify="left", wraplength=600)
        self.lbl_about_text.pack(anchor="w")
        tk.Label(pad, text="Version: v25.5 | Stand: 18.06.2026", font=("Segoe UI", 10), bg=BG_COLOR, fg=DARK_COLOR).pack(anchor="w", pady=(0, 15))
        tk.Label(pad, text="Änderungslog v25.5:", font=("Segoe UI", 10, "bold"), bg=BG_COLOR).pack(anchor="w")
        changes = [
            "• Screenshots: Dateiname enthält jetzt den Meeting-Titel (aus AI Context Tab)",
            "  Beispiel: screen_Projekt_Update_2026-06-18_09-30-00.png",
            "• Export-TXT: Dateiname enthält Titel + Aufnahme-Beginn (erster Screenshot)",
            "  Beispiel: Export_Projekt_Update_Beginn-2026-06-18_09-30_2026-06-18_09-45.txt",
            "• Export-TXT: Kopfzeile zeigt Meeting-Titel und Aufnahme-Beginn im Dokument",
            "• Aufnahme-Startzeitstempel wird automatisch beim ersten Screenshot gesetzt",
        ]
        for c in changes:
            tk.Label(pad, text=c, bg=BG_COLOR, fg="#444444", justify="left",
                     wraplength=620, font=("Segoe UI", 9)).pack(anchor="w")

    # --- HELPERS ---
    def create_header(self, parent, text):
        f = tk.Frame(parent, bg=BG_COLOR)
        f.pack(fill="x", pady=(5, 2))
        tk.Frame(f, bg=ACCENT_COLOR, height=2).pack(fill="x")
        lbl = tk.Label(f, text=text, bg=BG_COLOR, fg=ACCENT_COLOR,
                       font=("Segoe UI", 10, "bold"), anchor="w")
        lbl.pack(anchor="w")
        return lbl

    def styled_btn(self, parent, text, cmd, bg, fg):
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                         relief="flat", font=("Segoe UI", 10, "bold"),
                         padx=10, pady=8, activebackground=bg, cursor="hand2")

    def update_interval_label(self, val):
        self.lbl_interval_val.config(text=f"{float(val):.1f}s")

    def browse_path(self, var, mode):
        if mode == "exe":
            p = filedialog.askopenfilename(filetypes=[("Executables", "*.exe")])
        else:
            p = filedialog.askdirectory()
        if p:
            var.set(p)

    def find_tesseract_auto(self):
        candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.join(os.getenv('LOCALAPPDATA', ''), r"Programs\Tesseract-OCR\tesseract.exe"),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        found = which("tesseract")
        return found if found else ""

    def clear_session(self):
        self.session_files = []
        self.recording_start_ts = None
        self.update_session_file_count()

    def on_cap_mode_change(self):
        pass

    # --- SELECTOR ---
    def open_selector(self):
        if self.selector_win and self.selector_win.winfo_exists():
            self.selector_win.lift()
            return
        self.selector_win = ResizableSelectionWindow(
            self.root,
            label_text=self.t("lbl_frame_pull"),
            confirm_text=self.t("lbl_frame_confirm"),
            close_text=self.t("lbl_frame_close"),
            on_confirm=self.lock_selector
        )
        if self.last_frame_geo:
            self.selector_win.geometry(self.last_frame_geo)

    def lock_selector(self):
        if not self.selector_win or not self.selector_win.winfo_exists():
            messagebox.showwarning(self.t("err_title"), self.t("err_no_frame"))
            return
        x, y, w, h = self.selector_win.get_capture_box()
        self.last_frame_geo = self.selector_win.geometry()

        with mss.mss() as sct:
            monitors = sct.monitors[1:]
            mon_idx = 1
            for i, m in enumerate(monitors, 1):
                if (m['left'] <= x < m['left'] + m['width'] and
                        m['top'] <= y < m['top'] + m['height']):
                    mon_idx = i
                    break
            mon = monitors[mon_idx - 1]
            self.monitor_area = {
                'top': y, 'left': x, 'width': w, 'height': h,
                'mon': mon_idx
            }
            self.rel_area = {
                'left_rel': x - mon['left'],
                'top_rel': y - mon['top'],
                'width': w, 'height': h
            }

        mode = self.var_cap_mode.get()
        if mode == "window":
            hwnd = win32gui.WindowFromPoint((x + w // 2, y + h // 2))
            if hwnd:
                self.window_hwnd = hwnd
                title = win32gui.GetWindowText(hwnd)
                self.var_win_title.set(title or "-- Unbekannt --")
                info = self.t("lbl_area_ok_win").format(w=w, h=h, mon=self.monitor_area['mon'], title=title[:40])
            else:
                info = self.t("lbl_area_ok").format(w=w, h=h, mon=self.monitor_area['mon'])
        else:
            info = self.t("lbl_area_ok").format(w=w, h=h, mon=self.monitor_area['mon'])

        self.lbl_info.config(text=info, fg="green")
        self.area_locked = True
        if self.selector_win and self.selector_win.winfo_exists():
            self.selector_win.destroy()

    # --- CAPTURE ---
    def capture_screen(self):
        try:
            mode = self.var_cap_mode.get()
            if mode == "window" and self.window_hwnd:
                return self.capture_window_dc()
            else:
                return self.capture_mss()
        except Exception as e:
            print(f"Capture error: {e}")
            return None

    def capture_mss(self):
        with mss.mss() as sct:
            area = {
                'top': self.monitor_area['top'],
                'left': self.monitor_area['left'],
                'width': self.monitor_area['width'],
                'height': self.monitor_area['height']
            }
            shot = sct.grab(area)
            return Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")

    def capture_window_dc(self):
        hwnd = self.window_hwnd
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        w = right - left
        h = bottom - top
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(mfc_dc, w, h)
        save_dc.SelectObject(bmp)
        result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)
        bmp_info = bmp.GetInfo()
        bmp_str = bmp.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmp_info['bmWidth'], bmp_info['bmHeight']),
                                bmp_str, 'raw', 'BGRX', 0, 1)
        win32gui.DeleteObject(bmp.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)
        if not result:
            return self.capture_mss()

        if self.rel_area:
            rl = self.rel_area['left_rel']
            rt = self.rel_area['top_rel']
            rw = self.rel_area['width']
            rh = self.rel_area['height']
            try:
                img = img.crop((rl, rt, rl + rw, rt + rh))
            except Exception:
                pass
        return img

    def show_preview(self, lbl, img, max_w=300, max_h=180):
        if img is None:
            lbl.config(image="", text="[Preview]", fg="gray", font=("Segoe UI", 9))
            lbl.image = None
            return
        try:
            img_copy = img.copy()
            img_copy.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img_copy)
            lbl.config(image=tk_img, text="")
            lbl.image = tk_img
        except Exception as e:
            print(f"Preview error: {e}")

    # --- RECORDING ---
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
        self.recording_start_ts = None  # wird beim ersten gespeicherten Bild gesetzt
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

                # Aufnahme-Startzeitpunkt beim ersten Bild festhalten
                if self.recording_start_ts is None:
                    self.recording_start_ts = ts

                # Kurztitel aus Meeting-Titel ableiten (max. 30 Zeichen, dateisicher)
                raw_title = self.var_title.get().strip()
                safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in raw_title)
                safe_title = safe_title.replace(' ', '_')[:30].strip('_')
                if safe_title:
                    fn = os.path.join(self.var_out_dir.get(), f"screen_{safe_title}_{ts}.png")
                else:
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

    # --- OCR ---
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
        self.fr_progress.pack(fill="x", pady=(5, 5))
        self.btn_ocr.config(state="disabled")
        self.root.update_idletasks()
        self.root.update()

        now_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')

        # Meeting-Titel dateisicher machen (max. 40 Zeichen)
        raw_title = self.var_title.get().strip()
        safe_title_export = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in raw_title)
        safe_title_export = safe_title_export.replace(' ', '_')[:40].strip('_')

        # Aufnahme-Startzeitpunkt: aus session recording_start_ts oder erstem Dateinamen
        recording_start_str = ""
        if hasattr(self, 'recording_start_ts') and self.recording_start_ts:
            recording_start_str = self.recording_start_ts
        elif files:
            try:
                mtime_first = os.path.getmtime(files[0])
                recording_start_str = datetime.datetime.fromtimestamp(mtime_first).strftime('%Y-%m-%d_%H-%M-%S')
            except Exception:
                recording_start_str = now_str

        prompt_txt = self.get_ai_prompt_string()
        full_text = f"{prompt_txt}\n\n"
        full_text += f"=== ORIGINAL OCR DATA START ===\n"
        # Erweiterte Kopfzeile: Meeting-Titel + Aufnahme-Beginn
        if raw_title:
            full_text += f"Meeting: {raw_title}\n"
        if recording_start_str:
            try:
                dt_start = datetime.datetime.strptime(recording_start_str[:19], '%Y-%m-%d_%H-%M-%S')
                full_text += f"Aufnahme-Beginn: {dt_start.strftime('%d.%m.%Y %H:%M:%S')}\n"
            except Exception:
                full_text += f"Aufnahme-Beginn: {recording_start_str}\n"
        full_text += f"Export erstellt: {now_str} | Settings: {lang_code}, {psm_arg}, {preproc_key}\n"

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
            except Exception as e:
                print(e)

        self.fr_progress.pack_forget()
        self.btn_ocr.config(state="normal")

        self.last_export_text = full_text

        # Dateiname: Export_<MeetingTitel>_Beginn-<start>_<now>.txt
        parts = ["Export"]
        if safe_title_export:
            parts.append(safe_title_export)
        if recording_start_str:
            parts.append(f"Beginn-{recording_start_str[:16]}")
        parts.append(now_str)
        fname = os.path.join(self.var_out_dir.get(), "_".join(parts) + ".txt")
        with open(fname, "w", encoding="utf-8") as f:
            f.write(full_text)
        os.startfile(fname)

    # --- AI PROMPT ---
    def get_ai_prompt_string(self):
        lang = self.current_lang
        template = PROMPT_TEMPLATE_DE if lang == "DE" else PROMPT_TEMPLATE_EN
        job = self.var_job.get()
        comp = self.var_comp.get()
        dept = self.var_dept.get()
        title = self.var_title.get()
        trans_lang = self.var_trans_lang.get().strip()

        if lang == "DE":
            ctx = f"Ich bin {job} bei {comp} im Bereich {dept}." if any([job, comp, dept]) else ""
            trans_note = f"Hinweis: Das Meeting wurde auf einer anderen Sprache als der Transkription geführt ({trans_lang}). Bitte berücksichtige dies bei der Rekonstruktion." if trans_lang else ""
        else:
            ctx = f"I am a {job} at {comp} in the {dept} department." if any([job, comp, dept]) else ""
            trans_note = f"Note: The meeting was conducted in a different language than the transcription ({trans_lang}). Please account for this during reconstruction." if trans_lang else ""

        return template.format(context_sentence=ctx, title=title, trans_note=trans_note)

    def update_prompt_preview(self):
        prompt = self.get_ai_prompt_string()
        self.txt_prompt.config(state="normal")
        self.txt_prompt.delete("1.0", "end")
        self.txt_prompt.insert("1.0", prompt)
        self.txt_prompt.config(state="disabled")

    def copy_prompt(self):
        prompt = self.get_ai_prompt_string()
        self.root.clipboard_clear()
        self.root.clipboard_append(prompt)
        messagebox.showinfo("", self.t("msg_copied"))

    def open_ai_chat(self):
        if not self.last_export_text:
            messagebox.showwarning(self.t("err_title"), self.t("err_no_export"))
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_export_text)
        messagebox.showinfo("", self.t("msg_chat_copied"))
        url = self.var_ai_url.get() or AI_CHAT_URL
        browser_key = self.var_ai_browser.get()
        try:
            if browser_key == "default":
                webbrowser.open(url)
            else:
                webbrowser.get(browser_key).open(url)
        except Exception:
            webbrowser.open(url)


# --- MAIN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartCaptureApp(root)
    root.mainloop()
