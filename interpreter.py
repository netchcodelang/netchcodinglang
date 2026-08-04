import sys
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

# ─────────────────────────────────────────────
#  LEXER
# ─────────────────────────────────────────────

TOKEN_PATTERNS = [
    ('HEADER',    r'<using\.ntch>'),
    ('USE',       r'\buse\b'),
    ('FUNCTION',  r'\bfunction\b'),
    ('IF',        r'\bif\b'),
    ('ELSE',      r'\belse\b'),
    ('WHILE',     r'\bwhile\b'),
    ('CLICKED',   r'\bclicked\b'),
    ('ACTION',    r'\baction\b'),
    ('PRINT',     r'\bprint\b'),
    ('RUN',       r'\brun\b'),
    ('REPEAT',    r'\brepeat\b'),
    ('NUMBER',    r'\bnumber\b'),
    ('STRING_LIT',r'"[^"]*"'),
    ('FLOAT',     r'\d+\.\d+'),
    ('INT',       r'\d+'),
    ('BOOL',      r'\b(true|false)\b'),
    ('IDENT',     r'[a-zA-Z_][a-zA-Z0-9_.]*'),
    ('LPAREN',    r'\('),
    ('RPAREN',    r'\)'),
    ('LBRACE',    r'\{'),
    ('RBRACE',    r'\}'),
    ('COMMA',     r','),
    ('PLUS',      r'\+'),
    ('MINUS',     r'-'),
    ('STAR',      r'\*'),
    ('SLASH',     r'/'),
    ('EQ',        r'=='),
    ('NEQ',       r'!='),
    ('LTE',       r'<='),
    ('GTE',       r'>='),
    ('LT',        r'<'),
    ('GT',        r'>'),
    ('ASSIGN',    r'='),
    ('NEWLINE',   r'\n'),
    ('SKIP',      r'[ \t]+'),
    ('COMMENT',   r'#[^\n]*'),
    ('MCOMMENT',  r'"""[\s\S]*?"""'),
]

def tokenize(code):
    tokens = []
    pos = 0
    while pos < len(code):
        match = None
        for tok_type, pattern in TOKEN_PATTERNS:
            regex = re.compile(pattern)
            match = regex.match(code, pos)
            if match:
                if tok_type not in ('SKIP', 'COMMENT', 'MCOMMENT'):
                    tokens.append((tok_type, match.group()))
                pos = match.end()
                break
        if not match:
            pos += 1  # skip unknown chars
    return tokens

# ─────────────────────────────────────────────
#  INTERPRETER STATE
# ─────────────────────────────────────────────

class NetchState:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.window = None
        self.widgets = {}
        self.button_actions = {}
        self.window_title = "Netch App"
        self.window_width = 800
        self.window_height = 600
        self.theme_color = "#ffffff"
        self.font_name = "Segoe UI"
        self.font_size = 12

state = NetchState()

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def resolve(value):
    """Resolve a value - variable lookup or literal."""
    if isinstance(value, str):
        if value in state.variables:
            return state.variables[value]
        # string literal (strip quotes)
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        if value == 'true':
            return True
        if value == 'false':
            return False
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value
    return value

def netch_print(msg):
    print(str(msg))

def ensure_window():
    if state.window is None:
        state.window = tk.Tk()
        state.window.title(state.window_title)
        state.window.geometry(f"{state.window_width}x{state.window_height}")
        state.window.configure(bg=state.theme_color)

# ─────────────────────────────────────────────
#  EXPRESSION EVALUATOR
# ─────────────────────────────────────────────

def eval_expr(tokens, pos):
    """Very simple expression evaluator. Returns (value, new_pos)."""
    left, pos = eval_atom(tokens, pos)
    while pos < len(tokens) and tokens[pos][0] in ('PLUS','MINUS','STAR','SLASH','EQ','NEQ','LT','GT','LTE','GTE'):
        op = tokens[pos][0]
        pos += 1
        right, pos = eval_atom(tokens, pos)
        left = apply_op(op, left, right)
    return left, pos

def eval_atom(tokens, pos):
    if pos >= len(tokens):
        return None, pos
    tok_type, tok_val = tokens[pos]

    # function call or identifier
    if tok_type == 'IDENT':
        pos += 1
        if pos < len(tokens) and tokens[pos][0] == 'LPAREN':
            # function call
            args, pos = parse_args(tokens, pos)
            result = call_builtin(tok_val, args)
            return result, pos
        return resolve(tok_val), pos

    if tok_type == 'STRING_LIT':
        return tok_val[1:-1], pos + 1
    if tok_type == 'INT':
        return int(tok_val), pos + 1
    if tok_type == 'FLOAT':
        return float(tok_val), pos + 1
    if tok_type == 'BOOL':
        return tok_val == 'true', pos + 1
    if tok_type == 'PRINT':
        pos += 1
        args, pos = parse_args(tokens, pos)
        val = args[0] if args else ''
        netch_print(val)
        return val, pos

    return None, pos + 1

def apply_op(op, left, right):
    if op == 'PLUS':  return str(left) + str(right) if isinstance(left, str) or isinstance(right, str) else left + right
    if op == 'MINUS': return left - right
    if op == 'STAR':  return left * right
    if op == 'SLASH': return left / right if right != 0 else 0
    if op == 'EQ':    return left == right
    if op == 'NEQ':   return left != right
    if op == 'LT':    return left < right
    if op == 'GT':    return left > right
    if op == 'LTE':   return left <= right
    if op == 'GTE':   return left >= right

def parse_args(tokens, pos):
    """Parse (arg1, arg2, ...) and return list of evaluated args + new pos."""
    args = []
    if pos < len(tokens) and tokens[pos][0] == 'LPAREN':
        pos += 1  # skip (
        while pos < len(tokens) and tokens[pos][0] != 'RPAREN':
            if tokens[pos][0] == 'COMMA':
                pos += 1
                continue
            val, pos = eval_expr(tokens, pos)
            args.append(val)
        if pos < len(tokens):
            pos += 1  # skip )
    return args, pos

# ─────────────────────────────────────────────
#  BUILT-IN FUNCTIONS
# ─────────────────────────────────────────────

def call_builtin(name, args):
    # window/UI
    if name == 'window.title':
        state.window_title = str(args[0]) if args else ''
        if state.window:
            state.window.title(state.window_title)
        return None

    if name == 'window.size':
        if len(args) >= 2:
            state.window_width = int(args[0])
            state.window_height = int(args[1])
            if state.window:
                state.window.geometry(f"{state.window_width}x{state.window_height}")
        return None

    if name == 'window.theme':
        state.theme_color = str(args[0]) if args else '#ffffff'
        if state.window:
            state.window.configure(bg=state.theme_color)
        return None

    # displaytext
    if name == 'displaytext':
        ensure_window()
        text = str(args[0]) if args else ''
        lbl = tk.Label(state.window, text=text, bg=state.theme_color,
                       font=(state.font_name, state.font_size))
        lbl.pack(pady=5)
        return None

    # button
    if name == 'button':
        ensure_window()
        label = str(args[0]) if args else 'Button'
        btn = tk.Button(state.window, text=label,
                        font=(state.font_name, state.font_size),
                        relief='flat', bg='#0078d4', fg='white',
                        padx=12, pady=6, cursor='hand2')
        btn.pack(pady=5)
        state.widgets[label] = btn
        return None

    # input box
    if name == 'input':
        ensure_window()
        name_key = str(args[0]) if args else 'input'
        entry = tk.Entry(state.window, font=(state.font_name, state.font_size), width=30)
        entry.pack(pady=5)
        state.widgets[name_key] = entry
        return None

    # get input value
    if name == 'getinput':
        key = str(args[0]) if args else ''
        widget = state.widgets.get(key)
        if widget and isinstance(widget, tk.Entry):
            return widget.get()
        return ''

    # print
    if name == 'print':
        msg = str(args[0]) if args else ''
        netch_print(msg)
        return None

    # file ops
    if name == 'openfile':
        path = str(args[0]) if args else ''
        if path:
            os.startfile(path)
        else:
            path = filedialog.askopenfilename()
        return path

    if name == 'deletefile':
        path = str(args[0]) if args else ''
        if os.path.exists(path):
            os.remove(path)
        return None

    if name == 'copyfile':
        import shutil
        if len(args) >= 2:
            shutil.copy(str(args[0]), str(args[1]))
        return None

    # math
    if name == 'number':
        return float(args[0]) if args else 0
    if name == 'random':
        import random
        if len(args) >= 2:
            return random.randint(int(args[0]), int(args[1]))
        return 0

    # string ops
    if name == 'upper':
        return str(args[0]).upper() if args else ''
    if name == 'lower':
        return str(args[0]).lower() if args else ''
    if name == 'contains':
        if len(args) >= 2:
            return str(args[1]) in str(args[0])
        return False
    if name == 'length':
        return len(str(args[0])) if args else 0

    # ask user input
    if name == 'ask':
        prompt = str(args[0]) if args else ''
        return input(prompt + ' ')

    # time
    if name == 'time.now':
        import datetime
        return str(datetime.datetime.now())

    # user-defined function call
    if name in state.functions:
        run_block(state.functions[name])
        return None

    return None

# ─────────────────────────────────────────────
#  BLOCK RUNNER
# ─────────────────────────────────────────────

def run_block(lines):
    """Run a list of source lines as a netch block."""
    run_lines(lines)

def run_lines(lines):
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # skip blank / comments / header
        if not line or line.startswith('#') or line == '<using.ntch>':
            i += 1
            continue

        # multi-line comment
        if line.startswith('"""'):
            while i < len(lines) and not lines[i].rstrip().endswith('"""') or (lines[i].strip() == '"""' and i == i):
                i += 1
                if lines[i-1].strip().endswith('"""') and lines[i-1].strip() != '"""':
                    break
            i += 1
            continue

        # use window
        if line == 'use window':
            ensure_window()
            i += 1
            continue

        # function definition
        if line.startswith('function '):
            fname = line[9:].strip()
            body = []
            i += 1
            while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                body.append(lines[i])
                i += 1
            state.functions[fname] = body
            continue

        # run(functionname)
        if line.startswith('run(') and line.endswith(')'):
            fname = line[4:-1].strip()
            if fname in state.functions:
                run_block(state.functions[fname])
            i += 1
            continue

        # if statement
        if line.startswith('if '):
            condition_part = line[3:].strip()
            # check for clicked
            clicked_match = re.match(r'button\("?([^")]+)"?\)\s+clicked', condition_part)
            if clicked_match:
                btn_name = clicked_match.group(1)
                body = []
                i += 1
                while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                    body.append(lines[i])
                    i += 1
                widget = state.widgets.get(btn_name)
                if widget:
                    captured_body = body[:]
                    widget.config(command=lambda b=captured_body: run_block(b))
                continue

            # regular condition
            tokens = tokenize(condition_part)
            cond, _ = eval_expr(tokens, 0)
            body = []
            else_body = []
            i += 1
            in_else = False
            while i < len(lines):
                stripped = lines[i].strip()
                if stripped == 'else':
                    in_else = True
                    i += 1
                    continue
                if lines[i].startswith('    ') or lines[i].startswith('\t'):
                    if in_else:
                        else_body.append(lines[i])
                    else:
                        body.append(lines[i])
                    i += 1
                else:
                    break
            if cond:
                run_block(body)
            else:
                run_block(else_body)
            continue

        # while loop
        if line.startswith('while '):
            condition_src = line[6:].strip()
            body = []
            i += 1
            while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                body.append(lines[i])
                i += 1
            loop_count = 0
            MAX_LOOPS = 100000
            while loop_count < MAX_LOOPS:
                tokens = tokenize(condition_src)
                cond, _ = eval_expr(tokens, 0)
                if not cond:
                    break
                run_block(body)
                loop_count += 1
            if loop_count >= MAX_LOOPS:
                print("WARNING: Infinite loop stopped by netch safety cap.")
            continue

        # repeat N times
        if line.startswith('repeat '):
            parts = line.split()
            count = int(resolve(parts[1])) if len(parts) > 1 else 0
            body = []
            i += 1
            while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                body.append(lines[i])
                i += 1
            for _ in range(count):
                run_block(body)
            continue

        # button with action
        btn_action = re.match(r'button\("?([^")]+)"?\)\s+action\s+(.+)', line)
        if btn_action:
            ensure_window()
            btn_label = btn_action.group(1)
            action_src = btn_action.group(2).strip()
            btn = tk.Button(state.window, text=btn_label,
                            font=(state.font_name, state.font_size),
                            relief='flat', bg='#0078d4', fg='white',
                            padx=12, pady=6, cursor='hand2')
            btn.pack(pady=5)
            state.widgets[btn_label] = btn

            def make_action(src):
                def do_action():
                    toks = tokenize(src)
                    eval_expr(toks, 0)
                return do_action
            btn.config(command=make_action(action_src))
            i += 1
            continue

        # variable assignment
        assign_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', line)
        if assign_match:
            var_name = assign_match.group(1)
            val_src = assign_match.group(2).strip()
            tokens = tokenize(val_src)
            val, _ = eval_expr(tokens, 0)
            state.variables[var_name] = val
            i += 1
            continue

        # window config shorthands
        if line.startswith('window.title(') or line.startswith('window.size(') or line.startswith('window.theme('):
            tokens = tokenize(line)
            eval_expr(tokens, 0)
            i += 1
            continue

        # general expression / function call
        tokens = tokenize(line)
        if tokens:
            eval_expr(tokens, 0)

        i += 1

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

def run_file(path):
    if not path.endswith('.ntch'):
        print("WARNING: This file does not use the .ntch extension. Are you sure this is a Netch 2 file?")

    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()

    lines = source.split('\n')

    # check for header
    has_header = any(line.strip() == '<using.ntch>' for line in lines[:5])
    if not has_header:
        print("WARNING: Missing <using.ntch> header. Attempting to run anyway...")

    run_lines(lines)

    # if a window was created, start the mainloop
    if state.window:
        state.window.mainloop()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Netch 2 Interpreter")
        print("Usage: python interpreter.py yourfile.ntch")
        sys.exit(0)
    run_file(sys.argv[1])
