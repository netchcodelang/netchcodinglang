#!/usr/bin/env python3
"""
Netch Package Creator
A GUI tool to create .ntchpkg packages easily
An Aerotion Production
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, json, zipfile, shutil, re

NETCH_DIR    = os.path.join(os.path.expanduser("~"), "Netch2")
PACKAGES_DIR = os.path.join(NETCH_DIR, "packages")
os.makedirs(PACKAGES_DIR, exist_ok=True)

# ── theme ──
BG       = "#1a1a2e"
PANEL    = "#16213e"
ACCENT   = "#0f3460"
BLUE     = "#4361ee"
GREEN    = "#4cc9f0"
WHITE    = "#e0e0e0"
GRAY     = "#888888"
RED      = "#e63946"
FONT     = ("Segoe UI", 11)
FONT_SM  = ("Segoe UI", 9)
FONT_LG  = ("Segoe UI", 14, "bold")
MONO     = ("Consolas", 10)

class PackageCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Netch Package Creator — Aerotion Productions")
        self.root.geometry("860x680")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.extra_files = []   # list of (src_path, dest_name)
        self.build_ui()

    # ────────────────────────────────────────────
    #  UI
    # ────────────────────────────────────────────

    def build_ui(self):
        # ── top bar ──
        top = tk.Frame(self.root, bg=ACCENT, height=56)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="📦  Netch Package Creator",
                 bg=ACCENT, fg=WHITE, font=FONT_LG).pack(side="left", padx=20, pady=12)
        tk.Label(top, text="An Aerotion Production",
                 bg=ACCENT, fg=GRAY, font=FONT_SM).pack(side="right", padx=20)

        # ── notebook / tabs ──
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",       background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",   background=PANEL, foreground=GRAY,
                        padding=[16,8], font=FONT)
        style.map("TNotebook.Tab",
                  background=[("selected", BLUE)],
                  foreground=[("selected", WHITE)])

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=12, pady=12)

        self.tab_info   = tk.Frame(self.nb, bg=BG)
        self.tab_code   = tk.Frame(self.nb, bg=BG)
        self.tab_files  = tk.Frame(self.nb, bg=BG)
        self.tab_build  = tk.Frame(self.nb, bg=BG)

        self.nb.add(self.tab_info,  text="  📋 Package Info  ")
        self.nb.add(self.tab_code,  text="  📝 Code  ")
        self.nb.add(self.tab_files, text="  📁 Extra Files  ")
        self.nb.add(self.tab_build, text="  🔨 Build  ")

        self._build_info_tab()
        self._build_code_tab()
        self._build_files_tab()
        self._build_build_tab()

    # ── helpers ──
    def label(self, parent, text, small=False):
        tk.Label(parent, text=text, bg=BG, fg=GRAY if small else WHITE,
                 font=FONT_SM if small else FONT).pack(anchor="w", padx=20, pady=(10,2))

    def entry(self, parent, textvariable, placeholder=""):
        e = tk.Entry(parent, textvariable=textvariable,
                     bg=PANEL, fg=WHITE, insertbackground=WHITE,
                     relief="flat", font=FONT, bd=0, highlightthickness=1,
                     highlightcolor=BLUE, highlightbackground=ACCENT)
        e.pack(fill="x", padx=20, pady=2, ipady=8)
        if placeholder and not textvariable.get():
            e.insert(0, placeholder)
            e.config(fg=GRAY)
            e.bind("<FocusIn>",  lambda ev, en=e, ph=placeholder, tv=textvariable:
                   self._clear_placeholder(ev, en, ph, tv))
            e.bind("<FocusOut>", lambda ev, en=e, ph=placeholder, tv=textvariable:
                   self._set_placeholder(ev, en, ph, tv))
        return e

    def _clear_placeholder(self, e, entry, placeholder, tv):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg=WHITE)

    def _set_placeholder(self, e, entry, placeholder, tv):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=GRAY)

    def btn(self, parent, text, cmd, color=BLUE, side="left"):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=color, fg=WHITE, relief="flat", font=FONT,
                      padx=18, pady=8, cursor="hand2",
                      activebackground=color, activeforeground=WHITE, bd=0)
        b.pack(side=side, padx=6, pady=6)
        b.bind("<Enter>", lambda e: b.config(bg=self._lighten(color)))
        b.bind("<Leave>", lambda e: b.config(bg=color))
        return b

    def _lighten(self, hex_color):
        try:
            r=int(hex_color[1:3],16); g=int(hex_color[3:5],16); b=int(hex_color[5:7],16)
            r=min(255,r+30); g=min(255,g+30); b=min(255,b+30)
            return f"#{r:02x}{g:02x}{b:02x}"
        except: return hex_color

    # ── info tab ──
    def _build_info_tab(self):
        p = self.tab_info
        tk.Label(p, text="Package Information", bg=BG, fg=WHITE,
                 font=FONT_LG).pack(anchor="w", padx=20, pady=(18,4))
        tk.Label(p, text="Fill in the details about your package.",
                 bg=BG, fg=GRAY, font=FONT_SM).pack(anchor="w", padx=20, pady=(0,12))

        self.v_name    = tk.StringVar()
        self.v_version = tk.StringVar(value="1.0.0")
        self.v_desc    = tk.StringVar()
        self.v_author  = tk.StringVar()
        self.v_warning = tk.StringVar()

        self.label(p, "Package Name  (no spaces, lowercase)")
        self.entry(p, self.v_name, "mypkg")

        self.label(p, "Version")
        self.entry(p, self.v_version, "1.0.0")

        self.label(p, "Description")
        self.entry(p, self.v_desc, "What does this package do?")

        self.label(p, "Author")
        self.entry(p, self.v_author, "Your name")

        self.label(p, "Warning  (optional — shown during install)")
        self.entry(p, self.v_warning, "Leave blank if none")

        # usage lines
        self.label(p, "Usage lines  (shown after install — one per line)")
        self.usage_box = tk.Text(p, height=4, bg=PANEL, fg=WHITE,
                                 insertbackground=WHITE, relief="flat",
                                 font=MONO, bd=0, highlightthickness=1,
                                 highlightbackground=ACCENT)
        self.usage_box.pack(fill="x", padx=20, pady=2)
        self.usage_box.insert("end", "importpkg mypkg\n")

    # ── code tab ──
    def _build_code_tab(self):
        p = self.tab_code
        tk.Label(p, text="Package Code  (init.py)",
                 bg=BG, fg=WHITE, font=FONT_LG).pack(anchor="w", padx=20, pady=(18,2))
        tk.Label(p,
                 text="This is the Python code that runs when someone does importpkg yourpkg\n"
                      "Use NETCH_BUILTINS dict to register new functions that work in .ntch scripts.",
                 bg=BG, fg=GRAY, font=FONT_SM, justify="left").pack(anchor="w", padx=20, pady=(0,10))

        # toolbar
        bar = tk.Frame(p, bg=BG)
        bar.pack(fill="x", padx=20, pady=(0,4))
        self.btn(bar, "Insert Template", self._insert_template)
        self.btn(bar, "Insert Builtin Example", self._insert_builtin_example)

        self.code_box = tk.Text(p, bg=PANEL, fg=WHITE,
                                insertbackground=WHITE, relief="flat",
                                font=MONO, bd=0, highlightthickness=1,
                                highlightbackground=ACCENT,
                                wrap="none", tabs=("1c",))
        self.code_box.pack(fill="both", expand=True, padx=20, pady=(0,12))

        # scrollbar
        sb = tk.Scrollbar(self.code_box, command=self.code_box.yview)
        self.code_box.config(yscrollcommand=sb.set)

        self._insert_template()

    def _insert_template(self):
        name = self.v_name.get().strip() or "mypkg"
        self.code_box.delete("1.0", "end")
        self.code_box.insert("end", f'''"""
Netch Package: {name}
{self.v_desc.get().strip() or "My package description"}
"""

PACKAGE_NAME    = "{name}"
PACKAGE_VERSION = "{self.v_version.get().strip() or "1.0.0"}"

# Register functions that can be used in .ntch scripts
# Format: "functionname": lambda args: your_code_here
NETCH_BUILTINS = {{
    # "myfunction": lambda args: print("Hello from {name}!"),
}}

# This runs when the package is loaded
print(f"[{name}] Package loaded!")
''')

    def _insert_builtin_example(self):
        self.code_box.insert("end", '''
# ── Example: add a new function to netch ──
# After adding this, users can call: myalert("Hello!")
def _my_alert(args):
    import tkinter.messagebox as mb
    msg = str(args[0]) if args else "Alert!"
    mb.showinfo("Alert", msg)

NETCH_BUILTINS["myalert"] = _my_alert
''')

    # ── files tab ──
    def _build_files_tab(self):
        p = self.tab_files
        tk.Label(p, text="Extra Files",
                 bg=BG, fg=WHITE, font=FONT_LG).pack(anchor="w", padx=20, pady=(18,2))
        tk.Label(p, text="Add images, data files, or anything else your package needs.",
                 bg=BG, fg=GRAY, font=FONT_SM).pack(anchor="w", padx=20, pady=(0,12))

        bar = tk.Frame(p, bg=BG)
        bar.pack(fill="x", padx=20, pady=(0,8))
        self.btn(bar, "＋  Add File", self._add_file)
        self.btn(bar, "✕  Remove Selected", self._remove_file, color=RED)

        # file list
        list_frame = tk.Frame(p, bg=PANEL, bd=0, highlightthickness=1,
                              highlightbackground=ACCENT)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0,12))

        self.file_listbox = tk.Listbox(list_frame, bg=PANEL, fg=WHITE,
                                       selectbackground=BLUE, relief="flat",
                                       font=FONT, bd=0, highlightthickness=0)
        self.file_listbox.pack(fill="both", expand=True, padx=4, pady=4)

        tk.Label(p, text="Files are included in the .ntchpkg and extracted when installed.",
                 bg=BG, fg=GRAY, font=FONT_SM).pack(anchor="w", padx=20)

    def _add_file(self):
        paths = filedialog.askopenfilenames(title="Select files to include in package")
        for path in paths:
            dest = os.path.basename(path)
            self.extra_files.append((path, dest))
            self.file_listbox.insert("end", f"  {dest}  ←  {path}")

    def _remove_file(self):
        sel = self.file_listbox.curselection()
        for idx in reversed(sel):
            self.file_listbox.delete(idx)
            self.extra_files.pop(idx)

    # ── build tab ──
    def _build_build_tab(self):
        p = self.tab_build
        tk.Label(p, text="Build Package",
                 bg=BG, fg=WHITE, font=FONT_LG).pack(anchor="w", padx=20, pady=(18,2))
        tk.Label(p, text="Review and build your .ntchpkg file.",
                 bg=BG, fg=GRAY, font=FONT_SM).pack(anchor="w", padx=20, pady=(0,12))

        # output dir
        dir_frame = tk.Frame(p, bg=BG)
        dir_frame.pack(fill="x", padx=20, pady=4)
        tk.Label(dir_frame, text="Save to:", bg=BG, fg=WHITE, font=FONT).pack(side="left")
        self.v_outdir = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Desktop"))
        tk.Entry(dir_frame, textvariable=self.v_outdir, bg=PANEL, fg=WHITE,
                 relief="flat", font=FONT, insertbackground=WHITE,
                 highlightthickness=1, highlightbackground=ACCENT).pack(
                 side="left", fill="x", expand=True, padx=8, ipady=6)
        self.btn(dir_frame, "Browse", lambda: self.v_outdir.set(
            filedialog.askdirectory() or self.v_outdir.get()))

        # also install locally checkbox
        self.v_also_install = tk.BooleanVar(value=True)
        tk.Checkbutton(p, text="Also install to local Netch packages folder  (so you can test it right away)",
                       variable=self.v_also_install, bg=BG, fg=WHITE,
                       selectcolor=PANEL, activebackground=BG,
                       font=FONT).pack(anchor="w", padx=20, pady=8)

        # build button
        build_frame = tk.Frame(p, bg=BG)
        build_frame.pack(pady=8)
        big_btn = tk.Button(build_frame, text="  🔨  Build .ntchpkg  ",
                            command=self.build_package,
                            bg=GREEN, fg="#0a0a0a", relief="flat",
                            font=("Segoe UI", 13, "bold"),
                            padx=28, pady=14, cursor="hand2",
                            activebackground="#38b2d8")
        big_btn.pack()

        # log
        tk.Label(p, text="Build Log", bg=BG, fg=GRAY, font=FONT_SM).pack(
            anchor="w", padx=20, pady=(16,2))
        self.log_box = tk.Text(p, height=12, bg=PANEL, fg=GREEN,
                               insertbackground=WHITE, relief="flat",
                               font=MONO, bd=0, state="disabled",
                               highlightthickness=1, highlightbackground=ACCENT)
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(0,12))

    # ────────────────────────────────────────────
    #  BUILD LOGIC
    # ────────────────────────────────────────────

    def log(self, msg, color=None):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def build_package(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")

        # ── validate ──
        name    = self.v_name.get().strip()
        version = self.v_version.get().strip() or "1.0.0"
        desc    = self.v_desc.get().strip()
        author  = self.v_author.get().strip()
        warning = self.v_warning.get().strip()
        outdir  = self.v_outdir.get().strip()
        code    = self.code_box.get("1.0", "end").strip()
        usage   = [l for l in self.usage_box.get("1.0","end").splitlines() if l.strip()]

        if not name:
            messagebox.showerror("Missing Info", "Package name is required!"); return
        if not re.match(r'^[a-z0-9_]+$', name):
            messagebox.showerror("Invalid Name",
                "Package name must be lowercase with no spaces.\nOnly letters, numbers, underscores."); return
        if not desc:
            messagebox.showerror("Missing Info", "Description is required!"); return
        if not os.path.isdir(outdir):
            messagebox.showerror("Bad Output Dir", f"Output folder doesn't exist:\n{outdir}"); return

        self.log(f"Starting build: {name} v{version}")
        self.log("━"*44)

        # ── temp build folder ──
        import tempfile
        tmp = tempfile.mkdtemp(prefix="netch_pkg_")
        self.log(f"Temp folder: {tmp}")

        try:
            # write init.py
            init_path = os.path.join(tmp, "init.py")
            with open(init_path, "w", encoding="utf-8") as f:
                f.write(code)
            self.log("✓ init.py written")

            # write package.json
            meta = {
                "name":        name,
                "version":     version,
                "description": desc,
                "author":      author,
                "usage":       usage,
            }
            if warning and warning.lower() not in ("leave blank if none", ""):
                meta["warning"] = warning
            meta_path = os.path.join(tmp, "package.json")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
            self.log("✓ package.json written")

            # copy extra files
            for src, dest in self.extra_files:
                shutil.copy(src, os.path.join(tmp, dest))
                self.log(f"✓ included: {dest}")

            # zip into .ntchpkg
            pkg_filename = f"{name}.ntchpkg"
            pkg_path     = os.path.join(outdir, pkg_filename)
            with zipfile.ZipFile(pkg_path, "w", zipfile.ZIP_DEFLATED) as z:
                for fname in os.listdir(tmp):
                    z.write(os.path.join(tmp, fname), fname)
            self.log(f"✓ built: {pkg_path}")

            # also install locally?
            if self.v_also_install.get():
                local_pkg_dir = os.path.join(PACKAGES_DIR, name)
                if os.path.exists(local_pkg_dir):
                    shutil.rmtree(local_pkg_dir)
                os.makedirs(local_pkg_dir)
                with zipfile.ZipFile(pkg_path, "r") as z:
                    z.extractall(local_pkg_dir)
                self.log(f"✓ installed locally: {local_pkg_dir}")

            self.log("━"*44)
            self.log(f"SUCCESS! Package ready: {pkg_filename}")
            self.log("")
            self.log("Next steps:")
            self.log(f"  1. Upload {pkg_filename} to your GitHub packages/ folder")
            self.log(f"  2. Add an entry for '{name}' to packages/index.json")
            self.log(f"  3. Users install with: netch pkg install {name}")
            if self.v_also_install.get():
                self.log(f"  4. Test it now: importpkg {name}")

            messagebox.showinfo("Build Complete!",
                f"Package built successfully!\n\n"
                f"File: {pkg_path}\n\n"
                f"Upload it to GitHub packages/ folder\n"
                f"and add it to packages/index.json")

        except Exception as e:
            self.log(f"ERROR: {e}")
            messagebox.showerror("Build Failed", str(e))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


def main():
    root = tk.Tk()
    app = PackageCreator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
