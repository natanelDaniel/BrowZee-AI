
// -------------------- TODO LIST -------------------- //
// ⏳ בניית GUI עם כפתור לפתיחת צ'אט דפדפן (input/output)
// ⏳ תמיכה באינטראקציה של ה-LLM עם ה-DOM וסיכום מסך אוטומטי
//
// ⏳ סוכן AI מתקדם שיכול לפעול דרך n8n ולבצע משימות מורכבות
//
// ⏳ כפתור "למד את האתר/הדף הנוכחי" ויכולת לשאול עליו שאלות (One-click RAG)
//
// ⏳ בדיקת תקינות ריצה של הדפדפן עם הדגלים הרצויים לכל משתמש
//
// ⏳ בדיקת התאמה להפצה מסחרית בהתאם לרישוי של Chromium
//
// ⏳ הפעלת שרת ה-AI יחד עם פתיחת הדפדפן (אם לא רץ עדיין)

// -------------------- README for Developers --------------------

## 🧑‍💻 BrowZee AI - Developer Setup Guide

### 1. Clone the repository:

```bash
git clone https://github.com/your-user/browzee-ai-browser.git
cd browzee-ai-browser
```

### 2. Set up a virtual environment and install dependencies:

```bash
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate (Linux/Mac)
pip install -r requirements_clean.txt
```

### 3. Build the `ai_server.exe` file using PyInstaller:

```bash
pyinstaller ^
  --hidden-import=pydantic ^
  --hidden-import=pydantic-core ^
  --hidden-import=pydantic.deprecated.decorator ^
  --onefile ^
  --uac-admin ^
  --add-data "venv/Lib/site-packages/browser_use/agent/system_prompt.md;browser_use/agent" ^
  --add-data "venv/Lib/site-packages/browser_use/dom/buildDomTree.js;browser_use/dom" ^
  AI_Agent/ai_server.py
```

Output binary will be located at:

```bash
dist/ai_server.exe
```

### 4. Start the AI server manually:

```bash
dist/ai_server.exe
```

### 5. Build the customized Chromium browser

#### Step A: Generate build files with GN (first time only - can take up to a day):

```bash
gn gen out/Default
```

#### Step B: Compile the browser and installer:

```bash
autoninja -C out/Default chrome
autoninja -C out/Default mini_installer.exe
```

#### Step C: Launch the newly installed Chromium browser:

```bash
<project_path>/out/Default/mini_installer.exe
```

Then run:

```bash
<user_profile_path>/AppData/Local/Chromium/Application/chrome.exe
```

## 🧪 Testing the Browser

Simply launch:

```bash
<user_profile_path>/AppData/Local/Chromium/Application/chrome.exe
```

It should open with remote debugging enabled.

## 🧩 Future Features

- AI DOM agent with in-browser chat box
- Smart summarization of current page
- One-click website learning for Q&A
- Seamless integration with n8n workflows
- Automatic startup of AI server alongside browser launch
- Commercial packaging and EXE bundling
