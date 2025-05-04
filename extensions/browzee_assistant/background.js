const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let serverProcess = null;

// Function to ensure .env file exists with proper configuration
function ensureEnvFile() {
  const envPath = path.join(__dirname, '.env');
  const defaultEnv = {
    GEMINI_API_KEY: 'AIzaSyA1jseZInDQvJOWAecLaLJWbApXxgv6mws',
    PORT: '8010',
    NODE_ENV: 'production'
  };

  // Read existing .env if it exists
  let existingEnv = {};
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf8');
    envContent.split('\n').forEach(line => {
      const [key, value] = line.split('=');
      if (key && value) {
        existingEnv[key.trim()] = value.trim();
      }
    });
  }

  // Merge with defaults, preserving any existing values
  const finalEnv = { ...defaultEnv, ...existingEnv };

  // Write the final .env file
  const envContent = Object.entries(finalEnv)
    .map(([key, value]) => `${key}=${value}`)
    .join('\n');
  
  fs.writeFileSync(envPath, envContent);
  return finalEnv;
}

// Function to start the server
function startServer() {
  if (serverProcess) {
    console.log('Server is already running');
    return;
  }

  const serverPath = path.join(__dirname, 'server.js');
  
  // Ensure .env exists and get environment variables
  const env = ensureEnvFile();
  
  // Start the server with the environment variables
  serverProcess = spawn('node', [serverPath], {
    stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, ...env }
  });

  // Log server output
  serverProcess.stdout.on('data', (data) => {
    console.log(`Server: ${data}`);
  });

  serverProcess.stderr.on('data', (data) => {
    console.error(`Server Error: ${data}`);
  });

  serverProcess.on('close', (code) => {
    console.log(`Server process exited with code ${code}`);
    serverProcess = null;
  });

  console.log('Server started successfully');
}

// Function to stop the server
function stopServer() {
  if (serverProcess) {
    serverProcess.kill();
    serverProcess = null;
    console.log('Server stopped');
  }
}

// Start server when extension is installed or updated
chrome.runtime.onInstalled.addListener(() => {
  startServer();
});

// Start server when extension is loaded
chrome.runtime.onStartup.addListener(() => {
  startServer();
});

// Stop server when extension is uninstalled
chrome.runtime.onSuspend.addListener(() => {
  stopServer();
});

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'CHECK_SERVER_STATUS') {
    sendResponse({ running: !!serverProcess });
  }
}); 