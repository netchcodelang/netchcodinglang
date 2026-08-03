// Reference data — kept in sync with netch-builder/cheatsheet.js, the source of truth
// for what netch actually supports (nothing aspirational).
const REFERENCE = [{"cat":"Basics","title":"File header","syntax":"<using.netch>","example":"<using.netch>\n\nprint(\"hello world\")","note":"Required at the top of every netch file. Missing it just warns instead of crashing."},{"cat":"Basics","title":"Comments","syntax":"#  and  \"\"\" \"\"\"","example":"# this is a comment\n\"\"\"\nthis is a\nmulti-line comment\n\"\"\""},{"cat":"Basics","title":"Variables","syntax":"name = value","example":"age = 10\nname = jake   # no quotes needed"},{"cat":"Basics","title":"Print","syntax":"print(value)","example":"print(\"hello\")\nprint(age)"},{"cat":"Basics","title":"Math","syntax":"+  -  *  /","example":"total = price + tax"},{"cat":"Functions","title":"Define a function","syntax":"function name():","example":"function greet():\n    print(\"hi!\")"},{"cat":"Functions","title":"Call a function","syntax":"run(name)","example":"run(greet)"},{"cat":"Logic & Loops","title":"If / else","syntax":"if x > 5:\n    ...\nelse:\n    ...","example":"if score > 5:\n    print(\"nice\")\nelse:\n    print(\"keep going\")"},{"cat":"Logic & Loops","title":"While loop","syntax":"while condition:","example":"while count < 5:\n    print(count)\n    count = count + 1","note":"Auto-stops after 100,000 loops outside a window app, so it can never freeze forever."},{"cat":"Logic & Loops","title":"Repeat loop","syntax":"repeat N times:","example":"repeat 3 times:\n    print(\"hi\")"},{"cat":"Logic & Loops","title":"True / false","syntax":"while true:","example":"while true:\n    if button.clicked(mybtn):\n        print(\"clicked!\")"},{"cat":"Lists","title":"Make a list","syntax":"name = [a, b, c]","example":"fruits = [apple, banana, cherry]"},{"cat":"Lists","title":"For each loop","syntax":"for each x in list:","example":"for each fruit in fruits:\n    print(fruit)"},{"cat":"Lists","title":"Add / remove","syntax":"list.add(x)\nlist.remove(x)","example":"fruits.add(mango)\nfruits.remove(banana)"},{"cat":"Lists","title":"Length & indexing","syntax":"list.length\nlist[0]","example":"print(fruits.length)\nprint(fruits[0])"},{"cat":"Windows","title":"Start a window app","syntax":"<using.netch>\n<window.using>","example":"<using.netch>\n<window.using>\n\nwindow.title(\"My App\")"},{"cat":"Windows","title":"Title & size","syntax":"window.title(\"...\")\nwindow.size(w, h)","example":"window.title(\"My App\")\nwindow.size(500, 400)"},{"cat":"Windows","title":"Plain text on screen","syntax":"window.text(\"...\")","example":"window.text(\"Welcome!\")"},{"cat":"Labels","title":"Named/updatable label","syntax":"window.text.name = \"value\"","example":"window.text.status = \"Ready\""},{"cat":"Labels","title":"Position","syntax":"text.name.position(x, y)","example":"text.status.position(20, 10)"},{"cat":"Buttons","title":"Button with an action","syntax":"window.button.name = action ...","example":"window.button.save = action run(save_file)"},{"cat":"Buttons","title":"Button without an action (for polling)","syntax":"window.button.name","example":"window.button.mybtn"},{"cat":"Buttons","title":"Check if clicked","syntax":"if button.clicked(name):","example":"if button.clicked(mybtn):\n    print(\"pressed!\")","note":"Fires True once per press, then resets — put this inside a loop."},{"cat":"Buttons","title":"Color","syntax":"button.name.color = \"...\"","example":"button.save.color = \"#4a90d9\""},{"cat":"Buttons","title":"Position & size","syntax":"button.name.position(x, y)\nbutton.name.size(w, h)","example":"button.save.position(50, 20)\nbutton.save.size(100, 40)"},{"cat":"Buttons","title":"Rounded corners","syntax":"button.name.round(radius)","example":"button.save.round(10)"},{"cat":"Buttons","title":"Font size","syntax":"button.name.fontsize(n)","example":"button.save.fontsize(15)"},{"cat":"Text Editors","title":"Make a text box","syntax":"window.textbox.name","example":"window.textbox.editor"},{"cat":"Text Editors","title":"Position & size","syntax":"textbox.name.position(x, y)\ntextbox.name.size(w, h)","example":"textbox.editor.position(20, 80)\ntextbox.editor.size(400, 250)"},{"cat":"Text Editors","title":"Font size","syntax":"textbox.name.fontsize(n)","example":"textbox.editor.fontsize(16)"},{"cat":"Text Editors","title":"Save to file","syntax":"write(box, \"file.txt\")","example":"write(editor, \"notes.txt\")"},{"cat":"Text Editors","title":"Load from file","syntax":"read(\"file.txt\", box)","example":"read(\"notes.txt\", editor)"},{"cat":"Checkboxes, Sliders & Progress","title":"Checkbox","syntax":"window.checkbox.name = \"label\"","example":"window.checkbox.agree = \"I agree\"\nagreed = checkbox.agree"},{"cat":"Checkboxes, Sliders & Progress","title":"Slider","syntax":"window.slider.name = slider(min, max)","example":"window.slider.volume = slider(0, 100)\nvol = slider.volume"},{"cat":"Checkboxes, Sliders & Progress","title":"Progress bar","syntax":"window.progress.name = progress(max)\nprogress.name.set(n)","example":"window.progress.loading = progress(100)\nprogress.loading.set(45)"},{"cat":"Checkboxes, Sliders & Progress","title":"Position & size","syntax":"<widget>.name.position(x, y)\n<widget>.name.size(w, h)","example":"checkbox.agree.position(20, 20)"},{"cat":"Images","title":"Show an image","syntax":"window.image.name = \"path.png\"","example":"window.image.logo = \"logo.png\""},{"cat":"Images","title":"Position & size","syntax":"image.name.position(x, y)\nimage.name.size(w, h)","example":"image.logo.position(20, 20)\nimage.logo.size(120, 120)","note":"Resizing needs Pillow, which netch auto-installs the first time you use it."},{"cat":"Selections","title":"Dropdown / radio","syntax":"window.selection.name = dropdown(a, b, c)","example":"window.selection.color = dropdown(red, green, blue)"},{"cat":"Selections","title":"Read the value","syntax":"selection.name","example":"chosen = selection.color\nprint(chosen)"},{"cat":"Selections","title":"Color & size","syntax":"selection.name.color = \"...\"\nselection.name.size(w, h)","example":"selection.color.color = \"#eeeeee\""},{"cat":"Themes","title":"Set a color theme","syntax":"window.theme(\"dark\" | \"light\" | \"#hexcolor\")","example":"window.theme(\"dark\")","note":"Buttons, textboxes, and labels created afterward automatically use the theme colors."},{"cat":"Input","title":"Key press detection","syntax":"if key.pressed(\"keyname\"):","example":"while true:\n    if key.pressed(\"space\"):\n        print(\"jump!\")","note":"Same one-shot-per-press pattern as button.clicked() — put it inside a loop."},{"cat":"Math","title":"Random number","syntax":"random(min, max)","example":"x = random(1, 10)\nprint(random(50, 100))"},{"cat":"Files & System","title":"Open a file / link","syntax":"open(\"path or url\")","example":"open(\"https://example.com\")\nopen(\"C:/notes.txt\")"},{"cat":"Files & System","title":"Delete a file","syntax":"delete(\"path\")","example":"delete(\"old_file.txt\")"},{"cat":"Files & System","title":"Copy a file","syntax":"copy(\"source\", \"destination\")","example":"copy(\"notes.txt\", \"backup.txt\")"},{"cat":"Files & System","title":"Download a file","syntax":"download.file(\"url\")\ndownload.file(\"url\", \"savename\")","example":"download.file(\"https://example.com/thing.zip\")"},{"cat":"Files & System","title":"Wait / pause","syntax":"wait(seconds)","example":"wait(2)"},{"cat":"Files & System","title":"Close the app","syntax":"close()","example":"window.button.quit = action close()"},{"cat":"Web","title":"Show a webpage","syntax":"display.webpage(\"url\")","example":"display.webpage(\"www.example.com\")","note":"https:// gets added automatically if you forget it."},{"cat":"Discord Bots","title":"Set up the bot","syntax":"bot.token = \"...\"\nbot.prefix = \"...\"","example":"bot.token = \"YOUR_TOKEN\"\nbot.prefix = \"!\""},{"cat":"Discord Bots","title":"Add a command","syntax":"bot.command.name = action func","example":"bot.command.hello = action say_hi"},{"cat":"Mixing in Python","title":"Raw python block","syntax":"# why: <reason>\n<python>\n...\n</python>","example":"# why: netch has no regex yet\n<python>\nimport re\nfound = re.findall(r\"\\d+\", text)\n</python>","note":"Needs a \"# why:\" comment right above it. Python + bat combined can never be more than 30% of the file."},{"cat":"Mixing in Python","title":"Raw .bat block (Windows only)","syntax":"# why: <reason>\n<bat>\n...\n</bat>","example":"# why: quick system command netch can't do yet\n<bat>\necho hello\n</bat>"}];

// ---- reference search ----
const refSearch = document.getElementById('ref-search');
const refResults = document.getElementById('ref-results');

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function renderReference(filterText) {
  const q = (filterText || '').toLowerCase().trim();
  const matches = REFERENCE.filter((entry) => {
    if (!q) return true;
    return (entry.cat + ' ' + entry.title + ' ' + entry.syntax + ' ' + entry.example)
      .toLowerCase()
      .includes(q);
  });

  refResults.innerHTML = '';
  if (matches.length === 0) {
    refResults.innerHTML = '<div class="ref-empty">No matches. Try a different word.</div>';
    return;
  }

  matches.forEach((entry) => {
    const div = document.createElement('div');
    div.className = 'ref-entry';
    div.innerHTML = `
      <div class="ref-cat">${escapeHtml(entry.cat)}</div>
      <div class="ref-title">${escapeHtml(entry.title)}</div>
      <div class="ref-syntax">${escapeHtml(entry.syntax)}</div>
      <div class="ref-example">${escapeHtml(entry.example)}</div>
      ${entry.note ? `<div class="ref-note">${escapeHtml(entry.note)}</div>` : ""}
    `;
    refResults.appendChild(div);
  });
}

refSearch.addEventListener('input', () => renderReference(refSearch.value));
renderReference('');

// ---- install tabs ----
document.querySelectorAll('.install-tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.install-tab').forEach((t) => t.classList.remove('active'));
    document.querySelectorAll('.install-panel').forEach((p) => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.target).classList.add('active');
  });
});
