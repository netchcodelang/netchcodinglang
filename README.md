# Netch 2 🌐
### The easiest and best coding language on earth
*An Aerotion Production*

---

## What is Netch?
Netch is a beginner-friendly programming language designed to be simpler than Python, while still being powerful enough to grow with you. We listen to our community and build what YOU want.

## ⚠️ Netch 1 Notice
Netch 1 has been discontinued. You can still find the old version on the [official website](https://netchcodelang.github.io/netchcodinglang/index.html#) under the "Learn More" page.

**Netch 2 is a fresh start — same vision, better everything.**

---

## 🚀 Quick Start

### Requirements
- Windows 10 or later
- Python 3.8+ (installer handles this for you)

### Install
**No Python?** Download `installer.bat` and run it as Administrator.
**Already have Python?** Run `installer.py` directly.

To run a `.ntch` file:
```
python interpreter.py yourfile.ntch
```

---

## 📝 Netch 2 Syntax

Every Netch 2 file starts with:
```
<using.ntch>
```

### Hello World
```
<using.ntch>
print("Hello, World!")
```

### Variables & Math
```
<using.ntch>
name = "netch"
x = 10
y = 5
result = x + y
print(result)
```

### Window App
```
<using.ntch>
use window
window.title("My App")
window.size(600, 400)
window.theme("#ffffff")

label("Welcome to Netch 2!")
button("Click Me") action print("You clicked it!")
```

### All UI Widgets
```
<using.ntch>
use window

label("Enter your name:")
textbox("namebox")

label("Password:")
passwordbox("passbox")

label("Pick a color:")
dropdown("colors", "Red", "Green", "Blue")

label("Volume:")
slider("vol", 0, 100)

checkbox("agree", "I agree to the terms")

radiobutton("size", "Small", "small")
radiobutton("size", "Large", "large")

label("Pick an item:")
listbox("mylist", "Apples", "Bananas", "Oranges")

progressbar("loading", 75)

image("logo.png")

button("Submit") action print(getinput("namebox"))
```

### Tab Control
```
<using.ntch>
use window
tabcontrol("tabs")
addtab("tabs", "Home")
addtab("tabs", "Settings")
addtab("tabs", "About")
```

### Reading Widget Values
```
<using.ntch>
getinput("namebox")       # textbox / passwordbox
getchecked("agree")       # checkbox → true/false
getradio("size")          # radiobutton → selected value
getdropdown("colors")     # dropdown → selected item
getslider("vol")          # slider → number
getlist("mylist")         # listbox → selected item
```

### Sound
```
<using.ntch>
sound.play("alert.wav")
sound.stop()
```

### Functions
```
<using.ntch>
function greet
    print("Hello from a function!")

run(greet)
```

### If / Else
```
<using.ntch>
score = 85

if score > 90
    print("Grade: A")
else
    print("Grade: B")
```

### If Button Clicked
```
<using.ntch>
use window
button("Say Hi")

if button("Say Hi") clicked
    print("Hi!")
```

### While Loop
```
<using.ntch>
x = 0
while x < 5
    print(x)
    x = x + 1
```

### Repeat Loop
```
<using.ntch>
repeat 3
    print("Netch!")
```

### File Operations
```
<using.ntch>
openfile("C:/example.txt")
copyfile("C:/source.txt", "C:/dest.txt")
deletefile("C:/old.txt")
download.file("https://example.com/file.txt", "C:/saved.txt")
```

### String & Math Utilities
```
<using.ntch>
print(upper("hello"))       # HELLO
print(lower("WORLD"))       # world
print(length("netch"))      # 5
print(contains("netch2", "netch"))  # true
print(random(1, 100))       # random number
print(time.now())           # current date/time
```

---

## ❌ Error Messages
Netch 2 gives you clear, beginner-friendly errors that tell you exactly what went wrong AND how to fix it:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ❌  Netch Error
  📍  Line 5: openfile("wrongpath")
  💬  Could not open file: wrongpath
  🔧  Fix: Check the file path is correct and the file actually exists.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔄 Auto-Updater
Every time you run a `.ntch` file, Netch 2 automatically checks GitHub for updates and lets you know if a newer version is available.

---

## 🌍 Community
Join our Reddit to stay updated, show off your projects, report bugs, and chat with other netch coders!

👉 [r/netchcoding2](https://www.reddit.com/r/netchcoding2/)

## 🐛 Bug Reports
Found a bug? Post it on the Reddit and we'll fix it ASAP!

## 📋 Changelog
See [UPDATELOG.md](UPDATELOG.md) for the full version history.

---

## 👥 Credits
- **cutestcookie9** — Original owner & founder of Netch (cutestcookie9@gmail.com)
- **fineed99** — New owner of Netch & founder of Aerotion Productions (fineed99@gmail.com)
