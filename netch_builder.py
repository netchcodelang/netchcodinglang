"""
Netch Builder 2 — Visual IDE for Netch 2
An Aerotion Production
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import os, sys, json, subprocess, tempfile, threading, re

# ── THEME ──────────────────────────────────────
THEMES = {
    "dark": {
        "bg":BG, "sidebar":"#16161f", "panel":"#2a2a3e",
        "editor":"#12121e", "text":"#e0e0f0", "subtext":"#7070a0",
        "border":"#3a3a5a", "entry":"#1a1a2e", "accent":"#7c6af7",
        "accent2":"#5a4fcf", "success":"#3fb950", "error":"#f85149",
        "warn":"#e3b341"
    } if False else None,
}

BG      = "#1e1e2e"
SIDEBAR = "#16161f"
PANEL   = "#2a2a3e"
EDITOR  = "#12121e"
LIGHT_BG    = "#f5f5f5"
LIGHT_SIDE  = "#e8e8f0"
LIGHT_PANEL = "#ffffff"
ACCENT  = "#7c6af7"
ACCENT2 = "#5a4fcf"
TEXT    = "#e0e0f0"
SUBTEXT = "#7070a0"
SUCCESS = "#3fb950"
ERROR   = "#f85149"
WARN    = "#e3b341"
BORDER  = "#3a3a5a"
FONT    = "Segoe UI"
CODE    = "Consolas"

KEYWORDS  = ["if","else","while","repeat","function","run","use","window",
             "importpkg","import","true","false","for","foreach","from",
             "to","in","dark:true","dark:false","end","control","flag",
             "confirmation","import all pkgs"]
BUILTINS  = sorted([
    "print","label","button","cr.button","textbox","passwordbox","displaytext",
    "dropdown","checkbox","radiobutton","slider","listbox","tabcontrol","addtab",
    "image","progressbar","setprogress","input","getinput","getchecked",
    "getradio","getdropdown","getslider","getlist","sound.play","sound.stop",
    "openfile","deletefile","copyfile","download.file","send.post","send.json",
    "get.request","connect.server","send.message","send.textbox","run.bat",
    "run.shell","random","number","upper","lower","contains","length","ask",
    "time.now","window.title","window.size","window.theme","window.center",
    "window.minimize","window.maximize","window.icon","window.opacity",
    "window.resizable","window.always.top","window.fullscreen","separator",
    "spacer","heading","link","colorpicker","set.font","clear.window",
    "url.open","json.parse","json.make","typeof","tonumber","totext",
    "isnumber","isempty","math.abs","math.round","math.floor","math.ceil",
    "math.sqrt","math.power","math.max","math.min","math.clamp",
    "str.replace","str.split","str.trim","str.starts","str.ends","str.repeat",
    "str.index","str.reverse","str.count","str.format","list.new","list.add",
    "list.get","list.length","list.remove","list.contains","list.join",
    "file.read","file.write","file.append","file.exists","file.rename",
    "file.size","clipboard.copy","clipboard.paste","dialog.info","dialog.error",
    "dialog.warn","dialog.ask","dialog.input","dialog.file","dialog.folder",
    "dialog.save","sys.env","sys.exit","sys.platform","sys.username",
    "sys.homedir","sys.cwd","sys.desktop","date.today","date.year",
    "date.month","date.day","time.sleep","time.stamp","ai.key","ai.system",
    "ai.model","ai.ask","ai.chat","ai.clear","ai.history","display.webpage",
    "windowtitle","dark","canvas.new","canvas.line","canvas.rect","canvas.circle",
    "canvas.text","canvas.image","canvas.clear","canvas.onclick","tts.say",
    "tts.save","voice.listen","voice.listen.offline","video.play","video.stop",
    "pdf.create","pdf.text","pdf.heading","pdf.newpage","pdf.save",
    "email.send","email.send.html","browser.open","plugin.load","plugin.call",
], key=len, reverse=True)

WIDGET_SNIPPETS = {
    "📝 Label":         'label("Your text here")',
    "🔠 Heading":       'heading("Big Title")',
    "🔘 Button":        'button("Click Me") action print("Clicked!")',
    "🔵 Round Button":  'cr.button("Rounded") action print("Clicked!")',
    "📥 Textbox":       'textbox("mybox", 30, "Type here...")',
    "🔐 Password Box":  'passwordbox("mypass")',
    "📋 Dropdown":      'dropdown("mydrop", "Option 1", "Option 2", "Option 3")',
    "☑️ Checkbox":      'checkbox("mycheck", "Check me")',
    "🔘 Radio Button":  'radiobutton("mygroup", "Option A", "a")',
    "🎚️ Slider":        'slider("myslider", 0, 100)',
    "📜 List Box":      'listbox("mylist", "Item 1", "Item 2", "Item 3")',
    "📊 Progress Bar":  'progressbar("myprog", 50)',
    "🖼️ Image":         'image("yourimage.png")',
    "━ Separator":      'separator',
    "⬛ Spacer":        'spacer(20)',
    "🔗 Link":          'link("Click here", "https://example.com")',
    "📑 Tabs":          'tabcontrol("mytabs")\naddtab("mytabs", "Tab 1")\naddtab("mytabs", "Tab 2")',
    "🌐 Webpage":       'display.webpage("https://example.com")',
    "🎨 Canvas":        'canvas.new("mycanvas", 400, 300)\ncanvas.rect("mycanvas", 10, 10, 200, 100, "#0078d4")\ncanvas.text("mycanvas", 100, 50, "Hello!")',
    "🎬 Video":         'video.play("myvideo.mp4")',
}

SNIPPETS = {
    "If / Else":        "if x > 0\n    print(\"positive\")\nelse\n    print(\"zero or negative\")",
    "While Loop":       "x = 0\nwhile x < 5\n    print(x)\n    x = x + 1",
    "For Loop":         "for i from 1 to 10\n    print(i)",
    "Foreach":          "mylist = list.new(\"a\", \"b\", \"c\")\nforeach item in mylist\n    print(item)",
    "Function":         "function greet\n    print(\"Hello!\")\n\nrun(greet)",
    "File Read/Write":  'file.write("myfile.txt", "Hello Netch!")\ncontent = file.read("myfile.txt")\nprint(content)',
    "Dialog Ask":       'answer = dialog.ask("Confirm", "Are you sure?")\nif answer == true\n    print("You clicked yes!")',
    "AI Chat":          'importpkg ainetchintegration\nai.key("your-key-here")\nai.system("You are a helpful assistant")\nreply = ai.ask("What is Netch 2?")\nprint(reply)',
    "Send to Server":   'textbox("msg", 30, "Type message...")\nbutton("Send") action send.textbox("msg", "https://yourserver.com/api", "message")',
    "Dark Window":      'dark:true\nuse window\nwindow.title("Dark App")\nwindow.size(800, 500)\nwindow.center',
    "Canvas Drawing":   'use window\ncanvas.new("c", 500, 300, "#1e1e2e")\ncanvas.rect("c", 50, 50, 200, 150, "#7c6af7")\ncanvas.circle("c", 350, 120, 60, "#3fb950")\ncanvas.text("c", 250, 20, "My Canvas", "#ffffff")',
    "Custom Window":    'importpkg customwindowtitle\nuse window\nwindow.size(800, 500)\nwindow.center\nwindowtitle("title.nframetchpng", "My App")',
    "Text to Speech":   'tts.say("Hello from Netch 2!")',
    "Voice Input":      'print("Listening...")\ntext = voice.listen()\nprint(text)',
    "PDF Create":       'pdf.create("myreport.pdf", "My Report")\npdf.heading("Hello World")\npdf.text("This was made with Netch 2")\npdf.save()',
    "Email Send":       'email.send("you@gmail.com", "yourpassword", "them@gmail.com", "Subject", "Hello from Netch!")',
    "Get User Input":   'textbox("name", 25, "Enter your name...")\nbutton("Submit") action print(getinput("name"))',
    "List Operations":  'mylist = list.new("Apple", "Banana", "Orange")\nlist.add("mylist", "Grape")\nprint(list.length("mylist"))\nprint(list.get("mylist", 0))',
}

class NetchBuilder:
    def __init__(self, root):
        self.root        = root
        self.dark_mode   = True
        self.current_file= None
        self.unsaved     = False
        self._proc       = None
        self.interpreter = self._find_interpreter()
        self.compiler    = self._find_compiler()

        self.root.title("Netch Builder 2 — An Aerotion Production")
        self.root.geometry("1400x860")
        self.root.configure(bg=self._bg())
        self.root.state("zoomed")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        self._new_file()

    def _bg(self):    return BG if self.dark_mode else LIGHT_BG
    def _side(self):  return SIDEBAR if self.dark_mode else LIGHT_SIDE
    def _panel(self): return PANEL if self.dark_mode else LIGHT_PANEL
    def _fg(self):    return TEXT if self.dark_mode else "#1a1a2a"
    def _sfg(self):   return SUBTEXT if self.dark_mode else "#606080"
    def _ed(self):    return EDITOR if self.dark_mode else "#fdfdff"
    def _brd(self):   return BORDER if self.dark_mode else "#d0d0e0"

    def _find_interpreter(self):
        netch = os.path.join(os.path.expanduser("~"), "Netch2")
        for p in [os.path.join(netch,"interpreter.py"),
                  os.path.join(os.path.dirname(__file__),"interpreter.py"),
                  "interpreter.py"]:
            if os.path.exists(p): return p
        return None

    def _find_compiler(self):
        netch = os.path.join(os.path.expanduser("~"), "Netch2")
        for p in [os.path.join(netch,"netch_compile.py"),
                  os.path.join(os.path.dirname(__file__),"netch_compile.py"),
                  "netch_compile.py"]:
            if os.path.exists(p): return p
        return None

    # ── BUILD UI ───────────────────────────────
    def _build_ui(self):
        self._build_menu()
        self._build_toolbar()
        pane = tk.PanedWindow(self.root, orient="horizontal",
                               bg=self._bg(), sashwidth=4,
                               sashrelief="flat", bd=0)
        pane.pack(fill="both", expand=True)
        self._build_left(pane)
        self._build_center(pane)
        self._build_right(pane)
        self._build_statusbar()

    def _build_menu(self):
        mb = tk.Menu(self.root, bg=self._side(), fg=self._fg(),
                     activebackground=ACCENT, activeforeground="white",
                     relief="flat", bd=0)
        self.root.config(menu=mb)

        def menu(label, items):
            m = tk.Menu(mb, tearoff=0, bg=self._panel(), fg=self._fg(),
                        activebackground=ACCENT, activeforeground="white")
            mb.add_cascade(label=label, menu=m)
            for item in items:
                if item == "-": m.add_separator()
                else: m.add_command(label=item[0], command=item[1])
            return m

        menu("File", [
            ("New          Ctrl+N",      self._new_file),
            ("Open         Ctrl+O",      self._open_file),
            ("Save         Ctrl+S",      self._save_file),
            ("Save As      Ctrl+Shift+S",self._save_as),
            "-",
            ("Compile to EXE",           self._compile_exe),
            "-",
            ("Exit",                     self._on_close),
        ])
        menu("Run", [
            ("▶  Run Script    F5",  self._run_script),
            ("⏹  Stop",              self._stop_script),
        ])
        menu("Packages", [
            ("Install Package",    self._pkg_install),
            ("List Packages",      self._pkg_list),
            ("Update All Packages",self._pkg_update),
            "-",
            ("Open Package Creator",self._open_pkg_creator),
        ])
        menu("View", [
            ("Toggle Dark/Light",  self._toggle_theme),
            ("Increase Font Size", lambda: self._change_font(1)),
            ("Decrease Font Size", lambda: self._change_font(-1)),
        ])
        menu("Help", [
            ("Netch 2 Docs",   lambda: __import__('webbrowser').open("https://netchcodelang.github.io/netchcodinglang/docs.html")),
            ("Community",      lambda: __import__('webbrowser').open("https://reddit.com/r/netchcoding2")),
            ("GitHub",         lambda: __import__('webbrowser').open("https://github.com/netchcodelang/netchcodinglang")),
        ])

        for key, cmd in [("<Control-n>",self._new_file),("<Control-o>",self._open_file),
                         ("<Control-s>",self._save_file),("<F5>",self._run_script),
                         ("<F6>",self._compile_exe)]:
            self.root.bind(key, lambda e, c=cmd: c())

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=self._side(), height=46)
        bar.pack(fill="x"); bar.pack_propagate(False)

        def btn(text, cmd, bg=None, fg=None):
            b = tk.Button(bar, text=text, command=cmd,
                          bg=bg or self._panel(), fg=fg or self._fg(),
                          font=(FONT,9,"bold"), relief="flat", bd=0,
                          padx=14, pady=9, cursor="hand2",
                          activebackground=ACCENT, activeforeground="white")
            b.pack(side="left", padx=2, pady=4)
            return b

        btn("🆕",  self._new_file)
        btn("📂",  self._open_file)
        btn("💾",  self._save_file)
        tk.Frame(bar, bg=self._brd(), width=1).pack(side="left", fill="y", padx=6, pady=8)
        btn("▶ Run",         self._run_script,  ACCENT,    "white")
        btn("⏹",             self._stop_script, "#3a1a1a", ERROR)
        btn("🔨 Compile EXE",self._compile_exe, "#1a3a1a", SUCCESS)
        tk.Frame(bar, bg=self._brd(), width=1).pack(side="left", fill="y", padx=6, pady=8)
        btn("📦 Packages", self._pkg_install)
        btn("🌙/☀️",        self._toggle_theme)

        self.title_lbl = tk.Label(bar, text=" untitled.ntch",
                                   bg=self._side(), fg=self._sfg(), font=(FONT,9))
        self.title_lbl.pack(side="left", padx=6)

        tk.Label(bar, text="Netch Builder 2  •  An Aerotion Production",
                 bg=self._side(), fg=ACCENT, font=(FONT,9,"bold")).pack(side="right", padx=14)

    def _build_left(self, pane):
        left = tk.Frame(pane, bg=self._side(), width=190)
        pane.add(left, minsize=160)
        left.pack_propagate(False)

        def section(title):
            tk.Label(left, text=title, bg=self._side(), fg=ACCENT,
                     font=(FONT,8,"bold")).pack(anchor="w", padx=10, pady=(10,2))
            tk.Frame(left, bg=self._brd(), height=1).pack(fill="x", padx=8, pady=(0,4))

        def item(text, cmd):
            b = tk.Button(left, text=text, command=cmd,
                          bg=self._side(), fg=self._fg(), font=(FONT,9),
                          relief="flat", bd=0, padx=10, pady=4,
                          cursor="hand2", anchor="w", width=22,
                          activebackground=self._panel(), activeforeground=ACCENT)
            b.pack(fill="x", padx=4, pady=1)

        section("WIDGETS")
        for name, code in WIDGET_SNIPPETS.items():
            item(name, lambda c=code: self._insert(c))

        section("SNIPPETS")
        for name, code in SNIPPETS.items():
            item(name, lambda c=code: self._insert(c))

    def _build_center(self, pane):
        self.center = tk.Frame(pane, bg=self._bg())
        pane.add(self.center, minsize=500)

        # tab bar
        tabs = tk.Frame(self.center, bg=self._side(), height=30)
        tabs.pack(fill="x"); tabs.pack_propagate(False)
        self.tab_lbl = tk.Label(tabs, text="  untitled.ntch  ",
                                 bg=self._bg(), fg=self._fg(), font=(FONT,9), padx=4)
        self.tab_lbl.pack(side="left", ipady=4)

        # editor row
        edit_row = tk.Frame(self.center, bg=self._ed())
        edit_row.pack(fill="both", expand=True)

        self.line_nums = tk.Text(edit_row, width=4, bg="#0a0a18" if self.dark_mode else "#ededf5",
                                  fg=self._sfg(), font=(CODE,11), state="disabled",
                                  relief="flat", highlightthickness=0, bd=0,
                                  selectbackground="#0a0a18" if self.dark_mode else "#ededf5")
        self.line_nums.pack(side="left", fill="y")

        self.editor = tk.Text(edit_row, bg=self._ed(), fg=self._fg(),
                               font=(CODE,11), relief="flat",
                               insertbackground=ACCENT,
                               selectbackground="#3a3a6a" if self.dark_mode else "#c8c8ff",
                               undo=True, wrap="none",
                               highlightthickness=0, bd=0, spacing3=3,
                               tabs=("4c",))
        self.editor.pack(side="left", fill="both", expand=True)

        ys = ttk.Scrollbar(edit_row, orient="vertical",
                            command=lambda *a: (self.editor.yview(*a), self._sync_lines()))
        ys.pack(side="right", fill="y")
        self.editor.config(yscrollcommand=ys.set)
        xs = ttk.Scrollbar(self.center, orient="horizontal",
                            command=self.editor.xview)
        xs.pack(fill="x")
        self.editor.config(xscrollcommand=xs.set)

        self.editor.bind("<KeyRelease>",   self._on_key)
        self.editor.bind("<Return>",       self._auto_indent)
        self.editor.bind("<Tab>",          self._tab)
        self.editor.bind("<Control-z>",    lambda e: self.editor.edit_undo())
        self.editor.bind("<Control-y>",    lambda e: self.editor.edit_redo())

        self._setup_highlight()

        # console
        con_wrap = tk.Frame(self.center, bg=self._side(), height=170)
        con_wrap.pack(fill="x"); con_wrap.pack_propagate(False)

        ch = tk.Frame(con_wrap, bg=self._panel())
        ch.pack(fill="x")
        tk.Label(ch, text="  OUTPUT", bg=self._panel(), fg=self._sfg(),
                 font=(FONT,8,"bold")).pack(side="left", pady=4)
        tk.Button(ch, text="Clear", bg=self._panel(), fg=self._sfg(),
                  font=(FONT,8), relief="flat", bd=0, padx=8,
                  cursor="hand2", command=self._clear_console,
                  activebackground=self._brd()).pack(side="right", padx=4, pady=2)

        self.console = tk.Text(con_wrap, bg="#08080f" if self.dark_mode else "#f0f0f8",
                                fg=self._fg(), font=(CODE,10), relief="flat",
                                state="disabled", wrap="word", highlightthickness=0, bd=0)
        self.console.pack(fill="both", expand=True, padx=4, pady=(0,4))
        for tag, col in [("error",ERROR),("success",SUCCESS),("warn",WARN),("info","#58a6ff")]:
            self.console.tag_config(tag, foreground=col)

    def _build_right(self, pane):
        right = tk.Frame(pane, bg=self._side(), width=220)
        pane.add(right, minsize=180)
        right.pack_propagate(False)

        def section(title):
            tk.Label(right, text=title, bg=self._side(), fg=ACCENT,
                     font=(FONT,8,"bold")).pack(anchor="w", padx=10, pady=(12,2))
            tk.Frame(right, bg=self._brd(), height=1).pack(fill="x", padx=8, pady=(0,4))

        def info_label(text):
            return tk.Label(right, text=text, bg=self._panel(), fg=self._fg(),
                            font=(FONT,9), anchor="w")

        section("FILE INFO")
        info_frame = tk.Frame(right, bg=self._panel(),
                               highlightbackground=self._brd(), highlightthickness=1)
        info_frame.pack(fill="x", padx=8, pady=2)
        self.info_lines  = tk.Label(info_frame, text="Lines: 1", bg=self._panel(),
                                     fg=self._fg(), font=(FONT,9), anchor="w")
        self.info_lines.pack(fill="x", padx=8, pady=2)
        self.info_chars  = tk.Label(info_frame, text="Chars: 0", bg=self._panel(),
                                     fg=self._fg(), font=(FONT,9), anchor="w")
        self.info_chars.pack(fill="x", padx=8, pady=2)
        self.info_cursor = tk.Label(info_frame, text="Ln 1, Col 1", bg=self._panel(),
                                     fg=self._sfg(), font=(FONT,9), anchor="w")
        self.info_cursor.pack(fill="x", padx=8, pady=(2,6))

        section("QUICK ACTIONS")
        for text, cmd in [
            ("▶  Run Script",           self._run_script),
            ("🔨  Compile to EXE",       self._compile_exe),
            ("💾  Save",                 self._save_file),
            ("📦  Install Package",      self._pkg_install),
            ("🎨  Package Creator",      self._open_pkg_creator),
            ("📋  Copy All",             self._copy_all),
            ("🗑️  Clear Editor",         self._clear_editor),
            ("🌐  Open Docs",            lambda: __import__('webbrowser').open(
                                             "https://netchcodelang.github.io/netchcodinglang/docs.html")),
        ]:
            tk.Button(right, text=text, command=cmd,
                      bg=self._panel(), fg=self._fg(), font=(FONT,9),
                      relief="flat", bd=0, padx=8, pady=5,
                      cursor="hand2", anchor="w", width=24,
                      activebackground=self._brd(),
                      activeforeground=ACCENT).pack(fill="x", padx=8, pady=2)

        section("INTERPRETER")
        st_col  = SUCCESS if self.interpreter else ERROR
        st_text = "✅ Found" if self.interpreter else "❌ Not found"
        tk.Label(right, text=st_text, bg=self._side(), fg=st_col,
                 font=(FONT,9)).pack(anchor="w", padx=10)
        if self.compiler:
            tk.Label(right, text="🔨 Compiler ready", bg=self._side(),
                     fg=SUCCESS, font=(FONT,9)).pack(anchor="w", padx=10)

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=ACCENT2, height=22)
        bar.pack(fill="x", side="bottom"); bar.pack_propagate(False)
        self.status_var = tk.StringVar(value="Ready — Netch Builder 2")
        tk.Label(bar, textvariable=self.status_var,
                 bg=ACCENT2, fg="white", font=(FONT,8)).pack(side="left", padx=10)
        tk.Label(bar, text="reddit.com/r/netchcoding2  •  github.com/netchcodelang/netchcodinglang",
                 bg=ACCENT2, fg="#c0b8ff", font=(FONT,8)).pack(side="right", padx=10)

    # ── SYNTAX HIGHLIGHTING ─────────────────────
    def _setup_highlight(self):
        self.editor.tag_config("kw",  foreground="#c792ea")
        self.editor.tag_config("bi",  foreground="#82aaff")
        self.editor.tag_config("str", foreground="#c3e88d")
        self.editor.tag_config("cmt", foreground="#546e7a")
        self.editor.tag_config("num", foreground="#f78c6c")
        self.editor.tag_config("op",  foreground="#89ddff")
        self.editor.tag_config("hdr", foreground=ACCENT, font=(CODE,11,"bold"))

    def _highlight(self, event=None):
        for tag in ("kw","bi","str","cmt","num","op","hdr"):
            self.editor.tag_remove(tag,"1.0","end")
        content = self.editor.get("1.0","end")
        for ln, line in enumerate(content.split("\n"), 1):
            if line.strip() == "<using.ntch>":
                self.editor.tag_add("hdr",f"{ln}.0",f"{ln}.end"); continue
            for m in re.finditer(r'#.*$', line):
                self.editor.tag_add("cmt",f"{ln}.{m.start()}",f"{ln}.{m.end()}")
            for m in re.finditer(r'"[^"]*"', line):
                self.editor.tag_add("str",f"{ln}.{m.start()}",f"{ln}.{m.end()}")
            for m in re.finditer(r'\b\d+\.?\d*\b', line):
                self.editor.tag_add("num",f"{ln}.{m.start()}",f"{ln}.{m.end()}")
            for kw in KEYWORDS:
                for m in re.finditer(r'\b'+re.escape(kw)+r'\b', line):
                    self.editor.tag_add("kw",f"{ln}.{m.start()}",f"{ln}.{m.end()}")
            for bi in BUILTINS:
                for m in re.finditer(re.escape(bi), line):
                    self.editor.tag_add("bi",f"{ln}.{m.start()}",f"{ln}.{m.end()}")

    def _sync_lines(self, event=None):
        self.line_nums.config(state="normal")
        self.line_nums.delete("1.0","end")
        n = int(self.editor.index("end-1c").split(".")[0])
        self.line_nums.insert("1.0", "\n".join(str(i) for i in range(1,n+1)))
        self.line_nums.config(state="disabled")
        self.line_nums.yview_moveto(self.editor.yview()[0])

    def _on_key(self, e=None):
        self.unsaved = True
        self._update_title()
        content = self.editor.get("1.0","end-1c")
        self.info_lines.config(text=f"Lines: {content.count(chr(10))+1}")
        self.info_chars.config(text=f"Chars: {len(content)}")
        try:
            p = self.editor.index("insert").split(".")
            self.info_cursor.config(text=f"Ln {p[0]}, Col {int(p[1])+1}")
        except: pass
        self._sync_lines()
        self.root.after(80, self._highlight)

    def _auto_indent(self, e=None):
        pos  = self.editor.index("insert")
        ln   = int(pos.split(".")[0])
        curr = self.editor.get(f"{ln}.0",f"{ln}.end")
        ind  = len(curr)-len(curr.lstrip())
        endscolon = curr.rstrip().endswith(":")
        blockkw   = any(curr.strip().startswith(k) for k in
                        ["if ","else","while ","repeat ","function ","for ","foreach "])
        if endscolon or blockkw: ind += 4
        self.editor.insert("insert","\n"+" "*ind)
        return "break"

    def _tab(self, e=None):
        self.editor.insert("insert","    "); return "break"

    # ── FILE OPS ───────────────────────────────
    def _new_file(self):
        if self.unsaved and not messagebox.askyesno("Unsaved","Discard unsaved changes?"): return
        self.editor.delete("1.0","end")
        self.editor.insert("1.0","<using.ntch>\n\nprint(\"Hello from Netch 2!\")\n")
        self.current_file = None; self.unsaved = False
        self._update_title(); self._highlight(); self._sync_lines()

    def _open_file(self):
        p = filedialog.askopenfilename(
            title="Open Netch Script",
            filetypes=[("Netch 2","*.ntch"),("All","*.*")])
        if not p: return
        with open(p,"r",encoding="utf-8") as f: content=f.read()
        self.editor.delete("1.0","end")
        self.editor.insert("1.0",content)
        self.current_file=p; self.unsaved=False
        self._update_title(); self._highlight(); self._sync_lines()
        self._log(f"Opened: {p}","info")

    def _save_file(self):
        if not self.current_file: self._save_as(); return
        with open(self.current_file,"w",encoding="utf-8") as f:
            f.write(self.editor.get("1.0","end-1c"))
        self.unsaved=False; self._update_title()
        self._log(f"Saved: {self.current_file}","success")
        self.status_var.set(f"Saved — {os.path.basename(self.current_file)}")

    def _save_as(self):
        p = filedialog.asksaveasfilename(
            title="Save Netch Script",
            defaultextension=".ntch",
            filetypes=[("Netch 2","*.ntch"),("All","*.*")])
        if not p: return
        self.current_file=p; self._save_file()

    def _update_title(self):
        name = os.path.basename(self.current_file) if self.current_file else "untitled.ntch"
        mark = " •" if self.unsaved else ""
        self.root.title(f"Netch Builder 2 — {name}{mark}  |  An Aerotion Production")
        self.title_lbl.config(text=f" {name}{mark}")
        self.tab_lbl.config(text=f"  {name}{mark}  ")

    # ── RUN ────────────────────────────────────
    def _run_script(self):
        if not self.interpreter:
            self._log("interpreter.py not found!","error"); return
        if self.current_file and not self.unsaved:
            run_path = self.current_file
        else:
            tmp = tempfile.NamedTemporaryFile(suffix=".ntch",delete=False,
                                              mode="w",encoding="utf-8")
            tmp.write(self.editor.get("1.0","end-1c")); tmp.close()
            run_path = tmp.name
        self._log("▶ Running...","info")
        self.status_var.set("Running...")

        def _run():
            try:
                self._proc = subprocess.Popen(
                    [sys.executable, self.interpreter, run_path],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace")
                for line in self._proc.stdout:
                    self.root.after(0, lambda l=line.rstrip(): self._log(l))
                self._proc.wait()
                code = self._proc.returncode
                msg  = "✅ Done" if code==0 else f"❌ Exited ({code})"
                tag  = "success" if code==0 else "error"
                self.root.after(0, lambda: self._log(msg, tag))
                self.root.after(0, lambda: self.status_var.set(msg))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"Error: {e}","error"))

        threading.Thread(target=_run, daemon=True).start()

    def _stop_script(self):
        if self._proc:
            self._proc.terminate()
            self._log("⏹ Stopped","warn")
            self.status_var.set("Stopped")

    # ── COMPILE ────────────────────────────────
    def _compile_exe(self):
        if not self.compiler:
            messagebox.showerror("Compiler not found",
                "netch_compile.py not found.\nPlace it in ~/Netch2/ or same folder as Netch Builder.")
            return
        if not self.current_file:
            if not messagebox.askyesno("Save first","Save the file before compiling?"):
                return
            self._save_as()
            if not self.current_file: return
        else:
            self._save_file()

        self._log("🔨 Compiling to EXE...","info")
        self.status_var.set("Compiling...")

        def _compile():
            try:
                result = subprocess.run(
                    [sys.executable, self.compiler, self.current_file],
                    capture_output=True, text=True, encoding="utf-8")
                for line in result.stdout.split("\n"):
                    if line.strip():
                        self.root.after(0, lambda l=line: self._log(l))
                if result.returncode == 0:
                    self.root.after(0, lambda: self.status_var.set("✅ Compiled!"))
                else:
                    self.root.after(0, lambda: self._log("Compile failed","error"))
                    self.root.after(0, lambda: self.status_var.set("❌ Compile failed"))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"Error: {e}","error"))

        threading.Thread(target=_compile, daemon=True).start()

    # ── PACKAGES ───────────────────────────────
    def _pkg_install(self):
        name = tk.simpledialog_or_input(self.root, "Install Package",
            "Package name (e.g. customwindowtitle):") if False else self._ask("Install Package","Package name:")
        if not name: return
        netch_dir = os.path.join(os.path.expanduser("~"),"Netch2")
        pkg_script= os.path.join(netch_dir,"netch_pkg.py")
        if not os.path.exists(pkg_script):
            messagebox.showerror("Error","netch_pkg.py not found in ~/Netch2/"); return
        self._log(f"Installing {name}...","info")
        def _install():
            r = subprocess.run([sys.executable,pkg_script,"install",name],
                               capture_output=True,text=True)
            for line in r.stdout.split("\n"):
                if line.strip(): self.root.after(0, lambda l=line: self._log(l))
        threading.Thread(target=_install, daemon=True).start()

    def _ask(self, title, prompt):
        from tkinter import simpledialog
        return simpledialog.askstring(title, prompt, parent=self.root)

    def _pkg_list(self):
        netch_dir = os.path.join(os.path.expanduser("~"),"Netch2")
        pkg_script= os.path.join(netch_dir,"netch_pkg.py")
        if not os.path.exists(pkg_script): return
        r = subprocess.run([sys.executable,pkg_script,"list"],capture_output=True,text=True)
        self._log(r.stdout.strip())

    def _pkg_update(self):
        netch_dir = os.path.join(os.path.expanduser("~"),"Netch2")
        pkg_script= os.path.join(netch_dir,"netch_pkg.py")
        if not os.path.exists(pkg_script): return
        self._log("Checking for package updates...","info")
        def _upd():
            r = subprocess.run([sys.executable,pkg_script,"update"],capture_output=True,text=True)
            for line in r.stdout.split("\n"):
                if line.strip(): self.root.after(0, lambda l=line: self._log(l))
        threading.Thread(target=_upd, daemon=True).start()

    def _open_pkg_creator(self):
        netch_dir = os.path.join(os.path.expanduser("~"),"Netch2")
        creator   = os.path.join(netch_dir,"netch_package_creator.py")
        if not os.path.exists(creator):
            creator = os.path.join(os.path.dirname(__file__),"netch_package_creator.py")
        if os.path.exists(creator):
            subprocess.Popen([sys.executable,creator])
        else:
            messagebox.showerror("Not found","netch_package_creator.py not found.")

    # ── THEME ──────────────────────────────────
    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        messagebox.showinfo("Theme changed",
            "Restart Netch Builder to apply the theme change.")

    def _change_font(self, delta):
        curr = self.editor.cget("font")
        try:
            parts = str(curr).split()
            size  = int(parts[1]) + delta if len(parts)>1 else 11+delta
            size  = max(8, min(24, size))
            self.editor.config(font=(CODE, size))
            self.line_nums.config(font=(CODE, size))
        except: pass

    # ── UTILS ──────────────────────────────────
    def _insert(self, code):
        pos  = self.editor.index("insert")
        ln   = int(pos.split(".")[0])
        curr = self.editor.get(f"{ln}.0",f"{ln}.end").strip()
        self.editor.insert("insert", ("\n" if curr else "") + code + "\n")
        self._on_key()

    def _log(self, msg, tag=None):
        self.console.config(state="normal")
        if tag: self.console.insert("end", msg+"\n", tag)
        else:   self.console.insert("end", msg+"\n")
        self.console.see("end")
        self.console.config(state="disabled")

    def _clear_console(self):
        self.console.config(state="normal")
        self.console.delete("1.0","end")
        self.console.config(state="disabled")

    def _copy_all(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.editor.get("1.0","end-1c"))
        self.status_var.set("Copied!")

    def _clear_editor(self):
        if messagebox.askyesno("Clear","Clear all code?"):
            self.editor.delete("1.0","end"); self._on_key()

    def _on_close(self):
        if self.unsaved and not messagebox.askyesno("Quit","You have unsaved changes. Quit anyway?"): return
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    NetchBuilder(root)
    root.mainloop()
