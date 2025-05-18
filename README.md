# BrowZee AI

This repository contains tools and approaches for integrating BrowZee with local backend servers while avoiding Content Security Policy (CSP) restrictions.

## BrowZee Bridge (Recommended)

The BrowZee Bridge is a separate local web server that acts as a proxy between your browser and BrowZee's backend services. This approach completely avoids CSP issues by serving a custom web interface that can freely communicate with the backend services.

### Why the Bridge Approach?

After trying multiple approaches to work around Chrome's strict CSP rules, we found that creating a separate bridge server is the most reliable solution. This approach:

1. Doesn't require any browser extensions or modifications
2. Works across all browsers (not just Chrome)
3. Provides a clean, dedicated interface for BrowZee functionality
4. Completely bypasses CSP restrictions

### Getting Started with BrowZee Bridge

1. Navigate to the `BrowZee-Bridge` directory
2. Run `run_bridge.bat` (Windows) or `run_bridge.ps1` (PowerShell)
3. Open your browser to [http://localhost:3000](http://localhost:3000)
4. Use the web interface to interact with BrowZee's backend services

For more details, see the [BrowZee Bridge README](BrowZee-Bridge/README.md).

## Alternative Approaches (Not Recommended)

We previously tried several other approaches that proved problematic:

### Chrome Extension

We attempted to create Chrome extensions (see `BrowZee-Extension` and `BrowZee-Extension-Proxy`) to bypass CSP restrictions. These approaches:

- Required installing a Chrome extension
- Were prone to breaking with Chrome updates
- Still encountered CSP issues in some contexts
- Required complex workarounds to function

### Direct Integration

We also tried direct integration approaches by modifying Chrome's New Tab Page or injecting scripts. These approaches:

- Faced severe CSP restrictions
- Required bypassing Chrome's security mechanisms
- Were unreliable and inconsistent across Chrome versions

## Requirements

- Python 3.6 or later
- BrowZee backend services:
  - Search Agent running on port 5000
  - Task Server running on port 8000

## License

© 2025 BrowZee. All rights reserved.

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
pyinstaller ^ --hidden-import=pydantic ^--hidden-import=playwright ^--hidden-import=PIL ^--hidden-import=posthog ^--hidden-import=PIL.Image ^ --hidden-import=selenium ^--hidden-import=pydantic-core ^ --hidden-import=pydantic.deprecated.decorator ^ --onefile ^ --uac-admin ^ --add-data "browzee_agent/agent/system_prompt.md;browzee_agent/agent" ^ --add-data "browzee_agent/dom/buildDomTree.js;browzee_agent/dom" ^ server2.py
```
or
```bash
pyinstaller --hidden-import=pydantic --hidden-import=pydantic-core --hidden-import=pydantic.deprecated.decorator --onefile --uac-admin --add-data "venv/Lib/site-packages/browser_use/agent/system_prompt.md;browser_use/agent" --add-data "venv/Lib/site-packages/browser_use/dom/buildDomTree.js;browser_use/dom" ai_server.py
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
$env:DEPOT_TOOLS_WIN_TOOLCHAIN = "0"
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
entering AI interface:
http://localhost:8000/

It should open with remote debugging enabled.

lunch with log:
```bash
 .\out\Default\chrome.exe --enable-logging --v=1 --log-file="C:\Users\21dan\chromium_ai_browser\src\out\Default\chrome_debug.log"
```
## 🧩 Future Features

- AI DOM agent with in-browser chat box
- Smart summarization of current page
- One-click website learning for Q&A
- Seamless integration with n8n workflows
- Automatic startup of AI server alongside browser launch
- Commercial packaging and EXE bundling
