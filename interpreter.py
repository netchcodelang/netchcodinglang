import sys
import os
import re
import urllib.request
import json

# ─────────────────────────────────────────────
#  VERSION & AUTO-UPDATER
# ─────────────────────────────────────────────

NETCH_VERSION = "2.0.0"
GITHUB_API = "https://api.github.com/repos/netchcodelang/netchcodinglang/releases/latest"

def check_for_updates():
    try:
        req = urllib.request.Request(GITHUB_API, headers={"User-Agent": "netch2"})
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.loads(r.read())
            latest = data.get("tag_name", "").lstrip("v")
            if latest and latest != NETCH_VERSION:
                print(f"[Netch] Update available: v{latest} (you have v{NETCH_VERSION})")
                print("[Netch] Download at: https://github.com/netchcodelang/netchcodinglang")
    except:
        pass  # silently skip if offline

# ─────────────────────────────────────────────
#  NETCH 1 SYNTAX DETECTOR
# ─────────────────────────────────────────────

NETCH1_PATTERNS = [
    (r'<using\.netch>', "You used <using.netch> — that's Netch 1! In Netch 2 use <using.ntch>"),
    (r'\badd\.button\b', "add.button is Netch 1 syntax. In Netch 2, use: button(\"label\") action ..."),
    (r'\bdisplay\.text\b', "display.text is Netch 1 syntax. In Netch 2, use: displaytext(\"text\")"),
    (r'\bopen\.file\b', "open.file is Netch 1 syntax. In Netch 2, use: openfile(\"path\")"),
    (r'run on click', "\"run on click\" is Netch 1 syntax. In Netch 2, use: button(\"label\") action yourcode()"),
]

def detect_netch1(source):
    warnings = []
    for pattern, message in NETCH1_PATTERNS:
        if re.search(pattern, source):
            warnings.append(message)
    return warnings

# ─────────────────────────────────────────────
#  ERROR SYSTEM
# ─────────────────────────────────────────────

class NetchError(Exception):
    def __init__(self, message, line_num=None, line_text=None, fix=None):
        self.message = message
        self.line_num = line_num
        self.line_text = line_text
        self.fix = fix
        super().__init__(message)

def print_error(e, line_num=None, line_text=None):
    print()
    print("━" * 52)
    print("  ❌  Netch Error")
    if line_num:
        print(f"  📍  Line {line_num}: {line_text.strip() if line_text else ''}")
    print(f"  💬  {e.message if isinstance(e, NetchError) else str(e)}")
    if isinstance(e, NetchError) and e.fix:
        print(f"  🔧  Fix: {e.fix}")
    print("━" * 52)
    print()

# ─────────────────────────────────────────────
#  TKINTER (optional, graceful fallback)
# ─────────────────────────────────────────────

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False

# ─────────────────────────────────────────────
#  STATE
# ─────────────────────────────────────────────

class NetchState:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.window = None
        self.widgets = {}        # name -> tk widget
        self.button_actions = {}
        self.window_title = "Netch App"
        self.window_width = 800
        self.window_height = 600
        self.theme_color = "#ffffff"
        self.font_name = "Segoe UI"
        self.font_size = 12
        self.current_line = 0
        self.current_line_text = ""

state = NetchState()

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def resolve(value):
    if isinstance(value, str):
        if value in state.variables:
            return state.variables[value]
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        if value == 'true':  return True
        if value == 'false': return False
        try: return int(value)
        except: pass
        try: return float(value)
        except: pass
        return value
    return value

def ensure_window():
    if not TK_AVAILABLE:
        raise NetchError(
            "Tkinter is not installed on this system.",
            fix="Reinstall Python from python.org and make sure to check 'tcl/tk' during setup."
        )
    if state.window is None:
        state.window = tk.Tk()
        state.window.title(state.window_title)
        state.window.geometry(f"{state.window_width}x{state.window_height}")
        state.window.configure(bg=state.theme_color)

def netch_print(msg):
    print(str(msg))

def make_font(size=None, bold=False):
    if TK_AVAILABLE:
        return (state.font_name, size or state.font_size, 'bold' if bold else 'normal')
    return None

# ─────────────────────────────────────────────
#  EXPRESSION EVALUATOR
# ─────────────────────────────────────────────

def parse_args(tokens, pos):
    args = []
    if pos < len(tokens) and tokens[pos][0] == 'LPAREN':
        pos += 1
        depth = 1
        current = []
        while pos < len(tokens) and depth > 0:
            t, v = tokens[pos]
            if t == 'LPAREN': depth += 1; current.append((t,v))
            elif t == 'RPAREN':
                depth -= 1
                if depth > 0: current.append((t,v))
            elif t == 'COMMA' and depth == 1:
                if current:
                    val, _ = eval_expr(current, 0)
                    args.append(val)
                current = []
            else:
                current.append((t,v))
            pos += 1
        if current:
            val, _ = eval_expr(current, 0)
            args.append(val)
    return args, pos

TOKEN_PATTERNS = [
    ('HEADER',    r'<using\.ntch>'),
    ('STRING_LIT',r'"[^"]*"'),
    ('FLOAT',     r'\d+\.\d+'),
    ('INT',       r'\d+'),
    ('BOOL',      r'\b(true|false)\b'),
    ('IDENT',     r'[a-zA-Z_][a-zA-Z0-9_.]*'),
    ('LPAREN',    r'\('),
    ('RPAREN',    r'\)'),
    ('COMMA',     r','),
    ('PLUS',      r'\+'),
    ('MINUS',     r'-'),
    ('STAR',      r'\*'),
    ('SLASH',     r'/'),
    ('EEQ',       r'=='),
    ('NEQ',       r'!='),
    ('LTE',       r'<='),
    ('GTE',       r'>='),
    ('LT',        r'<'),
    ('GT',        r'>'),
    ('ASSIGN',    r'='),
    ('SKIP',      r'[ \t]+'),
    ('COMMENT',   r'#[^\n]*'),
]

def tokenize(code):
    tokens = []
    pos = 0
    while pos < len(code):
        matched = False
        for tok_type, pattern in TOKEN_PATTERNS:
            m = re.match(pattern, code[pos:])
            if m:
                if tok_type not in ('SKIP','COMMENT'):
                    tokens.append((tok_type, m.group()))
                pos += m.end()
                matched = True
                break
        if not matched:
            pos += 1
    return tokens

def eval_expr(tokens, pos):
    left, pos = eval_atom(tokens, pos)
    while pos < len(tokens) and tokens[pos][0] in ('PLUS','MINUS','STAR','SLASH','EEQ','NEQ','LT','GT','LTE','GTE'):
        op = tokens[pos][0]; pos += 1
        right, pos = eval_atom(tokens, pos)
        left = apply_op(op, left, right)
    return left, pos

def eval_atom(tokens, pos):
    if pos >= len(tokens): return None, pos
    tok_type, tok_val = tokens[pos]

    if tok_type == 'IDENT':
        pos += 1
        if pos < len(tokens) and tokens[pos][0] == 'LPAREN':
            args, pos = parse_args(tokens, pos)
            return call_builtin(tok_val, args), pos
        return resolve(tok_val), pos

    if tok_type == 'STRING_LIT': return tok_val[1:-1], pos+1
    if tok_type == 'INT':        return int(tok_val), pos+1
    if tok_type == 'FLOAT':      return float(tok_val), pos+1
    if tok_type == 'BOOL':       return tok_val == 'true', pos+1
    return None, pos+1

def apply_op(op, l, r):
    if op == 'PLUS':
        if isinstance(l, str) or isinstance(r, str): return str(l)+str(r)
        return l+r
    if op == 'MINUS': return l-r
    if op == 'STAR':  return l*r
    if op == 'SLASH': return l/r if r != 0 else 0
    if op == 'EEQ':   return l == r
    if op == 'NEQ':   return l != r
    if op == 'LT':    return l < r
    if op == 'GT':    return l > r
    if op == 'LTE':   return l <= r
    if op == 'GTE':   return l >= r

# ─────────────────────────────────────────────
#  BUILT-IN FUNCTIONS
# ─────────────────────────────────────────────

def call_builtin(name, args):
    s = state

    # ── window config ──
    if name == 'window':
        ensure_window(); return None
    if name == 'window.title':
        s.window_title = str(args[0]) if args else ''
        if s.window: s.window.title(s.window_title)
        return None
    if name == 'window.size':
        if len(args) >= 2:
            s.window_width = int(args[0]); s.window_height = int(args[1])
            if s.window: s.window.geometry(f"{s.window_width}x{s.window_height}")
        return None
    if name == 'window.theme':
        s.theme_color = str(args[0]) if args else '#fff'
        if s.window: s.window.configure(bg=s.theme_color)
        return None

    # ── label / displaytext ──
    if name in ('label', 'displaytext'):
        ensure_window()
        text = str(args[0]) if args else ''
        color = str(args[1]) if len(args) > 1 else '#000000'
        size  = int(args[2]) if len(args) > 2 else s.font_size
        lbl = tk.Label(s.window, text=text, bg=s.theme_color, fg=color,
                       font=(s.font_name, size))
        lbl.pack(pady=4, padx=10, anchor='w')
        return None

    # ── button ──
    if name == 'button':
        ensure_window()
        label = str(args[0]) if args else 'Button'
        bg    = str(args[1]) if len(args) > 1 else '#0078d4'
        fg    = str(args[2]) if len(args) > 2 else 'white'
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
        key = str(args[0]) if args else 'textbox'
        width = int(args[1]) if len(args) > 1 else 30
        entry = tk.Entry(s.window, font=make_font(), width=width,
                         relief='solid', bd=1)
        entry.pack(pady=4, padx=10, anchor='w')
        s.widgets[key] = entry
        return None

    # ── passwordbox ──
    if name == 'passwordbox':
        ensure_window()
        key = str(args[0]) if args else 'password'
        width = int(args[1]) if len(args) > 1 else 30
        entry = tk.Entry(s.window, font=make_font(), width=width,
                         show='*', relief='solid', bd=1)
        entry.pack(pady=4, padx=10, anchor='w')
        s.widgets[key] = entry
        return None

    # ── getinput ──
    if name == 'getinput':
        key = str(args[0]) if args else ''
        w = s.widgets.get(key)
        if w and hasattr(w, 'get'): return w.get()
        return ''

    # ── image ──
    if name == 'image':
        ensure_window()
        path = str(args[0]) if args else ''
        try:
            from tkinter import PhotoImage
            img = PhotoImage(file=path)
            lbl = tk.Label(s.window, image=img, bg=s.theme_color)
            lbl.image = img
            lbl.pack(pady=4, padx=10)
        except Exception as e:
            raise NetchError(
                f"Could not load image: {path}",
                fix="Make sure the image path is correct and the file exists. Netch supports .png and .gif images."
            )
        return None

    # ── progressbar ──
    if name == 'progressbar':
        ensure_window()
        key   = str(args[0]) if args else 'progress'
        value = int(args[1]) if len(args) > 1 else 0
        bar = ttk.Progressbar(s.window, length=300, mode='determinate')
        bar['value'] = value
        bar.pack(pady=4, padx=10, anchor='w')
        s.widgets[key] = bar
        return None

    if name == 'setprogress':
        key   = str(args[0]) if args else 'progress'
        value = int(args[1]) if len(args) > 1 else 0
        w = s.widgets.get(key)
        if w: w['value'] = value
        return None

    # ── checkbox ──
    if name == 'checkbox':
        ensure_window()
        key   = str(args[0]) if args else 'check'
        label = str(args[1]) if len(args) > 1 else key
        var = tk.BooleanVar()
        cb = tk.Checkbutton(s.window, text=label, variable=var,
                            bg=s.theme_color, font=make_font())
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
        label = str(args[1]) if len(args) > 1 else 'Option'
        value = str(args[2]) if len(args) > 2 else label
        if group not in s.widgets:
            s.widgets[group] = tk.StringVar()
        rb = tk.Radiobutton(s.window, text=label, variable=s.widgets[group],
                            value=value, bg=s.theme_color, font=make_font())
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
        options = [str(a) for a in args[1:]] if len(args) > 1 else ['Option 1']
        var = tk.StringVar(value=options[0])
        dd = ttk.Combobox(s.window, textvariable=var, values=options,
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
        key  = str(args[0]) if args else 'slider'
        mn   = int(args[1]) if len(args) > 1 else 0
        mx   = int(args[2]) if len(args) > 2 else 100
        var  = tk.IntVar(value=mn)
        sl   = tk.Scale(s.window, from_=mn, to=mx, orient='horizontal',
                        variable=var, bg=s.theme_color, font=make_font(9))
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
        lb = tk.Listbox(s.window, font=make_font(), relief='solid',
                        bd=1, height=6, width=30)
        for item in items:
            lb.insert(tk.END, item)
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
        nb = ttk.Notebook(s.window)
        nb.pack(fill='both', expand=True, padx=10, pady=4)
        s.widgets[key] = nb
        return None

    if name == 'addtab':
        key   = str(args[0]) if args else 'tabs'
        title = str(args[1]) if len(args) > 1 else 'Tab'
        nb = s.widgets.get(key)
        if nb:
            frame = tk.Frame(nb, bg=s.theme_color)
            nb.add(frame, text=title)
        return None

    # ── sound ──
    if name == 'sound.play':
        path = str(args[0]) if args else ''
        try:
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except ImportError:
            try:
                os.system(f'start /min "" "{path}"')
            except:
                raise NetchError(
                    "sound.play() could not play the file.",
                    fix="Make sure the file path is correct and the file exists. Supported formats: .wav"
                )
        return None

    if name == 'sound.stop':
        try:
            import winsound
            winsound.PlaySound(None, winsound.SND_PURGE)
        except: pass
        return None

    # ── file ops ──
    if name == 'openfile':
        path = str(args[0]) if args else ''
        if path:
            try: os.startfile(path)
            except Exception:
                raise NetchError(
                    f"Could not open file: {path}",
                    fix="Check the file path is correct and the file actually exists."
                )
        else:
            if TK_AVAILABLE:
                path = filedialog.askopenfilename()
        return path

    if name == 'deletefile':
        path = str(args[0]) if args else ''
        if not os.path.exists(path):
            raise NetchError(f"Cannot delete — file not found: {path}",
                             fix="Double-check the file path.")
        os.remove(path); return None

    if name == 'copyfile':
        import shutil
        if len(args) < 2:
            raise NetchError("copyfile() needs 2 arguments: source and destination",
                             fix='Example: copyfile("C:/source.txt", "C:/dest.txt")')
        shutil.copy(str(args[0]), str(args[1])); return None

    if name == 'download.file':
        if len(args) < 2:
            raise NetchError("download.file() needs a URL and a save path",
                             fix='Example: download.file("https://example.com/file.txt", "C:/file.txt")')
        urllib.request.urlretrieve(str(args[0]), str(args[1])); return None

    # ── print ──
    if name == 'print':
        netch_print(args[0] if args else '')
        return None

    # ── math / util ──
    if name == 'random':
        import random
        if len(args) >= 2: return random.randint(int(args[0]), int(args[1]))
        return random.randint(0, 100)

    if name == 'number':   return float(args[0]) if args else 0
    if name == 'upper':    return str(args[0]).upper() if args else ''
    if name == 'lower':    return str(args[0]).lower() if args else ''
    if name == 'contains': return str(args[1]) in str(args[0]) if len(args)>=2 else False
    if name == 'length':   return len(str(args[0])) if args else 0
    if name == 'ask':      return input(str(args[0]) + ' ' if args else '')
    if name == 'time.now':
        import datetime; return str(datetime.datetime.now())

    # ── user functions ──
    if name in s.functions:
        run_block(s.functions[name]); return None

    # unknown
    raise NetchError(
        f"Unknown function or command: {name}()",
        fix=f'Did you spell "{name}" correctly? Check the Netch 2 docs for a list of built-in functions.'
    )

# ─────────────────────────────────────────────
#  BLOCK / LINE RUNNER
# ─────────────────────────────────────────────

def run_block(lines):
    run_lines(lines)

def run_lines(lines):
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        state.current_line = i + 1
        state.current_line_text = stripped

        try:
            if not stripped or stripped == '<using.ntch>' or stripped.startswith('#'):
                i += 1; continue

            if stripped == 'use window':
                ensure_window(); i += 1; continue

            # ── function definition ──
            if stripped.startswith('function '):
                fname = stripped[9:].strip()
                if not fname:
                    raise NetchError("function needs a name",
                                     fix='Example: function greet')
                body = []; i += 1
                while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                    body.append(lines[i]); i += 1
                state.functions[fname] = body
                continue

            # ── run(name) ──
            m = re.match(r'^run\(([^)]+)\)$', stripped)
            if m:
                fname = m.group(1).strip()
                if fname not in state.functions:
                    raise NetchError(
                        f"run() called function \"{fname}\" which doesn't exist.",
                        fix=f'Make sure you defined it: function {fname}'
                    )
                run_block(state.functions[fname]); i += 1; continue

            # ── if / if...else ──
            if stripped.startswith('if '):
                cond_part = stripped[3:].strip()

                # button clicked
                cm = re.match(r'^button\(["\'"]?([^"\'")]+)["\'"]?\)\s+clicked$', cond_part)
                if cm:
                    btn_name = cm.group(1)
                    body = []; i += 1
                    while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                        body.append(lines[i]); i += 1
                    w = state.widgets.get(btn_name)
                    if w and isinstance(w, tk.Button if TK_AVAILABLE else object):
                        captured = body[:]
                        w.config(command=lambda b=captured: run_block(b))
                    continue

                toks = tokenize(cond_part)
                cond, _ = eval_expr(toks, 0)
                body = []; else_body = []; in_else = False
                i += 1
                while i < len(lines):
                    s2 = lines[i].strip()
                    if s2 == 'else':
                        in_else = True; i += 1; continue
                    if lines[i].startswith('    ') or lines[i].startswith('\t'):
                        (else_body if in_else else body).append(lines[i]); i += 1
                    else: break
                if cond: run_block(body)
                else:    run_block(else_body)
                continue

            # ── while ──
            if stripped.startswith('while '):
                cond_src = stripped[6:].strip()
                body = []; i += 1
                while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                    body.append(lines[i]); i += 1
                count = 0
                while count < 100000:
                    toks = tokenize(cond_src)
                    cond, _ = eval_expr(toks, 0)
                    if not cond: break
                    run_block(body); count += 1
                if count >= 100000:
                    print("[Netch] WARNING: Your while loop ran 100,000 times and was stopped.")
                    print("[Netch] Tip: Make sure your loop condition eventually becomes false.")
                continue

            # ── repeat ──
            if stripped.startswith('repeat '):
                count_src = stripped[7:].strip()
                toks = tokenize(count_src)
                count, _ = eval_expr(toks, 0)
                if not isinstance(count, (int, float)):
                    raise NetchError(f"repeat needs a number, got: {count}",
                                     fix='Example: repeat 5')
                body = []; i += 1
                while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                    body.append(lines[i]); i += 1
                for _ in range(int(count)): run_block(body)
                continue

            # ── button with action ──
            bm = re.match(r'^button\(["\'"]?([^"\'")]+)["\'"]?\)\s+action\s+(.+)$', stripped)
            if bm:
                ensure_window()
                label = bm.group(1)
                action_src = bm.group(2).strip()
                btn = tk.Button(state.window, text=label, bg='#0078d4', fg='white',
                                font=make_font(), relief='flat',
                                padx=12, pady=6, cursor='hand2') if TK_AVAILABLE else None
                if btn:
                    btn.pack(pady=4, padx=10, anchor='w')
                    state.widgets[label] = btn
                    def make_cmd(src): return lambda: eval_expr(tokenize(src), 0)
                    btn.config(command=make_cmd(action_src))
                i += 1; continue

            # ── assignment ──
            am = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', stripped)
            if am:
                toks = tokenize(am.group(2))
                val, _ = eval_expr(toks, 0)
                state.variables[am.group(1)] = val
                i += 1; continue

            # ── general expression / call ──
            toks = tokenize(stripped)
            if toks: eval_expr(toks, 0)
            i += 1

        except NetchError as e:
            print_error(e, state.current_line, state.current_line_text)
            sys.exit(1)
        except Exception as e:
            ne = NetchError(str(e), fix="Check this line for typos or incorrect values.")
            print_error(ne, state.current_line, state.current_line_text)
            sys.exit(1)

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

def run_file(path):
    if not path.endswith('.ntch'):
        print("[Netch] WARNING: This file doesn't use the .ntch extension.")
        print("[Netch] Netch 2 files should end in .ntch — are you running a Netch 1 file?")

    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()

    # netch 1 detection
    n1_warnings = detect_netch1(source)
    if n1_warnings:
        print()
        print("━" * 52)
        print("  👋  Hey! This looks like a Netch 1 file.")
        print("      Netch 1 has been discontinued.")
        print("      Here's what needs to change for Netch 2:")
        for w in n1_warnings:
            print(f"  •  {w}")
        print("  📖  Docs: github.com/netchcodelang/netchcodinglang")
        print("━" * 52)
        print()

    has_header = any(l.strip() == '<using.ntch>' for l in source.split('\n')[:5])
    if not has_header:
        print("[Netch] WARNING: Missing <using.ntch> at the top of your file.")
        print("[Netch] Add this as the very first line of your .ntch file.")

    check_for_updates()
    run_lines(source.split('\n'))

    if state.window:
        state.window.mainloop()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Netch 2 Interpreter v{NETCH_VERSION}")
        print("Usage: python interpreter.py yourfile.ntch")
        sys.exit(0)
    run_file(sys.argv[1])
