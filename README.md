
## 🧑‍💻 BrowZee AI - Developer Setup Guide

### 1. Clone the repository:

```bash
git clone https://github.com/natanelDaniel/BrowZee-AI.git
```

### 2. Set up a virtual environment and install dependencies:

```bash
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate (Linux/Mac)
pip install -r requirements.txt
```

### 3. Build the `ai_server.exe` file using PyInstaller (Its preferable from administrator cmd):

```bash
pyinstaller ^
  --hidden-import=pydantic ^
  --hidden-import=pydantic-core ^
  --hidden-import=pydantic.deprecated.decorator ^
  --onefile ^
  --uac-admin ^
  --add-data "venv/Lib/site-packages/browser_use/agent/system_prompt.md;browser_use/agent" ^
  --add-data "venv/Lib/site-packages/browser_use/dom/buildDomTree.js;browser_use/dom" ^
  ai_server.py
```

Output binary will be located at:

```bash
dist/ai_server.exe
```

### 4. Build the customized Chromium browser

#### Step A: Generate build files with GN (first time only - can take up to a day):
on cmd:
```bash
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
```
Add Depot Tools to PATH
Once you've downloaded Depot Tools, you'll need to add it to your system's PATH so that you can run commands like gclient from anywhere.

Find the location where you cloned Depot Tools (e.g., C:\path\to\depot_tools)

Right-click on "This PC" or "Computer" and select "Properties"

Click on "Advanced system settings" on the left

Click on the "Environment Variables" button

Under "System variables", find the "Path" variable and select "Edit"

Add the path to the Depot Tools directory (e.g., C:\path\to\depot_tools) to the list
open a powershall on your src folder
```bash
$env:DEPOT_TOOLS_WIN_TOOLCHAIN=0
fetch chromium
```
```bash
cd ..
powershell -ExecutionPolicy Bypass -File .\update_src.ps1
gclient runhooks
cd src
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

Start the AI server manually:

```bash
dist/ai_server.exe
```
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
