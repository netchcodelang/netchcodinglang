# Netch 2 🌐
### The easiest and best coding language on earth
*An Aerotion Production*

---

## What is Netch?
Netch is a beginner-friendly programming language for building real desktop apps. Simpler than Python, powerful enough for serious projects. We listen to our community and build what YOU want.

> ⚠️ **Netch 1 has been discontinued.** The old version is still available at the [official website](https://netchcodelang.github.io/netchcodinglang/index.html#) under "Learn More".

---

## 🚀 Quick Start

### Install
**No Python?** Run `installer.bat` as Administrator — it handles everything.  
**Already have Python?** Run `python installer.py`

### First Script
```
<using.ntch>
print("Hello from Netch 2!")
```
```
netch run hello.ntch
```

### Your First Window App
```
<using.ntch>
use window
window.title("My App")
window.size(600, 400)
label("Welcome to Netch 2!")
button("Click Me") action print("Hello!")
```

---

## 📋 Full Language Reference

### Variables & Types
```
name   = "Alice"
age    = 25
active = true
score  = 98.5
items  = list.new("a", "b", "c")
```

### Control Flow
```
# if/else
if score > 90
    print("A grade")
else
    print("B grade")

# while
x = 0
while x < 5
    print(x)
    x = x + 1

# repeat
repeat 3
    print("Hello!")

# for loop
for i from 1 to 10
    print(i)

# foreach
foreach item in mylist
    print(item)
```

### Functions
```
function greet
    print("Hello!")

run(greet)
```

### Math
```
math.abs(x)           # absolute value
math.round(x, 2)      # round to 2 decimals
math.floor(x)         # round down
math.ceil(x)          # round up
math.sqrt(x)          # square root
math.power(x, y)      # x to the power of y
math.max(a, b, c)     # largest value
math.min(a, b, c)     # smallest value
math.clamp(v, mn, mx) # keep between min and max
random(1, 100)        # random whole number
```

### Strings
```
upper("hello")               # "HELLO"
lower("WORLD")               # "world"
length("netch")              # 5
contains("netch2", "netch")  # true
str.replace("hi", "hi", "hey") # "hey"
str.trim("  hi  ")           # "hi"
str.split("a,b", ",")        # list
str.reverse("netch")         # "hcten"
str.format("Hi {}", "Alice") # "Hi Alice"
str.starts("hello", "he")    # true
str.ends("hello", "lo")      # true
str.repeat("ab", 3)          # "ababab"
str.count("hello", "l")      # 2
str.index("hello", "l")      # 2
```

### Lists
```
mylist = list.new("a", "b", "c")
list.add("mylist", "d")
list.get("mylist", 0)           # "a"
list.length("mylist")           # 4
list.remove("mylist", 0)
list.contains("mylist", "b")    # true
list.join("mylist", ", ")       # "a, b, c"
```

### File System
```
file.read("path.txt")
file.write("path.txt", "content")
file.append("path.txt", "new line")
file.exists("path.txt")         # true/false
file.rename("old.txt", "new.txt")
file.size("path.txt")           # bytes
openfile("C:/file.txt")
deletefile("C:/file.txt")
copyfile("C:/src.txt", "C:/dst.txt")
download.file("https://...", "C:/save.txt")
sys.desktop                     # Desktop path
sys.homedir                     # Home folder path
```

### Window & UI
```
dark:true                       # enable dark mode
use window
window.title("My App")
window.size(800, 600)
window.theme("#ffffff")
window.center
window.icon("app.ico")
window.opacity(0.9)
window.resizable(false)
window.minimize
window.maximize
window.fullscreen(true)
window.always.top(true)
clear.window
```

### Widgets
```
label("Text")
label("Text", "#ff0000")        # colored
heading("Big Title")
button("Click") action print("clicked")
cr.button("Rounded") action print("clicked")
textbox("mybox", 30, "Placeholder...")
passwordbox("mypass")
dropdown("mydrop", "A", "B", "C")
checkbox("mycheck", "Check me")
radiobutton("group", "Option A", "a")
slider("myslider", 0, 100)
listbox("mylist", "Item 1", "Item 2")
progressbar("prog", 50)
setprogress("prog", 75)
image("photo.png")
separator
spacer(20)
heading("Big Title")
link("Click", "https://example.com")
tabcontrol("tabs")
addtab("tabs", "Tab 1")
display.webpage("https://example.com")
```

### Reading Widget Values
```
getinput("mybox")           # textbox / passwordbox
getchecked("mycheck")       # checkbox → true/false
getradio("group")           # radio → selected value
getdropdown("mydrop")       # dropdown → selected item
getslider("myslider")       # slider → number
getlist("mylist")           # listbox → selected item
```

### Dialogs
```
dialog.info("Title", "Message")
dialog.error("Title", "Message")
dialog.warn("Title", "Message")
answer = dialog.ask("Title", "Sure?")   # true/false
text   = dialog.input("Title", "Prompt:")
file   = dialog.file("Open file")
folder = dialog.folder("Select folder")
save   = dialog.save("Save as")
```

### Canvas
```
canvas.new("c", 400, 300, "#000000")
canvas.line("c", x1, y1, x2, y2, "#ffffff", 2)
canvas.rect("c", x1, y1, x2, y2, "#0078d4")
canvas.circle("c", x, y, radius, "#0078d4")
canvas.text("c", x, y, "text", "#ffffff")
canvas.image("c", x, y, "photo.png")
canvas.clear("c")
canvas.onclick("c", "myfunctionname")
```

### Networking
```
get.request("https://api.example.com")
send.post("url", "key", "value")
send.json("url", "key", "value")
send.textbox("mybox", "url", "fieldname")
connect.server("ws://myserver.com")
send.message("hello server")
url.open("https://example.com")
browser.open("https://example.com")
json.parse("...")
json.make("key", "value")
# response stored in last.response
```

### Email
```
email.send("you@gmail.com", "apppassword",
           "them@gmail.com", "Subject", "Body")
email.send.html("you@gmail.com", "apppassword",
                "them@gmail.com", "Subject", "<h1>Hi</h1>")
```

### Sound, Video, TTS, Voice
```
sound.play("alert.wav")
sound.stop()
video.play("clip.mp4")
video.stop("clip")
tts.say("Hello from Netch 2!")
tts.say("Faster", 220)
tts.save("Hello!", "output.mp3")
text = voice.listen()           # uses Google (online)
text = voice.listen.offline()   # uses PocketSphinx (offline)
```

### PDF
```
pdf.create("report.pdf", "My Report")
pdf.heading("Title")
pdf.text("Body text")
pdf.text("Big text", 18)
pdf.newpage()
pdf.save()
```

### System & Date/Time
```
sys.env("PATH")
sys.exit()
sys.platform
sys.username
sys.homedir
sys.cwd
sys.desktop
date.today
date.year / date.month / date.day
time.now()
time.sleep(2)
time.stamp
```

### Type Utils
```
typeof(value)       # "text", "number", "bool", "list"
tonumber("42")      # 42
totext(42)          # "42"
isnumber("hello")   # false
isempty("")         # true
```

### Clipboard
```
clipboard.copy("text")
clipboard.paste()
```

### Shell / BAT Integration
```
run.bat("echo Hello")
run.bat("C:/myscript.bat")
run.shell("python other.py")
# results in bat.output and shell.exit
```

### Plugin System
```
plugin.load("myplugin.py")
plugin.call("myplugin.hello", "Alice")
```

---

## 📦 Package Manager

```
netch pkg install <name>      # install a package
netch pkg remove  <name>      # uninstall
netch pkg list                # list installed
netch pkg update              # update all packages
netch list pkgs all           # all packages on GitHub
netch pkg info <name>         # info about a package
```

### Official Packages

| Package | What it does |
|---|---|
| `customwindowtitle` | Custom PNG window title bars |
| `controllocalapps` | Attach custom titles to any .exe |
| `ainetchintegration` | Add AI to your app |

### Using Packages
```
<using.ntch>
importpkg customwindowtitle

# or load everything installed:
import all pkgs
```

### ainetchintegration
```
importpkg ainetchintegration
ai.key("your-anthropic-api-key")
ai.system("You are a helpful assistant")
reply = ai.ask("What is Netch?")
reply = ai.chat("Hello!")          # remembers history
ai.clear()                         # reset conversation
hist  = ai.history()               # get conversation text
```

### customwindowtitle
```
importpkg customwindowtitle
use window
windowtitle("title.nframetchpng", "My App")

# with custom close/min/max buttons:
windowtitle("title.nframetchpng", "My App",
            "close.png", "min.png", "max.png")
```

---

## 🔨 Compile to EXE

```
netch compiletoexe myapp.ntch
netch compiletoexe myapp.ntch --name "My App"
netch compiletoexe myapp.ntch --icon myapp.ico
netch compiletoexe myapp.ntch --output C:/releases
netch compiletoexe myapp.ntch --folder
```

Output is a standalone `.exe` — no Python required to run it.

---

## 🛠️ CLI Reference

```
netch run <file.ntch>         run a script
netch new <name>              create a new blank script
netch version                 show installed version
netch update                  check for updates
netch help                    show all commands
netch pkg install <name>      install a package
netch pkg remove  <name>      remove a package
netch pkg list                list installed packages
netch pkg update              update all packages
netch list pkgs all           all packages on GitHub
netch compiletoexe <file>     compile to .exe
netch create-pkg              open package creator GUI
```

---

## 🌍 Community
Join our Reddit — share projects, report bugs, request packages!

👉 **[r/netchcoding2](https://www.reddit.com/r/netchcoding2/)**

## 🐛 Bug Reports
Post on Reddit and we'll fix it fast. We actually listen.

## 👥 Credits
- **cutestcookie9** — Original owner & founder of Netch (cutestcookie9@gmail.com)
- **fineed99** — New owner of Netch & founder of Aerotion Productions (fineed99@gmail.com)

## 📋 Changelog
See [UPDATELOG.md](UPDATELOG.md) for full version history.
- **cutestcookie9** — Original owner & founder of Netch (cutestcookie9@gmail.com)
- **fineed99** — New owner of Netch & founder of Aerotion Productions (fineed99@gmail.com)
