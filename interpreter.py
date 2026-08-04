import sys, os, re, urllib.request, urllib.parse, json, subprocess, threading

# ─────────────────────────────────────────────
#  VERSION & AUTO-UPDATER
# ─────────────────────────────────────────────

NETCH_VERSION = "2.1.0"
GITHUB_API = "https://api.github.com/repos/netchcodelang/netchcodinglang/releases/latest"

def check_for_updates():
    try:
        req = urllib.request.Request(GITHUB_API, headers={"User-Agent": "netch2"})
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.loads(r.read())
            latest = data.get("tag_name","").lstrip("v")
            if latest and latest != NETCH_VERSION:
                print(f"[Netch] Update available: v{latest} (you have v{NETCH_VERSION})")
                print("[Netch] Download: https://github.com/netchcodelang/netchcodinglang")
    except: pass

# ─────────────────────────────────────────────
#  NETCH 1 DETECTOR
# ─────────────────────────────────────────────

NETCH1_PATTERNS = [
    (r'<using\.netch>',  "Use <using.ntch> instead of <using.netch>"),
    (r'\badd\.button\b', "add.button → button(\"label\") action ..."),
    (r'\bdisplay\.text\b',"display.text → displaytext(\"text\")"),
    (r'\bopen\.file\b',  "open.file → openfile(\"path\")"),
    (r'run on click',    "\"run on click\" → button(\"label\") action ..."),
]

def detect_netch1(source):
    return [msg for pat, msg in NETCH1_PATTERNS if re.search(pat, source)]

# ─────────────────────────────────────────────
#  ERRORS
# ─────────────────────────────────────────────

class NetchError(Exception):
    def __init__(self, message, line_num=None, line_text=None, fix=None):
        self.message   = message
        self.line_num  = line_num
        self.line_text = line_text
        self.fix       = fix
        super().__init__(message)

def print_error(e, line_num=None, line_text=None):
    print("\n" + "━"*52)
    print("  ❌  Netch Error")
    if line_num:
        print(f"  📍  Line {line_num}: {(line_text or '').strip()}")
    print(f"  💬  {e.message if isinstance(e, NetchError) else str(e)}")
    if isinstance(e, NetchError) and e.fix:
        print(f"  🔧  Fix: {e.fix}")
    print("━"*52 + "\n")

# ─────────────────────────────────────────────
#  TKINTER
# ─────────────────────────────────────────────

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from tkinter import scrolledtext
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False

# ─────────────────────────────────────────────
#  STATE
# ─────────────────────────────────────────────

class NetchState:
    def __init__(self):
        self.variables      = {}
        self.functions      = {}
        self.window         = None
        self.widgets        = {}
        self.button_actions = {}
        self.window_title   = "Netch App"
        self.window_width   = 800
        self.window_height  = 600
        self.theme_color    = "#ffffff"
        self.text_color     = "#000000"
        self.font_name      = "Segoe UI"
        self.font_size      = 12
        self.dark_mode      = False
        self.current_line   = 0
        self.current_line_text = ""

state = NetchState()

DARK_BG   = "#1e1e1e"
DARK_FG   = "#e0e0e0"
DARK_BTN  = "#2d2d2d"
DARK_ENTRY= "#2b2b2b"
DARK_BORDER="#444444"

def theme_bg():  return DARK_BG  if state.dark_mode else state.theme_color
def theme_fg():  return DARK_FG  if state.dark_mode else state.text_color
def theme_btn(): return DARK_BTN if state.dark_mode else "#0078d4"
def theme_entry():return DARK_ENTRY if state.dark_mode else "#ffffff"

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def resolve(value):
    if isinstance(value, str):
        if value in state.variables: return state.variables[value]
        if value.startswith('"') and value.endswith('"'): return value[1:-1]
        if value == 'true':  return True
        if value == 'false': return False
        try: return int(value)
        except: pass
        try: return float(value)
        except: pass
    return value

def ensure_window():
    if not TK_AVAILABLE:
        raise NetchError("Tkinter not found.",
            fix="Reinstall Python from python.org and check 'tcl/tk' during setup.")
    if state.window is None:
        state.window = tk.Tk()
        state.window.title(state.window_title)
        state.window.geometry(f"{state.window_width}x{state.window_height}")
        state.window.configure(bg=theme_bg())

def make_font(size=None, bold=False):
    return (state.font_name, size or state.font_size, 'bold' if bold else 'normal')

def parse_color_arg(args, idx, default):
    """Get color arg, or None if it looks like a keyword (not a color)."""
    if len(args) > idx:
        v = str(args[idx])
        if v.startswith('#') or v in ('red','green','blue','white','black',
            'gray','grey','yellow','orange','purple','pink','cyan','transparent'):
            return v
    return default

# ─────────────────────────────────────────────
#  TOKENIZER
# ─────────────────────────────────────────────

TOKEN_PATTERNS = [
    ('HEADER',     r'<using\.ntch>'),
    ('STRING_LIT', r'"[^"]*"'),
    ('FLOAT',      r'\d+\.\d+'),
    ('INT',        r'\d+'),
    ('BOOL',       r'\b(true|false)\b'),
    ('IDENT',      r'[a-zA-Z_][a-zA-Z0-9_.]*'),
    ('LPAREN',     r'\('),
    ('RPAREN',     r'\)'),
    ('COMMA',      r','),
    ('PLUS',       r'\+'),
    ('MINUS',      r'-'),
    ('STAR',       r'\*'),
    ('SLASH',      r'/'),
    ('EEQ',        r'=='),
    ('NEQ',        r'!='),
    ('LTE',        r'<='),
    ('GTE',        r'>='),
    ('LT',         r'<'),
    ('GT',         r'>'),
    ('ASSIGN',     r'='),
    ('SKIP',       r'[ \t]+'),
    ('COMMENT',    r'#[^\n]*'),
]

def tokenize(code):
    tokens, pos = [], 0
    while pos < len(code):
        matched = False
        for tt, pat in TOKEN_PATTERNS:
            m = re.match(pat, code[pos:])
            if m:
                if tt not in ('SKIP','COMMENT'):
                    tokens.append((tt, m.group()))
                pos += m.end(); matched = True; break
        if not matched: pos += 1
    return tokens

def parse_args(tokens, pos):
    args = []
    if pos < len(tokens) and tokens[pos][0] == 'LPAREN':
        pos += 1; depth = 1; current = []
        while pos < len(tokens) and depth > 0:
            t, v = tokens[pos]
            if   t == 'LPAREN': depth += 1; current.append((t,v))
            elif t == 'RPAREN':
                depth -= 1
                if depth > 0: current.append((t,v))
            elif t == 'COMMA' and depth == 1:
                if current:
                    val, _ = eval_expr(current, 0); args.append(val)
                current = []
            else: current.append((t,v))
            pos += 1
        if current:
            val, _ = eval_expr(current, 0); args.append(val)
    return args, pos

def eval_expr(tokens, pos):
    left, pos = eval_atom(tokens, pos)
    while pos < len(tokens) and tokens[pos][0] in (
            'PLUS','MINUS','STAR','SLASH','EEQ','NEQ','LT','GT','LTE','GTE'):
        op = tokens[pos][0]; pos += 1
        right, pos = eval_atom(tokens, pos)
        left = apply_op(op, left, right)
    return left, pos

def eval_atom(tokens, pos):
    if pos >= len(tokens): return None, pos
    tt, tv = tokens[pos]
    if tt == 'IDENT':
        pos += 1
        if pos < len(tokens) and tokens[pos][0] == 'LPAREN':
            args, pos = parse_args(tokens, pos)
            return call_builtin(tv, args), pos
        return resolve(tv), pos
    if tt == 'STRING_LIT': return tv[1:-1], pos+1
    if tt == 'INT':        return int(tv),  pos+1
    if tt == 'FLOAT':      return float(tv),pos+1
    if tt == 'BOOL':       return tv=='true',pos+1
    return None, pos+1

def apply_op(op, l, r):
    if op=='PLUS':  return str(l)+str(r) if isinstance(l,str) or isinstance(r,str) else l+r
    if op=='MINUS': return l-r
    if op=='STAR':  return l*r
    if op=='SLASH': return (l/r if r else 0)
    if op=='EEQ':   return l==r
    if op=='NEQ':   return l!=r
    if op=='LT':    return l<r
    if op=='GT':    return l>r
    if op=='LTE':   return l<=r
    if op=='GTE':   return l>=r

# ─────────────────────────────────────────────
#  BUILT-INS
# ─────────────────────────────────────────────

def call_builtin(name, args):
    s = state

    # ── dark mode ──
    if name == 'dark':
        s.dark_mode = bool(args[0]) if args else True
        if s.window:
            s.window.configure(bg=theme_bg())
        return None

    # ── window ──
    if name == 'window':      ensure_window(); return None
    if name == 'window.title':
        s.window_title = str(args[0]) if args else ''
        if s.window: s.window.title(s.window_title)
        return None
    if name == 'window.size':
        if len(args)>=2:
            s.window_width=int(args[0]); s.window_height=int(args[1])
            if s.window: s.window.geometry(f"{s.window_width}x{s.window_height}")
        return None
    if name == 'window.theme':
        s.theme_color = str(args[0]) if args else '#fff'
        if s.window: s.window.configure(bg=theme_bg())
        return None

    # ── label / displaytext ──
    if name in ('label','displaytext'):
        ensure_window()
        text  = str(args[0]) if args else ''
        color = parse_color_arg(args, 1, theme_fg())
        size  = int(args[2]) if len(args)>2 and isinstance(args[2],(int,float)) else s.font_size
        lbl = tk.Label(s.window, text=text, bg=theme_bg(), fg=color,
                       font=make_font(size))
        lbl.pack(pady=4, padx=10, anchor='w')
        return None

    # ── button ──
    # supports: button("label"), button("label", bg, fg), cr.button("label")
    if name in ('button', 'cr.button'):
        ensure_window()
        label  = str(args[0]) if args else 'Button'
        bg     = parse_color_arg(args, 1, theme_btn())
        fg     = parse_color_arg(args, 2, 'white')
        radius = (name == 'cr.button')  # rounded corners flag
        if TK_AVAILABLE:
            if radius:
                # rounded button using canvas trick
                btn = tk.Button(s.window, text=label, bg=bg, fg=fg,
                                font=make_font(), relief='flat',
                                padx=14, pady=7, cursor='hand2',
                                bd=0, highlightthickness=0,
                                activebackground=bg, activeforeground=fg)
                btn.configure(overrelief='flat')
            else:
                btn = tk.Button(s.window, text=label, bg=bg, fg=fg,
                                font=make_font(), relief='flat',
                                padx=12, pady=6, cursor='hand2',
                                activebackground=bg, activeforeground=fg)
            btn.pack(pady=4, padx=10, anchor='w')
            s.widgets[label] = btn
        return None

    # ── textbox ──
    if name == 'textbox':
        ensure_window()
        key   = str(args[0]) if args else 'textbox'
        width = int(args[1]) if len(args)>1 else 30
        placeholder = str(args[2]) if len(args)>2 else ''
        entry = tk.Entry(s.window, font=make_font(), width=width,
                         bg=theme_entry(), fg=theme_fg(),
                         insertbackground=theme_fg(),
                         relief='solid', bd=1)
        if placeholder:
            entry.insert(0, placeholder)
            entry.bind('<FocusIn>',  lambda e, en=entry, ph=placeholder:
                       en.delete(0,'end') if en.get()==ph else None)
        entry.pack(pady=4, padx=10, anchor='w')
        s.widgets[key] = entry
        return None

    # ── passwordbox ──
    if name == 'passwordbox':
        ensure_window()
        key   = str(args[0]) if args else 'password'
        width = int(args[1]) if len(args)>1 else 30
        entry = tk.Entry(s.window, font=make_font(), width=width,
                         show='*', bg=theme_entry(), fg=theme_fg(),
                         insertbackground=theme_fg(), relief='solid', bd=1)
        entry.pack(pady=4, padx=10, anchor='w')
        s.widgets[key] = entry
        return None

    # ── getinput ──
    if name == 'getinput':
        key = str(args[0]) if args else ''
        w = s.widgets.get(key)
        return w.get() if w and hasattr(w,'get') else ''

    # ── image ──
    if name == 'image':
        ensure_window()
        path = str(args[0]) if args else ''
        try:
            img = tk.PhotoImage(file=path)
            lbl = tk.Label(s.window, image=img, bg=theme_bg())
            lbl.image = img
            lbl.pack(pady=4, padx=10)
        except Exception:
            raise NetchError(f"Could not load image: {path}",
                fix="Make sure the path is correct. Netch supports .png and .gif images.")
        return None

    # ── progressbar ──
    if name == 'progressbar':
        ensure_window()
        key   = str(args[0]) if args else 'progress'
        value = int(args[1]) if len(args)>1 else 0
        bar   = ttk.Progressbar(s.window, length=300, mode='determinate')
        bar['value'] = value
        bar.pack(pady=4, padx=10, anchor='w')
        s.widgets[key] = bar
        return None

    if name == 'setprogress':
        key   = str(args[0]) if args else 'progress'
        value = int(args[1]) if len(args)>1 else 0
        w = s.widgets.get(key)
        if w: w['value'] = value
        return None

    # ── checkbox ──
    if name == 'checkbox':
        ensure_window()
        key   = str(args[0]) if args else 'check'
        label = str(args[1]) if len(args)>1 else key
        var   = tk.BooleanVar()
        cb    = tk.Checkbutton(s.window, text=label, variable=var,
                               bg=theme_bg(), fg=theme_fg(), font=make_font(),
                               selectcolor=theme_entry(),
                               activebackground=theme_bg())
        cb.pack(pady=4, padx=10, anchor='w')
        s.widgets[key] = var
        return None

    if name == 'getchecked':
        key = str(args[0]) if args else ''
        w = s.widgets.get(key)
        return bool(w.get()) if w else False

    # ── radiobutton ──
    if name == 'radiobutton':
        ensure_window()
        group = str(args[0]) if args else 'radio'
        label = str(args[1]) if len(args)>1 else 'Option'
        value = str(args[2]) if len(args)>2 else label
        if group not in s.widgets: s.widgets[group] = tk.StringVar()
        rb = tk.Radiobutton(s.window, text=label, variable=s.widgets[group],
                            value=value, bg=theme_bg(), fg=theme_fg(),
                            font=make_font(), activebackground=theme_bg(),
                            selectcolor=theme_entry())
        rb.pack(pady=2, padx=10, anchor='w')
        return None

    if name == 'getradio':
        key = str(args[0]) if args else ''
        w = s.widgets.get(key)
        return w.get() if w else ''

    # ── dropdown ──
    if name == 'dropdown':
        ensure_window()
        key     = str(args[0]) if args else 'dropdown'
        options = [str(a) for a in args[1:]] if len(args)>1 else ['Option 1']
        var     = tk.StringVar(value=options[0])
        dd      = ttk.Combobox(s.window, textvariable=var, values=options,
                               font=make_font(), state='readonly', width=20)
        dd.pack(pady=4, padx=10, anchor='w')
        s.widgets[key] = var
        return None

    if name == 'getdropdown':
        key = str(args[0]) if args else ''
        w = s.widgets.get(key)
        return w.get() if w else ''

    # ── slider ──
    if name == 'slider':
        ensure_window()
        key = str(args[0]) if args else 'slider'
        mn  = int(args[1]) if len(args)>1 else 0
        mx  = int(args[2]) if len(args)>2 else 100
        var = tk.IntVar(value=mn)
        sl  = tk.Scale(s.window, from_=mn, to=mx, orient='horizontal',
                       variable=var, bg=theme_bg(), fg=theme_fg(),
                       troughcolor=theme_entry(), font=make_font(9))
        sl.pack(pady=4, padx=10, anchor='w')
        s.widgets[key] = var
        return None

    if name == 'getslider':
        key = str(args[0]) if args else ''
        w = s.widgets.get(key)
        return w.get() if w else 0

    # ── listbox ──
    if name == 'listbox':
        ensure_window()
        key   = str(args[0]) if args else 'list'
        items = [str(a) for a in args[1:]]
        lb    = tk.Listbox(s.window, font=make_font(), relief='solid', bd=1,
                           height=6, width=30,
                           bg=theme_entry(), fg=theme_fg(),
                           selectbackground='#0078d4')
        for item in items: lb.insert(tk.END, item)
        lb.pack(pady=4, padx=10, anchor='w')
        s.widgets[key] = lb
        return None

    if name == 'getlist':
        key = str(args[0]) if args else ''
        w = s.widgets.get(key)
        if w:
            sel = w.curselection()
            return w.get(sel[0]) if sel else ''
        return ''

    # ── tabcontrol ──
    if name == 'tabcontrol':
        ensure_window()
        key = str(args[0]) if args else 'tabs'
        nb  = ttk.Notebook(s.window)
        nb.pack(fill='both', expand=True, padx=10, pady=4)
        s.widgets[key] = nb
        return None

    if name == 'addtab':
        key   = str(args[0]) if args else 'tabs'
        title = str(args[1]) if len(args)>1 else 'Tab'
        nb    = s.widgets.get(key)
        if nb:
            frame = tk.Frame(nb, bg=theme_bg())
            nb.add(frame, text=title)
        return None

    # ── display.webpage ──
    if name == 'display.webpage':
        ensure_window()
        url = str(args[0]) if args else ''
        width  = int(args[1]) if len(args)>1 else s.window_width - 20
        height = int(args[2]) if len(args)>2 else s.window_height - 60
        try:
            import tkinter.scrolledtext as st_mod
            # try cef or webview first, fall back to basic frame
            try:
                import webview
                def _open():
                    webview.create_window(s.window_title or 'Netch', url,
                                          width=width, height=height)
                    webview.start()
                threading.Thread(target=_open, daemon=True).start()
            except ImportError:
                # fallback — open in default browser with a label
                import webbrowser
                webbrowser.open(url)
                lbl = tk.Label(s.window,
                               text=f"🌐 Opened in browser: {url}",
                               bg=theme_bg(), fg='#0078d4',
                               font=make_font(), cursor='hand2')
                lbl.pack(pady=10, padx=10)
                lbl.bind('<Button-1>', lambda e: webbrowser.open(url))
        except Exception as ex:
            raise NetchError(f"display.webpage failed: {ex}",
                fix='Make sure the URL is correct. Example: display.webpage("https://example.com")')
        return None

    # ── sound ──
    if name == 'sound.play':
        path = str(args[0]) if args else ''
        try:
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except ImportError:
            os.system(f'start /min "" "{path}"')
        except Exception:
            raise NetchError(f"Could not play sound: {path}",
                fix="Make sure the file exists and is a .wav file.")
        return None

    if name == 'sound.stop':
        try:
            import winsound; winsound.PlaySound(None, winsound.SND_PURGE)
        except: pass
        return None

    # ── file ops ──
    if name == 'openfile':
        path = str(args[0]) if args else ''
        if path:
            try: os.startfile(path)
            except: raise NetchError(f"Could not open: {path}",
                        fix="Check the path is correct and the file exists.")
        elif TK_AVAILABLE:
            path = filedialog.askopenfilename()
        return path

    if name == 'deletefile':
        path = str(args[0]) if args else ''
        if not os.path.exists(path):
            raise NetchError(f"File not found: {path}", fix="Check the file path.")
        os.remove(path); return None

    if name == 'copyfile':
        import shutil
        if len(args)<2:
            raise NetchError("copyfile() needs 2 args: source and destination",
                fix='Example: copyfile("C:/source.txt", "C:/dest.txt")')
        shutil.copy(str(args[0]), str(args[1])); return None

    # ── internet — download ──
    if name == 'download.file':
        if len(args)<2:
            raise NetchError("download.file() needs a URL and save path",
                fix='Example: download.file("https://example.com/file.txt", "C:/file.txt")')
        url  = str(args[0])
        dest = str(args[1])
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"[Netch] Downloaded: {dest}")
        except Exception as ex:
            raise NetchError(f"Download failed: {ex}",
                fix="Check the URL is correct and you have internet access.")
        return dest

    # ── internet — send / post to server ──
    if name == 'send.post':
        # send.post("url", key, value, key, value, ...)
        if not args:
            raise NetchError("send.post() needs a URL",
                fix='Example: send.post("https://myserver.com/api", "name", getinput("namebox"))')
        url  = str(args[0])
        data = {}
        i = 1
        while i+1 < len(args):
            data[str(args[i])] = str(args[i+1]); i += 2
        try:
            payload = urllib.parse.urlencode(data).encode()
            req = urllib.request.Request(url, data=payload, method='POST')
            req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req, timeout=10) as r:
                resp = r.read().decode()
                s.variables['last.response'] = resp
                print(f"[Netch] Server replied: {resp[:200]}")
                return resp
        except Exception as ex:
            raise NetchError(f"send.post failed: {ex}",
                fix="Check the server URL is correct and reachable.")

    # ── internet — send JSON ──
    if name == 'send.json':
        if not args:
            raise NetchError("send.json() needs a URL",
                fix='Example: send.json("https://myserver.com/api", "key", "value")')
        url  = str(args[0])
        data = {}
        i = 1
        while i+1 < len(args):
            data[str(args[i])] = str(args[i+1]); i += 2
        try:
            payload = json.dumps(data).encode()
            req = urllib.request.Request(url, data=payload, method='POST')
            req.add_header('Content-Type','application/json')
            with urllib.request.urlopen(req, timeout=10) as r:
                resp = r.read().decode()
                s.variables['last.response'] = resp
                print(f"[Netch] Server replied: {resp[:200]}")
                return resp
        except Exception as ex:
            raise NetchError(f"send.json failed: {ex}",
                fix="Check the URL is correct and your internet is working.")

    # ── internet — get request ──
    if name == 'get.request':
        if not args:
            raise NetchError("get.request() needs a URL",
                fix='Example: get.request("https://api.example.com/data")')
        url = str(args[0])
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"netch2"})
            with urllib.request.urlopen(req, timeout=10) as r:
                resp = r.read().decode()
                s.variables['last.response'] = resp
                return resp
        except Exception as ex:
            raise NetchError(f"get.request failed: {ex}",
                fix="Check the URL is correct and you have internet access.")

    # ── connect to websocket server ──
    if name == 'connect.server':
        if not args:
            raise NetchError("connect.server() needs a URL",
                fix='Example: connect.server("ws://myserver.com:8080")')
        url = str(args[0])
        try:
            import websocket
            def on_message(ws, msg):
                s.variables['last.message'] = msg
                print(f"[Netch Server] {msg}")
            def on_error(ws, err):
                print(f"[Netch Server Error] {err}")
            def on_open(ws):
                s.variables['ws_connection'] = ws
                print(f"[Netch] Connected to {url}")
            ws = websocket.WebSocketApp(url,
                on_message=on_message, on_error=on_error, on_open=on_open)
            threading.Thread(target=ws.run_forever, daemon=True).start()
            s.widgets['__ws__'] = ws
        except ImportError:
            raise NetchError("websocket-client is not installed.",
                fix="Run this in your terminal: pip install websocket-client")
        return None

    if name == 'send.message':
        msg = str(args[0]) if args else ''
        ws = s.widgets.get('__ws__')
        if ws: ws.send(msg)
        else:  raise NetchError("No server connected.",
                    fix="Use connect.server() first before send.message()")
        return None

    # ── send textbox to server (shortcut) ──
    if name == 'send.textbox':
        # send.textbox("boxname", "serverurl", "fieldname")
        if len(args) < 2:
            raise NetchError("send.textbox() needs: box name and server URL",
                fix='Example: send.textbox("msgbox", "https://myserver.com/api", "message")')
        box_key    = str(args[0])
        url        = str(args[1])
        field_name = str(args[2]) if len(args)>2 else 'message'
        w = s.widgets.get(box_key)
        text = w.get() if w and hasattr(w,'get') else ''
        try:
            payload = urllib.parse.urlencode({field_name: text}).encode()
            req = urllib.request.Request(url, data=payload, method='POST')
            req.add_header('Content-Type','application/x-www-form-urlencoded')
            with urllib.request.urlopen(req, timeout=10) as r:
                resp = r.read().decode()
                s.variables['last.response'] = resp
                print(f"[Netch] Sent! Server replied: {resp[:200]}")
                return resp
        except Exception as ex:
            raise NetchError(f"send.textbox failed: {ex}",
                fix="Check the server URL is correct and reachable.")

    # ── run bat / shell command ──
    if name == 'run.bat':
        cmd = str(args[0]) if args else ''
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            out = result.stdout.strip()
            if out: print(f"[bat] {out}")
            s.variables['bat.output'] = out
            s.variables['bat.exit']   = result.returncode
            return out
        except Exception as ex:
            raise NetchError(f"run.bat failed: {ex}",
                fix='Example: run.bat("echo Hello")\nOr a .bat file: run.bat("C:/myscript.bat")')

    if name == 'run.shell':
        cmd = str(args[0]) if args else ''
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            out = result.stdout.strip()
            if out: print(f"[shell] {out}")
            s.variables['shell.output'] = out
            return out
        except Exception as ex:
            raise NetchError(f"run.shell failed: {ex}",
                fix='Example: run.shell("dir") or run.shell("python myscript.py")')

    # ── print ──
    if name == 'print':
        print(str(args[0]) if args else ''); return None

    # ── math / util ──
    if name == 'random':
        import random
        return random.randint(int(args[0] if args else 0),
                              int(args[1] if len(args)>1 else 100))
    if name == 'number':   return float(args[0]) if args else 0
    if name == 'upper':    return str(args[0]).upper() if args else ''
    if name == 'lower':    return str(args[0]).lower() if args else ''
    if name == 'contains': return str(args[1]) in str(args[0]) if len(args)>=2 else False
    if name == 'length':   return len(str(args[0])) if args else 0
    if name == 'ask':      return input(str(args[0])+' ' if args else '')
    if name == 'time.now':
        import datetime; return str(datetime.datetime.now())

    # ── user functions ──
    if name in s.functions:
        run_block(s.functions[name]); return None

    raise NetchError(f'Unknown command: {name}()',
        fix=f'Did you spell "{name}" correctly? Check the docs at github.com/netchcodelang/netchcodinglang')

# ─────────────────────────────────────────────
#  LINE RUNNER
# ─────────────────────────────────────────────

def run_block(lines): run_lines(lines)

def run_lines(lines):
    i = 0
    while i < len(lines):
        line    = lines[i]
        stripped= line.strip()
        state.current_line      = i+1
        state.current_line_text = stripped
        try:
            if not stripped or stripped=='<using.ntch>' or stripped.startswith('#'):
                i+=1; continue

            # dark:true / dark:false shorthand
            if stripped in ('dark:true','dark:false'):
                state.dark_mode = (stripped == 'dark:true')
                if state.window: state.window.configure(bg=theme_bg())
                i+=1; continue

            if stripped == 'use window':
                ensure_window(); i+=1; continue

            # function def
            if stripped.startswith('function '):
                fname = stripped[9:].strip()
                body=[]; i+=1
                while i<len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                    body.append(lines[i]); i+=1
                state.functions[fname]=body; continue

            # run()
            m = re.match(r'^run\(([^)]+)\)$', stripped)
            if m:
                fname=m.group(1).strip()
                if fname not in state.functions:
                    raise NetchError(f'run() called "{fname}" which doesn\'t exist.',
                        fix=f'Define it first: function {fname}')
                run_block(state.functions[fname]); i+=1; continue

            # if
            if stripped.startswith('if '):
                cond_part = stripped[3:].strip()
                cm = re.match(r'^button\(["\']?([^"\'")]+)["\']?\)\s+clicked$', cond_part)
                if cm:
                    btn_name=cm.group(1); body=[]; i+=1
                    while i<len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                        body.append(lines[i]); i+=1
                    w=state.widgets.get(btn_name)
                    if w and TK_AVAILABLE and isinstance(w, tk.Button):
                        cap=body[:]; w.config(command=lambda b=cap: run_block(b))
                    continue
                toks=tokenize(cond_part); cond,_=eval_expr(toks,0)
                body=[]; else_body=[]; in_else=False; i+=1
                while i<len(lines):
                    s2=lines[i].strip()
                    if s2=='else': in_else=True; i+=1; continue
                    if lines[i].startswith('    ') or lines[i].startswith('\t'):
                        (else_body if in_else else body).append(lines[i]); i+=1
                    else: break
                if cond: run_block(body)
                else:    run_block(else_body)
                continue

            # while
            if stripped.startswith('while '):
                cond_src=stripped[6:].strip(); body=[]; i+=1
                while i<len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                    body.append(lines[i]); i+=1
                count=0
                while count<100000:
                    toks=tokenize(cond_src); c,_=eval_expr(toks,0)
                    if not c: break
                    run_block(body); count+=1
                if count>=100000:
                    print("[Netch] WARNING: while loop hit 100,000 iterations and was stopped.")
                continue

            # repeat
            if stripped.startswith('repeat '):
                toks=tokenize(stripped[7:].strip()); n,_=eval_expr(toks,0)
                body=[]; i+=1
                while i<len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                    body.append(lines[i]); i+=1
                for _ in range(int(n)): run_block(body)
                continue

            # button with action (regular and cr.)
            bm = re.match(r'^(cr\.)?button\(["\']?([^"\'")]+)["\']?\)\s+action\s+(.+)$', stripped)
            if bm:
                ensure_window()
                rounded = bool(bm.group(1))
                label   = bm.group(2)
                act_src = bm.group(3).strip()
                bg = theme_btn()
                btn = tk.Button(state.window, text=label, bg=bg, fg='white',
                                font=make_font(), relief='flat',
                                padx=(14 if rounded else 12), pady=(7 if rounded else 6),
                                cursor='hand2', bd=0,
                                activebackground=bg, activeforeground='white')
                btn.pack(pady=4, padx=10, anchor='w')
                state.widgets[label]=btn
                def make_cmd(src): return lambda: eval_expr(tokenize(src),0)
                btn.config(command=make_cmd(act_src))
                i+=1; continue

            # assignment
            am = re.match(r'^([a-zA-Z_][a-zA-Z0-9_.]*)\s*=\s*(.+)$', stripped)
            if am:
                toks=tokenize(am.group(2)); val,_=eval_expr(toks,0)
                state.variables[am.group(1)]=val; i+=1; continue

            # general expression
            toks=tokenize(stripped)
            if toks: eval_expr(toks,0)
            i+=1

        except NetchError as e:
            print_error(e, state.current_line, state.current_line_text); sys.exit(1)
        except Exception as e:
            print_error(NetchError(str(e), fix="Check this line for typos or incorrect values."),
                        state.current_line, state.current_line_text); sys.exit(1)

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

def run_file(path):
    if not path.endswith('.ntch'):
        print("[Netch] WARNING: File doesn't use .ntch extension. Are you running a Netch 1 file?")
    with open(path,'r',encoding='utf-8') as f:
        source = f.read()
    n1 = detect_netch1(source)
    if n1:
        print("\n" + "━"*52)
        print("  👋  Hey! This looks like a Netch 1 file.")
        print("      Netch 1 is discontinued. Here's what to change:")
        for w in n1: print(f"  •  {w}")
        print("  📖  Docs: github.com/netchcodelang/netchcodinglang")
        print("━"*52 + "\n")
    has_header = any(l.strip()=='<using.ntch>' for l in source.split('\n')[:5])
    if not has_header:
        print("[Netch] WARNING: Missing <using.ntch> at the top of your file.")
    check_for_updates()
    run_lines(source.split('\n'))
    if state.window: state.window.mainloop()

if __name__ == '__main__':
    if len(sys.argv)<2:
        print(f"Netch 2 Interpreter v{NETCH_VERSION}")
        print("Usage: python interpreter.py yourfile.ntch")
        sys.exit(0)
    run_file(sys.argv[1])
