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
**No Python?** Download `installer.bat` and run it as administrator.  
**Already have Python?** Download `installer.py` and run it.

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

### Variables
```
<using.ntch>
name = "netch"
age = 2
print(name)
print(age)
```

### Window App
```
<using.ntch>
use window
window.title("My App")
window.size(600, 400)
window.theme("#ffffff")

displaytext("Welcome to my app!")
button("Click Me") action print("Button clicked!")
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
x = 10
if x > 5
    print("x is greater than 5")
else
    print("x is 5 or less")
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
    print("Netch is awesome!")
```

### File Operations
```
<using.ntch>
openfile("C:/example.txt")
copyfile("C:/source.txt", "C:/dest.txt")
deletefile("C:/old.txt")
```

### Button with Action
```
<using.ntch>
use window
button("Open File") action openfile("C:/myfile.txt")
```

### If Button Clicked
```
<using.ntch>
use window
button("Say Hi")

if button("Say Hi") clicked
    print("Hi!")
```

### Input Box
```
<using.ntch>
use window
input("mybox")
button("Submit") action print(getinput("mybox"))
```

### Math & Random
```
<using.ntch>
x = random(1, 100)
print(x)
```

### String Operations
```
<using.ntch>
print(upper("hello"))
print(lower("WORLD"))
print(length("netch"))
```

---

## 🌍 Community
Join our Reddit to stay updated, show off your projects, report bugs, and chat with other netch coders!

👉 [r/netchcoding2](https://www.reddit.com/r/netchcoding2/)

## 🐛 Bug Reports
Found a bug? Post it on the Reddit and we'll get it fixed ASAP!

## 👥 Credits
- **cutestcookie9** — Original owner & founder of Netch (cutestcookie9@gmail.com)
- **fineed99** — New owner of Netch & founder of Aerotion
