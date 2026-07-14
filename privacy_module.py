import os
import json
import glob
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

PRIVACY_CONFIG_FILE = os.path.join(
    os.getenv("LOCALAPPDATA", os.path.expanduser("~")),
    "SmartCapturePro",
    "privacy_settings.json"
)

os.makedirs(os.path.dirname(PRIVACY_CONFIG_FILE), exist_ok=True)

DEFAULT_PRIVACY_SETTINGS = {
    "auto_delete_enabled": True,
    "auto_delete_days": 7,
    "transcript_delete_days": 30,
    "show_consent_on_start": True,
    "last_deletion_check": "",
}

CONSENT_TEXT_DE = """DATENSCHUTZ-HINWEIS -- Bitte lesen und bestaetigen

Dieses Meeting wird mit SmartCapture Pro (OCR-Screenshot-Tool) transkribiert.

Was wird erfasst:
  * Bildschirmausschnitte der Live-Untertitel / des Transkript-Bereichs
  * Daraus per OCR extrahierter Text (kein Audio, keine Biometrie)

Speicherdauer:
  * Screenshots: {screenshot_days} Tage
  * Transkript-Textdatei: {transcript_days} Tage
  Danach automatische Loeschung vom Geraet des Aufzeichnenden.

Rechtsgrundlage:
  Berechtigtes Interesse gem. Art. 6 Abs. 1 lit. f DSGVO zur effizienten
  Besprechungsdokumentation.
  Verwendungszweck: ausschliesslich interne Protokollierung / Aufgaben-Extraktion.

Opt-out:
  Wer NICHT transkribiert werden moechte, kann dies jetzt im Chat oder
  per Direktnachricht mitteilen.

Rueckfragen: Bitte direkt an den Meeting-Organisator wenden.

Mit Verbleib im Meeting gilt die Information als zur Kenntnis genommen.
"""

CONSENT_TEXT_EN = """PRIVACY NOTICE -- Please read

This meeting is being transcribed using SmartCapture Pro (OCR screenshot tool).

What is captured:
  * Screen captures of the live subtitles / transcript area
  * Text extracted via OCR (no audio recording, no biometric data)

Retention period:
  * Screenshots: {screenshot_days} days
  * Transcript text file: {transcript_days} days
  Automatic deletion from the recorder's device after this period.

Legal basis:
  Legitimate interest pursuant to Art. 6(1)(f) GDPR for efficient
  meeting documentation.
  Purpose: internal note-taking / action-item extraction only.

Opt-out:
  Anyone who does NOT wish to be transcribed can state this now in the
  meeting chat or via direct message.

Questions: Please contact the meeting organiser directly.

By remaining in the meeting you acknowledge this notice.
"""


class PrivacyManager:
    def __init__(self, app):
        self.app = app
        self.settings = self._load_settings()
        self._privacy_parent = None
        self._privacy_container = None
        self._consent_cancelled = False

    def _load_settings(self):
        if os.path.exists(PRIVACY_CONFIG_FILE):
            try:
                with open(PRIVACY_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                merged = dict(DEFAULT_PRIVACY_SETTINGS)
                merged.update(data)
                return merged
            except Exception:
                pass
        return dict(DEFAULT_PRIVACY_SETTINGS)

    def _save_settings(self):
        with open(PRIVACY_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)

    def refresh_privacy_ui(self):
        if self._privacy_container is not None and self._privacy_container.winfo_exists():
            self._privacy_container.destroy()
            self._privacy_container = None

        if self._privacy_parent is not None and self._privacy_parent.winfo_exists():
            self.setup_privacy_tab(self._privacy_parent)

    def setup_privacy_tab(self, parent_frame):
        self._privacy_parent = parent_frame
        BGCOLOR = "#ffffff"
        GREEN = "#00893d"

        self._privacy_container = tk.Frame(parent_frame, bg=BGCOLOR)
        self._privacy_container.pack(fill="x", pady=(0, 0))
        parent = self._privacy_container

        sep = tk.Frame(parent, height=1, bg="#cccccc")
        sep.pack(fill="x", pady=(16, 4))

        lang = getattr(self.app, "current_lang", "DE")

        if lang == "DE":
            header_text = "Datenschutz & DSGVO"
            lbl_auto = "Automatische Loeschung aktivieren"
            lbl_days_sc = "Screenshots loeschen nach (Tage):"
            lbl_days_tr = "Transkript-Dateien loeschen nach (Tage):"
            lbl_consent = "Einwilligungs-Erinnerung beim Aufnahme-Start anzeigen"
            btn_now = "Jetzt Loeschung pruefen & ausfuehren"
            btn_copy_de = "Datenschutz-Text DE kopieren (Chat)"
            btn_copy_en = "Privacy Notice EN kopieren (Chat)"
            info = ("Alle Dateien im Ausgabeordner werden nach Ablauf\n"
                    "automatisch geloescht (Pruefung beim App-Start).")
            hint_sc = "(empf. 7)"
            hint_tr = "(empf. 30)"
        else:
            header_text = "Privacy & GDPR"
            lbl_auto = "Enable automatic deletion"
            lbl_days_sc = "Delete screenshots after (days):"
            lbl_days_tr = "Delete transcript files after (days):"
            lbl_consent = "Show consent reminder on recording start"
            btn_now = "Run deletion check now"
            btn_copy_de = "Copy privacy notice (DE) for chat"
            btn_copy_en = "Copy privacy notice (EN) for chat"
            info = ("All files in the output folder will be deleted\n"
                    "automatically after the configured period.")
            hint_sc = "(rec. 7)"
            hint_tr = "(rec. 30)"

        tk.Label(parent, text=header_text, bg=BGCOLOR,
                 font=("Segoe UI", 10, "bold"), fg=GREEN).pack(anchor="w", pady=(0, 6))

        self._var_auto_del = tk.BooleanVar(value=self.settings["auto_delete_enabled"])
        self._var_days_sc = tk.IntVar(value=self.settings["auto_delete_days"])
        self._var_days_tr = tk.IntVar(value=self.settings["transcript_delete_days"])
        self._var_consent = tk.BooleanVar(value=self.settings["show_consent_on_start"])

        tk.Checkbutton(parent, text=lbl_auto, variable=self._var_auto_del,
                       bg=BGCOLOR, activebackground=BGCOLOR,
                       font=("Segoe UI", 9, "bold"),
                       command=self._on_settings_change).pack(anchor="w")

        fr1 = tk.Frame(parent, bg=BGCOLOR)
        fr1.pack(fill="x", pady=2)
        tk.Label(fr1, text=lbl_days_sc, bg=BGCOLOR, font=("Segoe UI", 9)).pack(side="left")
        tk.Spinbox(fr1, from_=1, to=365, width=5, textvariable=self._var_days_sc,
                   command=self._on_settings_change).pack(side="left", padx=6)
        tk.Label(fr1, text=hint_sc, fg="#888888", bg=BGCOLOR,
                 font=("Segoe UI", 8)).pack(side="left")

        fr2 = tk.Frame(parent, bg=BGCOLOR)
        fr2.pack(fill="x", pady=2)
        tk.Label(fr2, text=lbl_days_tr, bg=BGCOLOR, font=("Segoe UI", 9)).pack(side="left")
        tk.Spinbox(fr2, from_=1, to=365, width=5, textvariable=self._var_days_tr,
                   command=self._on_settings_change).pack(side="left", padx=6)
        tk.Label(fr2, text=hint_tr, fg="#888888", bg=BGCOLOR,
                 font=("Segoe UI", 8)).pack(side="left")

        tk.Checkbutton(parent, text=lbl_consent, variable=self._var_consent,
                       bg=BGCOLOR, activebackground=BGCOLOR,
                       font=("Segoe UI", 9),
                       command=self._on_settings_change).pack(anchor="w", pady=(6, 2))

        tk.Label(parent, text=info, bg=BGCOLOR, fg="#555555",
                 font=("Segoe UI", 8), justify="left").pack(anchor="w", pady=4)

        tk.Button(parent, text=btn_now, command=self.run_deletion_now,
                  relief="flat", bg="#f0f0f0",
                  font=("Segoe UI", 9), cursor="hand2").pack(fill="x", pady=(4, 2))

        tk.Button(parent, text=btn_copy_de, command=lambda: self._copy_consent("DE"),
                  relief="flat", bg=GREEN, fg="white",
                  font=("Segoe UI", 9, "bold"), cursor="hand2").pack(fill="x", pady=2)

        tk.Button(parent, text=btn_copy_en, command=lambda: self._copy_consent("EN"),
                  relief="flat", bg="#0078D7", fg="white",
                  font=("Segoe UI", 9, "bold"), cursor="hand2").pack(fill="x", pady=2)

    def _on_settings_change(self):
        self.settings["auto_delete_enabled"] = self._var_auto_del.get()
        self.settings["auto_delete_days"] = self._var_days_sc.get()
        self.settings["transcript_delete_days"] = self._var_days_tr.get()
        self.settings["show_consent_on_start"] = self._var_consent.get()
        self._save_settings()

    def show_consent_reminder(self):
        if not self.settings.get("show_consent_on_start", True):
            return True

        lang = getattr(self.app, "current_lang", "DE")
        sc_days = self.settings["auto_delete_days"]
        tr_days = self.settings["transcript_delete_days"]

        win = tk.Toplevel(self.app.root)
        win.title("Datenschutz-Erinnerung / Privacy Reminder")
        win.geometry("700x700")
        win.minsize(640, 620)
        win.grab_set()
        win.resizable(True, True)

        BGCOLOR = "#ffffff"
        GREEN = "#00893d"

        content_frame = tk.Frame(win, bg=BGCOLOR)
        content_frame.pack(fill="both", expand=True)

        nb = ttk.Notebook(content_frame)
        nb.pack(fill="both", expand=True, padx=10, pady=(8, 4))

        def make_tab(label, text_content):
            frame = tk.Frame(nb, bg=BGCOLOR)
            nb.add(frame, text=label)
            txt = tk.Text(frame, wrap="word", font=("Consolas", 9),
                          bg="#f8f8f8", relief="flat", padx=8, pady=6)
            txt.insert("1.0", text_content)
            txt.config(state="disabled")
            sb = ttk.Scrollbar(frame, orient="vertical", command=txt.yview)
            txt.config(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y")
            txt.pack(fill="both", expand=True)

        de_text = CONSENT_TEXT_DE.format(screenshot_days=sc_days, transcript_days=tr_days)
        en_text = CONSENT_TEXT_EN.format(screenshot_days=sc_days, transcript_days=tr_days)

        make_tab("Deutsch (DE)", de_text)
        make_tab("English (EN)", en_text)

        nb.select(1 if lang == "EN" else 0)

        def copy_de():
            win.clipboard_clear()
            win.clipboard_append(de_text)
            win.update()
            messagebox.showinfo("Kopiert / Copied",
                                "Deutsch-Text kopiert.\nIm Teams-Chat einfuegen (Strg+V).",
                                parent=win)

        def copy_en():
            win.clipboard_clear()
            win.clipboard_append(en_text)
            win.update()
            messagebox.showinfo("Kopiert / Copied",
                                "English text copied.\nPaste into Teams chat (Ctrl+V).",
                                parent=win)

        def proceed():
            self._consent_cancelled = False
            win.destroy()

        def cancel():
            self._consent_cancelled = True
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", cancel)

        if lang == "DE":
            lbl_info = "Text im Meeting-Chat posten, dann Aufnahme starten:"
            btn_de = "DE-Text kopieren (Chat)"
            btn_en = "EN-Text kopieren (Chat)"
            btn_ok = "Verstanden - Aufnahme starten"
            btn_cancel = "Abbrechen"
        else:
            lbl_info = "Post this text in the meeting chat, then start recording:"
            btn_de = "Copy DE text (Chat)"
            btn_en = "Copy EN text (Chat)"
            btn_ok = "Understood - Start Recording"
            btn_cancel = "Cancel"

        bottom = tk.Frame(win, bg=BGCOLOR)
        bottom.pack(fill="x", side="bottom", padx=10, pady=(0, 8))

        tk.Label(bottom, text=lbl_info, bg=BGCOLOR,
                 font=("Segoe UI", 9, "italic"), fg="#555555").pack(fill="x", pady=(0, 4))

        btn_frame = tk.Frame(bottom, bg=BGCOLOR)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text=btn_de, command=copy_de,
                  relief="flat", bg=GREEN, fg="white",
                  font=("Segoe UI", 9, "bold"), cursor="hand2"
                  ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        tk.Button(btn_frame, text=btn_en, command=copy_en,
                  relief="flat", bg="#0078D7", fg="white",
                  font=("Segoe UI", 9, "bold"), cursor="hand2"
                  ).pack(side="left", fill="x", expand=True, padx=(4, 0))

        tk.Button(bottom, text=btn_ok, command=proceed,
                  relief="flat", bg="#2c3e50", fg="white",
                  font=("Segoe UI", 10, "bold"), cursor="hand2"
                  ).pack(fill="x", pady=(8, 2))

        tk.Button(bottom, text=btn_cancel, command=cancel,
                  relief="flat", bg="#f0f0f0",
                  font=("Segoe UI", 9), cursor="hand2"
                  ).pack(fill="x")

        self.app.root.wait_window(win)
        return not self._consent_cancelled

    def _copy_consent(self, lang="DE"):
        sc = self.settings["auto_delete_days"]
        tr = self.settings["transcript_delete_days"]

        if lang == "DE":
            text = CONSENT_TEXT_DE.format(screenshot_days=sc, transcript_days=tr)
            msg = "DE-Datenschutztext kopiert.\nIm Teams-Chat einfuegen (Strg+V)."
        else:
            text = CONSENT_TEXT_EN.format(screenshot_days=sc, transcript_days=tr)
            msg = "English privacy notice copied.\nPaste into Teams chat (Ctrl+V)."

        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(text)
        self.app.root.update()
        messagebox.showinfo("Kopiert / Copied", msg)

    def check_scheduled_deletions(self):
        if not self.settings.get("auto_delete_enabled", True):
            return

        today = datetime.date.today().isoformat()
        if self.settings.get("last_deletion_check", "") == today:
            return

        self._run_deletions()
        self.settings["last_deletion_check"] = today
        self._save_settings()

    def run_deletion_now(self):
        deleted_count, freed_mb = self._run_deletions()
        lang = getattr(self.app, "current_lang", "DE")

        if lang == "DE":
            title = "Loeschung abgeschlossen"
            msg = f"Loeschung abgeschlossen.\n\nGeloeschte Dateien: {deleted_count}\nFreigegeben: {freed_mb:.2f} MB"
        else:
            title = "Deletion complete"
            msg = f"Deletion complete.\n\nFiles deleted: {deleted_count}\nSpace freed: {freed_mb:.2f} MB"

        messagebox.showinfo(title, msg)

    def _run_deletions(self):
        sc_days = self.settings.get("auto_delete_days", 7)
        tr_days = self.settings.get("transcript_delete_days", 30)
        out_dir_var = getattr(self.app, "var_out_dir", None)

        if out_dir_var is None:
            return 0, 0.0

        out_dir = out_dir_var.get()
        if not out_dir or not os.path.isdir(out_dir):
            return 0, 0.0

        now = datetime.datetime.now()
        deleted = 0
        freed = 0.0

        for pattern in ("*.png", "*.jpg", "*.jpeg"):
            for fpath in glob.glob(os.path.join(out_dir, pattern)):
                try:
                    age = (now - datetime.datetime.fromtimestamp(os.path.getmtime(fpath))).days
                    if age >= sc_days:
                        freed += os.path.getsize(fpath) / (1024 * 1024)
                        os.remove(fpath)
                        deleted += 1
                except Exception:
                    pass

        for pattern in ("*.txt", "*.md"):
            for fpath in glob.glob(os.path.join(out_dir, pattern)):
                try:
                    age = (now - datetime.datetime.fromtimestamp(os.path.getmtime(fpath))).days
                    if age >= tr_days:
                        freed += os.path.getsize(fpath) / (1024 * 1024)
                        os.remove(fpath)
                        deleted += 1
                except Exception:
                    pass

        return deleted, freed
