"""
Netch Package Creator
An Aerotion Production

Creates .ntchpkg files for the Netch 2 package manager.
Just fill in the fields and click Create Package!
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, json, zipfile, shutil, re

# ─────────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────────

BG        = "#1e1e2e"
PANEL     = "#2a2a3e"
ACCENT    = "#7c6af7"
ACCENT2   = "#5a4fcf"
TEXT      = "#e0e0f0"
SUBTEXT   = "#9090b0"
INPUT_BG  = "#12121e"
INPUT_FG  = "#e0e0f0"
SUCCESS   = "#3fb950"
WARNING   = "#e3b341"
ERROR     = "#f85149"
BORDER    = "#3a3a5a"
FONT      = "Segoe UI"

# ─────────────────────────────────────────────
#  APP
# ─────────────────────────────────────────────

class NetchPackageCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Netch Package Creator — An Aerotion Production")
        self.root.geometry("800x700")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.extra_files = []  # list of extra file paths to bundle
        self.builtin_entries = []  # list of (name_var, code_var) pairs

        self._build_ui()

    # ─────────────────────────────────────────
    #  UI
    # ─────────────────────────────────────────

    def _build_ui(self):
        # header
        header = tk.Frame(self.root, bg=ACCENT, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📦  Netch Package Creator",
                 bg=ACCENT, fg="white",
                 font=(FONT, 16, "bold")).pack(side="left", padx=18, pady=12)
        tk.Label(header, text="An Aerotion Production",
                 bg=ACCENT, fg="#d0c8ff",
                 font=(FONT, 9)).pack(side="right", padx=18)

        # scrollable canvas
        canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=BG)
        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        f = self.scroll_frame
        pad = {"padx": 24, "pady": 6}

        # ── SECTION: Package Info ──
        self._section(f, "📋  Package Info")

        self.pkg_name    = self._field(f, "Package Name *",
            "e.g. customwindowtitle  (lowercase, no spaces)", **pad)
        self.pkg_version = self._field(f, "Version *",
            "e.g. 1.0.0", **pad)
        self.pkg_desc    = self._field(f, "Description *",
            "What does this package do?", **pad)
        self.pkg_author  = self._field(f, "Author",
            "Your name or username", **pad)

        # ── SECTION: Usage Example ──
        self._section(f, "📖  How to Use  (shown after install)")

        tk.Label(f, text="Usage lines (one per line):",
                 bg=BG, fg=SUBTEXT, font=(FONT, 9)).pack(anchor="w", **pad)
        self.usage_box = tk.Text(f, height=4, bg=INPUT_BG, fg=INPUT_FG,
                                  insertbackground=INPUT_FG,
                                  font=("Consolas", 10),
                                  relief="flat", bd=0,
                                  highlightbackground=BORDER,
                                  highlightthickness=1)
        self.usage_box.pack(fill="x", **pad)
        self.usage_box.insert("1.0", "importpkg yourpackage\n# add your usage here")

        # ── SECTION: Netch Builtins ──
        self._section(f, "⚙️  Netch Commands  (functions your package adds)")

        tk.Label(f,
            text="Each command becomes callable in .ntch scripts as  commandname(args)",
            bg=BG, fg=SUBTEXT, font=(FONT, 9)).pack(anchor="w", **pad)

        self.builtins_frame = tk.Frame(f, bg=BG)
        self.builtins_frame.pack(fill="x", **pad)
        self._add_builtin_row()  # start with one

        tk.Button(f, text="+ Add Command",
                  bg=PANEL, fg=ACCENT,
                  font=(FONT, 9, "bold"),
                  relief="flat", bd=0,
                  padx=12, pady=6,
                  cursor="hand2",
                  activebackground=BORDER,
                  command=self._add_builtin_row).pack(anchor="w", **pad)

        # ── SECTION: Extra Files ──
        self._section(f, "📁  Extra Files  (images, sounds, data — optional)")

        tk.Label(f, text="Bundle extra files into your package:",
                 bg=BG, fg=SUBTEXT, font=(FONT, 9)).pack(anchor="w", **pad)

        files_row = tk.Frame(f, bg=BG)
        files_row.pack(fill="x", **pad)
        tk.Button(files_row, text="+ Add Files",
                  bg=PANEL, fg=TEXT,
                  font=(FONT, 9), relief="flat", bd=0,
                  padx=12, pady=6, cursor="hand2",
                  activebackground=BORDER,
                  command=self._pick_files).pack(side="left")
        self.files_label = tk.Label(files_row, text="No extra files added",
                                     bg=BG, fg=SUBTEXT, font=(FONT, 9))
        self.files_label.pack(side="left", padx=10)

        # ── SECTION: Warning ──
        self._section(f, "⚠️  Safety Warning  (optional — for dangerous packages)")

        self.warning_var = tk.BooleanVar()
        tk.Checkbutton(f, text="This package requires the flag system (like controllocalapps)",
                       variable=self.warning_var,
                       bg=BG, fg=TEXT,
                       selectcolor=INPUT_BG,
                       activebackground=BG,
                       font=(FONT, 9),
                       command=self._toggle_warning).pack(anchor="w", **pad)

        self.warning_frame = tk.Frame(f, bg=BG)
        self.warning_text  = self._field(self.warning_frame, "Warning message",
            "e.g. THIS MAY BREAK STUFF ONLY USE IF YOU KNOW WHAT YOU ARE DOING",
            padx=24, pady=4)

        # ── OUTPUT ──
        self._section(f, "💾  Output")

        out_row = tk.Frame(f, bg=BG)
        out_row.pack(fill="x", **pad)
        self.out_path = tk.Entry(out_row, bg=INPUT_BG, fg=INPUT_FG,
                                  insertbackground=INPUT_FG,
                                  font=(FONT, 10), relief="flat",
                                  highlightbackground=BORDER,
                                  highlightthickness=1, width=48)
        self.out_path.pack(side="left", ipady=6, padx=(0,8))
        self.out_path.insert(0, os.path.join(os.path.expanduser("~"), "Desktop"))
        tk.Button(out_row, text="Browse",
                  bg=PANEL, fg=TEXT,
                  font=(FONT, 9), relief="flat", bd=0,
                  padx=12, pady=6, cursor="hand2",
                  activebackground=BORDER,
                  command=self._pick_output).pack(side="left")

        # ── STATUS ──
        self.status_var = tk.StringVar(value="")
        self.status_lbl = tk.Label(f, textvariable=self.status_var,
                                    bg=BG, fg=SUCCESS,
                                    font=(FONT, 9, "bold"),
                                    wraplength=700, justify="left")
        self.status_lbl.pack(anchor="w", **pad)

        # ── CREATE BUTTON ──
        tk.Button(f, text="✅  Create Package",
                  bg=ACCENT, fg="white",
                  font=(FONT, 13, "bold"),
                  relief="flat", bd=0,
                  padx=24, pady=12,
                  cursor="hand2",
                  activebackground=ACCENT2,
                  activeforeground="white",
                  command=self._create_package).pack(pady=20)

        tk.Label(f, text="", bg=BG).pack()  # spacer

    def _section(self, parent, title):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x", padx=24, pady=(16, 2))
        tk.Label(frame, text=title, bg=BG, fg=ACCENT,
                 font=(FONT, 11, "bold")).pack(side="left")
        tk.Frame(frame, bg=BORDER, height=1).pack(
            side="left", fill="x", expand=True, padx=10, pady=6)

    def _field(self, parent, label, placeholder="", **pack_kwargs):
        tk.Label(parent, text=label, bg=BG, fg=TEXT,
                 font=(FONT, 9, "bold")).pack(anchor="w", **pack_kwargs)
        entry = tk.Entry(parent, bg=INPUT_BG, fg=INPUT_FG,
                         insertbackground=INPUT_FG,
                         font=(FONT, 10), relief="flat",
                         highlightbackground=BORDER,
                         highlightthickness=1)
        entry.pack(fill="x", ipady=7, **pack_kwargs)
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=SUBTEXT)
            def on_focus_in(e, en=entry, ph=placeholder):
                if en.get() == ph: en.delete(0, "end"); en.config(fg=INPUT_FG)
            def on_focus_out(e, en=entry, ph=placeholder):
                if not en.get(): en.insert(0, ph); en.config(fg=SUBTEXT)
            entry.bind("<FocusIn>",  on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
        return entry

    def _add_builtin_row(self):
        row = tk.Frame(self.builtins_frame, bg=PANEL,
                       highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", pady=4)

        name_var = tk.StringVar()
        code_var = tk.StringVar()

        tk.Label(row, text="Command name:", bg=PANEL, fg=SUBTEXT,
                 font=(FONT, 8)).grid(row=0, column=0, sticky="w", padx=8, pady=(8,2))
        name_entry = tk.Entry(row, textvariable=name_var,
                               bg=INPUT_BG, fg=INPUT_FG,
                               insertbackground=INPUT_FG,
                               font=("Consolas", 10), relief="flat",
                               highlightbackground=BORDER, highlightthickness=1,
                               width=22)
        name_entry.grid(row=1, column=0, padx=8, pady=(0,8), ipady=5)
        name_entry.insert(0, "mycommand")

        tk.Label(row, text="Python code (use 'args' for arguments):",
                 bg=PANEL, fg=SUBTEXT, font=(FONT, 8)).grid(
                     row=0, column=1, sticky="w", padx=8, pady=(8,2))
        code_entry = tk.Entry(row, textvariable=code_var,
                               bg=INPUT_BG, fg=INPUT_FG,
                               insertbackground=INPUT_FG,
                               font=("Consolas", 10), relief="flat",
                               highlightbackground=BORDER, highlightthickness=1,
                               width=38)
        code_entry.grid(row=1, column=1, padx=8, pady=(0,8), ipady=5)
        code_entry.insert(0, "print(args[0] if args else 'hello!')")

        # remove button
        def remove_row():
            self.builtin_entries.remove((name_var, code_var))
            row.destroy()

        tk.Button(row, text="✕", bg=PANEL, fg=ERROR,
                  font=(FONT, 10, "bold"), relief="flat", bd=0,
                  cursor="hand2", activebackground=PANEL,
                  command=remove_row).grid(row=0, column=2, rowspan=2, padx=8)

        self.builtin_entries.append((name_var, code_var))

    def _pick_files(self):
        files = filedialog.askopenfilenames(
            title="Pick extra files to bundle",
            filetypes=[("All files", "*.*")])
        if files:
            self.extra_files = list(files)
            names = [os.path.basename(f) for f in files]
            self.files_label.config(
                text=", ".join(names[:3]) + (f" +{len(names)-3} more" if len(names)>3 else ""),
                fg=TEXT)

    def _pick_output(self):
        path = filedialog.askdirectory(title="Choose output folder")
        if path:
            self.out_path.delete(0, "end")
            self.out_path.insert(0, path)

    def _toggle_warning(self):
        if self.warning_var.get():
            self.warning_frame.pack(fill="x", padx=24)
        else:
            self.warning_frame.pack_forget()

    def _status(self, msg, color=SUCCESS):
        self.status_var.set(msg)
        self.status_lbl.config(fg=color)
        self.root.update()

    # ─────────────────────────────────────────
    #  CREATE PACKAGE
    # ─────────────────────────────────────────

    def _create_package(self):
        # ── validate ──
        def get(entry):
            v = entry.get().strip()
            return "" if v in ("", None) else v

        name    = get(self.pkg_name)
        version = get(self.pkg_version)
        desc    = get(self.pkg_desc)
        author  = get(self.pkg_author) or "Unknown"
        out_dir = get(self.out_path)

        # clear placeholder junk
        placeholders = [
            "e.g. customwindowtitle  (lowercase, no spaces)",
            "e.g. 1.0.0",
            "What does this package do?",
            "Your name or username",
        ]
        if name in placeholders:    name = ""
        if version in placeholders: version = ""
        if desc in placeholders:    desc = ""

        if not name:
            self._status("❌  Package name is required.", ERROR); return
        if not re.match(r'^[a-z0-9_]+$', name):
            self._status("❌  Package name: lowercase letters, numbers, underscores only.", ERROR); return
        if not version:
            self._status("❌  Version is required (e.g. 1.0.0).", ERROR); return
        if not desc:
            self._status("❌  Description is required.", ERROR); return
        if not out_dir or not os.path.isdir(out_dir):
            self._status("❌  Output folder doesn't exist. Click Browse to pick one.", ERROR); return

        self._status("⏳  Building package...", WARNING)

        # ── build init.py ──
        usage_lines = [l for l in self.usage_box.get("1.0","end").splitlines() if l.strip()]
        usage_repr  = json.dumps(usage_lines, indent=4)

        builtins_code = ""
        builtins_dict = ""
        for name_var, code_var in self.builtin_entries:
            fn_name  = name_var.get().strip()
            fn_code  = code_var.get().strip()
            if fn_name and fn_code:
                safe_name = fn_name.replace(".", "_").replace("-", "_")
                builtins_code += f'\ndef _cmd_{safe_name}(args):\n    {fn_code}\n'
                builtins_dict += f'    "{fn_name}": _cmd_{safe_name},\n'

        warning_block = ""
        if self.warning_var.get():
            warn_msg = get(self.warning_text)
            warning_block = f'''
WARNING = "{warn_msg}"
_flags  = {{"acknowledged": False}}

def require_flag():
    if not _flags["acknowledged"]:
        raise RuntimeError(
            f"Package \\"{name}\\" requires acknowledgement.\\n"
            f"  Warning: {{WARNING}}\\n"
            f"  Fix: Add the flag system to your script."
        )
'''

        init_py = f'''"""
Netch Package: {name} v{version}
{desc}
Author: {author}
Generated by Netch Package Creator
"""

PACKAGE_NAME    = "{name}"
PACKAGE_VERSION = "{version}"
{warning_block}
{builtins_code}

NETCH_BUILTINS = {{
{builtins_dict}}}

def on_load():
    print(f"[{name}] v{version} loaded!")
    print(f"[{name}] {desc}")

on_load()
'''

        # ── build package.json ──
        meta = {
            "name":        name,
            "version":     version,
            "description": desc,
            "author":      author,
            "installed":   False,
            "usage":       usage_lines,
        }
        if self.warning_var.get():
            meta["warning"] = get(self.warning_text)

        # ── write to temp folder and zip ──
        tmp_dir  = os.path.join(out_dir, f"_tmp_{name}")
        pkg_path = os.path.join(out_dir, f"{name}.ntchpkg")

        try:
            os.makedirs(tmp_dir, exist_ok=True)

            with open(os.path.join(tmp_dir, "init.py"), "w") as f:
                f.write(init_py)
            with open(os.path.join(tmp_dir, "package.json"), "w") as f:
                json.dump(meta, f, indent=2)

            # copy extra files
            for ef in self.extra_files:
                shutil.copy(ef, tmp_dir)

            # zip everything into .ntchpkg
            with zipfile.ZipFile(pkg_path, "w", zipfile.ZIP_DEFLATED) as z:
                for file in os.listdir(tmp_dir):
                    z.write(os.path.join(tmp_dir, file), file)

            shutil.rmtree(tmp_dir)

            # also write a preview of index.json entry
            index_entry = {name: {**meta, "file": f"{name}.ntchpkg"}}
            index_preview_path = os.path.join(out_dir, f"{name}_index_entry.json")
            with open(index_preview_path, "w") as f:
                json.dump(index_entry, f, indent=2)

            self._status(
                f"✅  Package created!  →  {pkg_path}\n"
                f"Also saved: {name}_index_entry.json  (add this to packages/index.json on GitHub)",
                SUCCESS
            )
            messagebox.showinfo("Package Created!",
                f"Your package is ready!\n\n"
                f"📦  {name}.ntchpkg\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"STEP 1 — Test your package locally\n"
                f"Put the .ntchpkg in ~/Netch2/packages/{name}/\n"
                f"then use: importpkg {name}\n\n"
                f"STEP 2 — Want it as an official Netch package?\n"
                f"Post on r/netchcoding2 with:\n"
                f"  • Title: [Package] {name}\n"
                f"  • What it does\n"
                f"  • Attach the .ntchpkg file\n"
                f"Netch developers will review and add it officially!\n\n"
                f"STEP 3 — Add to packages/index.json on GitHub\n"
                f"Use the {name}_index_entry.json file as a reference.")

        except Exception as e:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            self._status(f"❌  Error: {e}", ERROR)

# ─────────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app  = NetchPackageCreator(root)
    root.mainloop()
