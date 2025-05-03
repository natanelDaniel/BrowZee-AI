// ייבוא רכיב אנימציית הפלנטה
import './browzee_planet_animation.js';

// עדכון כתובת השרת
const SERVER_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws/status';

const socket = new WebSocket(WS_URL);
const output = document.getElementById('output');
const input = document.getElementById('input') as HTMLTextAreaElement | null;
const playPauseButton = document.getElementById('playPause');
const stopButton = document.getElementById('stop');
let awaitingResponse = false;
let loadingIndicator: HTMLDivElement | null = null;

// Type declaration for BrowzeePlanetAnimationElement for better type safety
interface BrowzeePlanetAnimationElement extends HTMLElement {
  // Add any specific methods or properties of the custom element if needed
}

function toggleTheme() {
  const icon = document.getElementById('themeIcon');
  document.body.classList.toggle('light-mode');
  const isLight = document.body.classList.contains('light-mode');
  // Using half-circle contrast icon which is perfect for theme switching
  // This icon doesn't look like settings and clearly shows light/dark concept
  if (icon) {
  icon.className = 'fa-solid fa-circle-half-stroke';
  // Rotate the icon to show which mode is active - top half light = light mode, top half dark = dark mode
  icon.style.transform = isLight ? 'rotate(180deg)' : 'rotate(0deg)';
  }
}

// Create loading indicator function - updated for agent thinking indicator
function createLoadingIndicator() {
  // First remove any existing indicator
  removeLoadingIndicator();
 
  // Create a new loading indicator
  loadingIndicator = document.createElement('div');
  loadingIndicator.className = 'loading-indicator';
  loadingIndicator.innerHTML = `
    <div class="dot-typing">
      <div></div>
      <div></div>
      <div></div>
    </div>
  `;
  if (output) {
  output.appendChild(loadingIndicator);
  }
  scrollToBottom(false);
  return loadingIndicator;
}

// Create agent thinking indicator between messages
function createAgentThinkingIndicator() {
  const thinkingIndicator = document.createElement('div');
  thinkingIndicator.className = 'agent-thinking-indicator';
  thinkingIndicator.innerHTML = `
    <div class="typing-dots">
      <div></div>
      <div></div>
      <div></div>
    </div>
  `;
  if (output) {
  output.appendChild(thinkingIndicator);
  }
 
  // Use the improved scrolling method
  scrollToBottom(false);
 
  return thinkingIndicator;
}

// Remove all loading indicators
function removeLoadingIndicator() {
  if (loadingIndicator) {
    loadingIndicator.remove();
    loadingIndicator = null;
  }
 
  const agentThinkingIndicator = document.querySelector('.agent-thinking-indicator');
  if (agentThinkingIndicator) {
    agentThinkingIndicator.remove();
  }
 
  adjustOutputPadding();
  scrollToBottom();
}

socket.onopen = () => {
  console.log("WebSocket connected successfully to", WS_URL);
};

socket.onerror = (error) => {
  console.error("WebSocket error:", error);
  appendMessage("Connection error: Could not connect to agent server", "error");
};

socket.onclose = (event) => {
  console.log("WebSocket closed:", event.code, event.reason);
  if (event.code !== 1000) { // If not closed normally
    appendMessage("Connection closed. Trying to reconnect...", "error");
    // Try to reconnect after a delay
    setTimeout(() => {
      console.log("Attempting to reconnect WebSocket...");
      const newSocket = new WebSocket(WS_URL);
      if (newSocket) {
        console.log("New WebSocket connection created");
        socket.onmessage = newSocket.onmessage;
        socket.onopen = newSocket.onopen;
        socket.onerror = newSocket.onerror;
        socket.onclose = newSocket.onclose;
      }
    }, 3000);
  }
};

socket.onmessage = (event) => {
  console.log("WebSocket message received:", event.data);
  const msg = event.data;
 
  // Remove any loading indicators first
  removeLoadingIndicator();
 
  // Show thinking indicator before displaying the message
  const thinkingIndicator = createAgentThinkingIndicator();
 
  // Set a timeout to display the actual message
  setTimeout(() => {
    // Remove the thinking indicator
    if (thinkingIndicator && thinkingIndicator.parentNode) {
      thinkingIndicator.parentNode.removeChild(thinkingIndicator);
    }
   
    // Display the actual message
    appendMessage(msg, "agent");
   
    if (msg.trim().endsWith("?")) {
      console.log("Message ends with ?, awaiting response");
      awaitingResponse = true;
    }
    if (msg.trim().startsWith("Task completed")) {
      console.log("Task completed message received");
      if (playPauseButton) {
      playPauseButton.innerHTML = '<i class="fas fa-rocket"></i>';
      }
      taskRunning = false;
      isPaused = false;
     
      // Hide processing indicator when task completes
      document.body.classList.remove('processing');
    }
   
    // Hide processing indicator after receiving a message
    document.body.classList.remove('processing');
  }, 800); // קיצור הזמן לאנימציה כדי להרגיש תגובתי יותר
};

let taskRunning = false;
let isPaused = false;

if (playPauseButton) {
  console.log('Found playPauseButton, setting up click handler');
  
playPauseButton.onclick = () => {
    console.log('Play/Pause button clicked');
    
    // Check if input exists and is the correct type before accessing value
    if (!(input instanceof HTMLTextAreaElement)) {
        console.error('Input element not found or not a textarea');
        return;
    }
    
  const text = input.value.trim();
    console.log('Current input text:', text || '(empty)');
    
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-type-assertion
    const modeSelect = document.getElementById('modeSelect') as HTMLSelectElement | null;
    const mode = modeSelect ? modeSelect.value : 'task'; // Default to task if not found
    console.log('Current mode:', mode);

  if (!taskRunning) {
      console.log('No task running, starting new task');
      
      if (!text && mode !== "chat-this-page") {
        console.log('No text entered and not in chat-this-page mode, ignoring');
        return;
      }

    // Add chat-active class to body and remove initial-screen
    document.body.classList.add('chat-active');
    document.body.classList.remove('initial-screen');
   
    // וידוא שהודעת הפתיחה מוסתרת לחלוטין
    const welcomeMsg = document.getElementById('welcomeMessage');
    if (welcomeMsg) {
      welcomeMsg.style.display = 'none';
      welcomeMsg.style.visibility = 'hidden';
    }
   
      // Hide the planet animation element completely
      const planetElement = document.querySelector('browzee-planet-animation') as BrowzeePlanetAnimationElement;
      if (planetElement) {
        planetElement.style.display = 'none';
        planetElement.style.visibility = 'hidden';
        planetElement.style.opacity = '0';
        planetElement.style.height = '0';
        planetElement.style.width = '0';
    }
   
    // Show processing indicator
    document.body.classList.add('processing');

      if (input) {
    input.value = '';
      }
    appendMessage(text, "task");
   
    // Show loading indicator under the last message
    createLoadingIndicator();

      // שליחת הבקשה לשרת עם הפרמטרים הנכונים
      console.log(`Sending POST request to ${SERVER_URL}/run-task with mode=${mode}`);
      
      fetch(`${SERVER_URL}/run-task`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task: text, mode: mode })
      })
      .then(response => {
        console.log('Received response from server:', response.status);
        if (!response.ok) {
          throw new Error(`Server responded with status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Received data from server:', data);
      })
      .catch(error => {
        console.error('Error sending request to server:', error);
        appendMessage(`Connection error: ${error.message}`, "error");
        removeLoadingIndicator();
        document.body.classList.remove('processing');
        taskRunning = false;
      });

    playPauseButton.innerHTML = '<i class="fas fa-pause"></i>';
    taskRunning = true;
    isPaused = false;
  } else {
    if (awaitingResponse) {
      socket.send(text);
      appendMessage(text, "task");
        if (input) {
      input.value = '';
        }
      awaitingResponse = false;
     
      // Show loading indicator under the last message
      createLoadingIndicator();
     
      // Show processing indicator when waiting for response
      document.body.classList.add('processing');
    }
    else {
      isPaused = !isPaused;
      const action = isPaused ? "pause" : "resume";
      playPauseButton.innerHTML = isPaused ? '<i class="fas fa-play"></i>' : '<i class="fas fa-pause"></i>';

        fetch(`${SERVER_URL}/${action}-task`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        .then(res => {
          if (!res.ok) {
            throw new Error(`Server responded with status: ${res.status}`);
          }
          return res.json();
        })
        .then(_ => {
          appendMessage(`Task ${action}d`, action);
               
                // If resuming, show loading indicator under the last message
                if (action === "resume") {
                  createLoadingIndicator();
                  document.body.classList.add('processing');
                } else {
                  removeLoadingIndicator();
                  document.body.classList.remove('processing');
                }
        })
        .catch(error => {
          console.error(`Error ${action}ing task:`, error);
          appendMessage(`Error ${action}ing task: ${error.message}`, "error");
          removeLoadingIndicator();
          document.body.classList.remove('processing');
        });
    }
  }
};
}

if (stopButton) {
stopButton.onclick = () => {
  fetch(`${SERVER_URL}/stop-task`, {
    method: 'POST'
  }).then(res => {
    if (!res.ok) {
      throw new Error(`Server responded with status: ${res.status}`);
    }
    return res.json();
  })
    .then(data => {
      const msg = data.status === "stopped"
        ? "🚩 Task stopped"
        : "⚠️ No active task to stop";
      appendMessage(msg, "stopped");
        if (playPauseButton) {
      playPauseButton.innerHTML = '<i class="fas fa-rocket"></i>';
        }
      taskRunning = false;
      isPaused = false;
     
      // Remove loading indicator when stopping
      removeLoadingIndicator();
     
      // Hide processing indicator when stopping
      document.body.classList.remove('processing');
    }).catch(error => {
      console.error('Error stopping task:', error);
      appendMessage(`Error stopping task: ${error.message}`, "error");
      removeLoadingIndicator();
      document.body.classList.remove('processing');
    });
};
}

// Improve input event handling
if (input) {
  console.log('Found input element, setting up event listeners');
  
  // Handle Enter key press
  input.addEventListener('keydown', (e) => {
    console.log('Key pressed in input:', e.key);
    // Send message when Enter is pressed (without shift for new line)
    if (e.key === 'Enter' && !e.shiftKey) {
      console.log('Enter pressed, triggering submission');
      e.preventDefault(); // Prevent default to avoid newline
      
      // Check if we have valid text to send
      const text = input.value.trim();
      if (text) {
        console.log('Submitting text:', text);
        if (playPauseButton) {
          playPauseButton.click();
        }
      }
    }
  });

  // Focus input when clicking on the input container
  const inputContainer = document.getElementById('inputContainer');
  if (inputContainer) {
    inputContainer.addEventListener('click', () => {
      if (input) {
        input.focus();
      }
    });
  }

  // Auto-expand input height as content grows
  input.addEventListener('input', () => {
    if (input) {
      input.style.height = 'auto';
      input.style.height = Math.min(input.scrollHeight, 120) + 'px'; // Max height 120px
    }
    });
}

// Ensure message is scrolled into view properly
function scrollToBottom(smooth = true) {
  if (!output) return;
  const lastMessage = output.lastElementChild;
  if (lastMessage instanceof HTMLElement) { // Check if lastMessage is an HTMLElement
    lastMessage.scrollIntoView({
      behavior: smooth ? 'smooth' : 'auto',
      block: 'start'  /* Changed from 'nearest' to 'start' to ensure visibility */
    });
   
    // Add additional scroll to provide more space
    setTimeout(() => {
      if (output) { // Check output again inside timeout
      output.scrollTop += 180; /* Increased from 120px to 180px */
      }
    }, smooth ? 150 : 0);
  }
}

function adjustOutputPadding() {
  const inputContainer = document.getElementById('inputContainer');
  const output = document.getElementById('output');

  if (inputContainer && output) {
    const inputHeight = inputContainer.offsetHeight + 40; // תוספת מרווח
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-type-assertion
    (output as HTMLElement).style.paddingBottom = `${inputHeight}px`;
  }
}

window.addEventListener('load', adjustOutputPadding);
window.addEventListener('resize', adjustOutputPadding);

// Update the appendMessage function to use our new scrolling method
function appendMessage(text: string, className: string) {
  const msg = document.createElement('div');
 
  // For status messages
  if (text.startsWith('🚀 Starting task:')) {
    msg.className = 'status-message task-starting';
    text = text.replace('🚀 Starting task:', 'Starting task:');
  }
  else if (text.includes('in the search box to perform')) {
    msg.className = 'status-message task-instruction';
  }
  else if (text.startsWith('🚩 Task stopped') || text.includes('Task stopped by user')) {
    msg.className = 'status-message task-stopped';
    text = text.replace('🚩 Task stopped', 'Task stopped by user.');
  }
  else if (text.startsWith('⚠️ No active task')) {
    msg.className = 'status-message task-warning';
    text = text.replace('⚠️ No active task to stop', 'No active task to stop');
  }
  else if (text.startsWith('Task paused')) {
    msg.className = 'status-message task-warning';
    text = 'Task paused';
  }
  else if (text.startsWith('Task resumed')) {
    msg.className = 'status-message task-starting';
    text = 'Task resumed';
  }
  else if (text.includes('Input') || text.includes('into index')) {
    msg.className = 'status-message keyboard-action';
  }
  else if (text.includes('Sent keys:')) {
    msg.className = 'status-message keyboard-action';
  }
  else if (text.includes('Scrolled')) {
    msg.className = 'status-message scroll-action';
  }
  else if (text.includes('Clicked button')) {
    msg.className = 'status-message click-action';
  }
  else if (text.includes('Task completed')) {
    msg.className = 'status-message completed';
  }
  else if (text.startsWith('Connection error:') || text.includes('error')) {
    msg.className = 'status-message error-message';
  }
  else if (text.startsWith('Server connection warning:')) {
    msg.className = 'status-message warning-message';
  }
  else {
    msg.className = 'message ' + className;
   
    // Add message actions for regular messages (not status messages)
    const messageActions = document.createElement('div');
    messageActions.className = 'message-actions';
   
    // Like button
    const likeBtn = document.createElement('button');
    likeBtn.className = 'message-action-btn';
    likeBtn.innerHTML = '<i class="far fa-thumbs-up"></i>';
    likeBtn.onclick = (e) => {
      e.stopPropagation();
      likeBtn.innerHTML = '<i class="fas fa-thumbs-up"></i>';
      likeBtn.style.color = '#3b82f6';
    };
   
    // Dislike button
    const dislikeBtn = document.createElement('button');
    dislikeBtn.className = 'message-action-btn';
    dislikeBtn.innerHTML = '<i class="far fa-thumbs-down"></i>';
    dislikeBtn.onclick = (e) => {
      e.stopPropagation();
      dislikeBtn.innerHTML = '<i class="fas fa-thumbs-down"></i>';
      dislikeBtn.style.color = '#ef4444';
    };
   
    // Copy button
    const copyBtn = document.createElement('button');
    copyBtn.className = 'message-action-btn';
    copyBtn.innerHTML = '<i class="far fa-copy"></i>';
    copyBtn.onclick = (e) => {
      e.stopPropagation();
      // Create a temporary element to copy from
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
     
      // Show success indicator
      const successIndicator = document.createElement('div');
      successIndicator.className = 'copy-success';
      successIndicator.textContent = 'Copied!';
      msg.appendChild(successIndicator);
     
      setTimeout(() => {
        successIndicator.classList.add('show');
      }, 10);
     
      setTimeout(() => {
        successIndicator.classList.remove('show');
        setTimeout(() => successIndicator.remove(), 300);
      }, 2000);
    };
   
    // Regenerate/refresh button
    const refreshBtn = document.createElement('button');
    refreshBtn.className = 'message-action-btn';
    refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
    refreshBtn.onclick = (e) => {
      e.stopPropagation();
      // This would typically trigger a regeneration
      // For now, it just changes color to indicate it was clicked
      refreshBtn.style.color = '#10b981';
    };
   
    // Add all buttons to the action container
    messageActions.appendChild(likeBtn);
    messageActions.appendChild(dislikeBtn);
    messageActions.appendChild(copyBtn);
    messageActions.appendChild(refreshBtn);
   
    // Add the action container to the message
    msg.appendChild(messageActions);
  }
 
  // Use innerHTML to render potential <br> tags from status messages too
  msg.innerHTML = text.replace(/\n/g, '<br>');
  if (output) {
  output.appendChild(msg);
  }
  adjustOutputPadding();
  scrollToBottom();
}

// Speech recognition functionality
const micButton = document.getElementById('micButton');
// Use 'any' for SpeechRecognition to bypass TS errors if types aren't available
const recognition = new ((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition)();
if (recognition) {
recognition.lang = 'en-US';
recognition.continuous = false;
recognition.interimResults = false;
}

if (micButton && recognition) {
micButton.onclick = () => {
  try {
    // Add recording class to body for visual feedback
    document.body.classList.add('recording');
   
    // Move to chat mode just like the regular button does
    if (!document.body.classList.contains('chat-active')) {
      document.body.classList.add('chat-active');
      document.body.classList.remove('initial-screen');
     
      // Make sure welcome message is completely hidden
      const welcomeMsg = document.getElementById('welcomeMessage');
      if (welcomeMsg) {
        welcomeMsg.style.display = 'none';
        welcomeMsg.style.visibility = 'hidden';
        welcomeMsg.style.height = '0';
        welcomeMsg.style.margin = '0';
        welcomeMsg.style.overflow = 'hidden';
      }
     
      // Hide the planet animation element completely
      const planetElement = document.querySelector('browzee-planet-animation') as BrowzeePlanetAnimationElement;
      if (planetElement) {
        planetElement.style.display = 'none';
        planetElement.style.visibility = 'hidden';
        planetElement.style.opacity = '0';
        planetElement.style.height = '0';
        planetElement.style.width = '0';
      }
     
      // Reposition input to bottom as in chat mode
      const inputContainer = document.getElementById('inputContainer');
      if (inputContainer) {
        inputContainer.style.position = 'fixed';
        inputContainer.style.bottom = '20px';
        inputContainer.style.left = '0';
        inputContainer.style.right = '0';
        inputContainer.style.margin = '0 auto';
      }
    }
   
  recognition.start();
  } catch (error) {
    console.error("Speech recognition error:", error);
    document.body.classList.remove('recording');
  }
};

  recognition.onresult = (event: any) => { // Use 'any' for event type
  document.body.classList.remove('recording');
  const transcript = event.results[0][0].transcript;
  if (transcript.trim() !== '') {
      if (input) {
  input.value = transcript;
      }
    // Trigger the same behavior as clicking the send button
      if (playPauseButton) {
  playPauseButton.click();
      }
   
    // Show processing indicator after submitting speech
    document.body.classList.add('processing');
  }
};

recognition.onend = () => {
  document.body.classList.remove('recording');
};

  recognition.onerror = (event: any) => { // Use 'any' for event type
  // Log error to console but don't show in UI
  console.error("Speech recognition error:", event.error);
  document.body.classList.remove('recording');
};
}

// Function to stop the current task
// Need to use 'let' for socket if we reassign it
let currentSocket = socket; // Assign initial socket to a mutable variable

function stopCurrentTask(): Promise<void> { // Explicitly type Promise as void
  return new Promise((resolve) => {
    if (taskRunning) {
      // If a task is running, stop it
      fetch(`${SERVER_URL}/stop-task`, {
        method: 'POST'
      }).then(res => {
        if (!res.ok) {
          throw new Error(`Server responded with status: ${res.status}`);
        }
        return res.json();
      })
        .then(data => {
          const msg = data.status === "stopped"
            ? "Task stopped for new chat"
            : "";
          if (msg) { // Only append if there's a message
          appendMessage(msg, "stopped");
          }
          if (playPauseButton) {
          playPauseButton.innerHTML = '<i class="fas fa-rocket"></i>';
          }
          taskRunning = false;
          isPaused = false;
         
          // Force disconnect and reconnect the WebSocket to ensure clean state
          if (currentSocket && currentSocket.readyState === WebSocket.OPEN) {
            currentSocket.close();
          }
         
          // Reconnect the socket after a short delay
          setTimeout(() => {
            // Create a new WebSocket connection and assign it
            currentSocket = new WebSocket(WS_URL);
           
            currentSocket.onopen = () => {
              console.log("WebSocket reconnected");
              resolve(); // Resolve with no arguments
            };
           
            currentSocket.onmessage = (event) => {
              const msg = event.data;
              // Remove any loading indicators first
              removeLoadingIndicator();
              // Show thinking indicator before displaying the message
              const thinkingIndicator = createAgentThinkingIndicator();
              setTimeout(() => {
                  if (thinkingIndicator && thinkingIndicator.parentNode) {
                      thinkingIndicator.parentNode.removeChild(thinkingIndicator);
                  }
              appendMessage(msg, "agent");
              if (msg.trim().endsWith("?")) {
                awaitingResponse = true;
              }
              if (msg.trim().startsWith("Task completed")) {
                      if (playPauseButton) {
                playPauseButton.innerHTML = '<i class="fas fa-rocket"></i>';
                      }
                taskRunning = false;
                isPaused = false;
                document.body.classList.remove('processing');
              }
              document.body.classList.remove('processing');
              }, 1200); // Added delay similar to original onmessage
            };
           
            currentSocket.onerror = () => {
              console.error("WebSocket reconnection error");
              resolve(); // Still resolve even on error
            };
          }, 300);
        })
        .catch(error => {
          console.error('Error stopping task:', error);
          resolve(); // Still resolve even on error
        });
    } else {
      // If no task is running, resolve immediately
      resolve();
    }
  });
}

// New Chat button functionality - stop current task first with stronger enforcement
const newChatBtn = document.getElementById('newChatBtn') as HTMLButtonElement | null;
if (newChatBtn) {
  newChatBtn.addEventListener('click', () => {
  // Disable the button temporarily to prevent multiple clicks
  newChatBtn.disabled = true;
  newChatBtn.style.opacity = '0.5';
 
  // Show an immediate visual feedback
  document.body.classList.add('processing');
  appendMessage("Starting new chat...", "stopped");
 
    // First stop any running task using the refactored function
    stopCurrentTask().then(() => {
      // Reset the UI state after task is stopped and socket potentially reconnected
      if (output) {
        output.innerHTML = '';
      }
      if (input) {
        input.value = '';
      }
    taskRunning = false;
    isPaused = false;
    awaitingResponse = false;
   
    // Reset UI to initial state
    document.body.className = 'initial-screen light-mode'; // Reset all classes
   
    // Make sure the welcome message is visible
    const welcomeMsg = document.getElementById('welcomeMessage');
    if (welcomeMsg) {
      welcomeMsg.style.display = 'block';
      welcomeMsg.style.visibility = 'visible';
      welcomeMsg.style.opacity = '1';
      welcomeMsg.style.height = 'auto';
      welcomeMsg.style.margin = '0 0 35px 0';
      welcomeMsg.style.overflow = 'visible';
    }
   
    // Reset input container position
    const inputContainer = document.getElementById('inputContainer');
    if (inputContainer) {
      inputContainer.style.position = '';
      inputContainer.style.bottom = '';
      inputContainer.style.left = '';
      inputContainer.style.right = '';
      inputContainer.style.margin = '0 auto';
      inputContainer.className = 'visible';
    }
   
    // Reset planet animation - using the custom element
    const planetAnimationElement = document.querySelector('browzee-planet-animation') as BrowzeePlanetAnimationElement;
    if (planetAnimationElement) {
      planetAnimationElement.style.display = 'block';
      planetAnimationElement.style.visibility = 'visible';
      planetAnimationElement.style.opacity = '1';
      planetAnimationElement.style.height = '280px';
      planetAnimationElement.style.width = '280px';
      planetAnimationElement.style.margin = '0 auto 20px';
      planetAnimationElement.style.position = 'relative';
      planetAnimationElement.style.overflow = 'visible';
      
      // Force refresh the custom element by removing and re-adding it to the DOM
      const parent = planetAnimationElement.parentNode;
      if (parent) {
        const newPlanetElement = document.createElement('browzee-planet-animation') as BrowzeePlanetAnimationElement;
        parent.replaceChild(newPlanetElement, planetAnimationElement);
      }
    }
   
    // Reset play button
      if (playPauseButton) {
    playPauseButton.innerHTML = '<i class="fas fa-rocket"></i>';
      }
   
    // Remove loading indicator if present
    removeLoadingIndicator();
   
    // Reset processing state
    document.body.classList.remove('processing');
   
    // Re-enable the button after UI is reset
    newChatBtn.disabled = false;
    newChatBtn.style.opacity = '1';
    }).catch(error => {
      console.error('Error in new chat sequence:', error);
    // Re-enable the button even if there was an error
    newChatBtn.disabled = false;
    newChatBtn.style.opacity = '1';
    document.body.classList.remove('processing');
  });
});
}

// Chat History button functionality
const historyChatBtn = document.getElementById('historyChatBtn');
if (historyChatBtn) {
  historyChatBtn.addEventListener('click', () => {
  // Implement chat history functionality here
    console.log('History button clicked');
});
}

// Share button functionality
const shareChatBtn = document.getElementById('shareChatBtn');
if (shareChatBtn) {
  shareChatBtn.addEventListener('click', () => {
  // Share functionality would be implemented here
  console.log('Share button clicked');
});
}

// Add dropdown menu directly in HTML
const dropdownMenu = document.createElement('div');
dropdownMenu.id = 'agentDropdownMenu';
dropdownMenu.style.cssText = `
  display: none;
  position: fixed;
  background: var(--panel);
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.6);
  z-index: 10000;
  width: 320px;
  padding: 12px 0;
  font-size: 14px;
  overflow: hidden;
`;

// Add header to dropdown
const dropdownHeader = document.createElement('div');
dropdownHeader.style.cssText = `
  padding: 8px 15px 15px 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 5px;
`;

const headerTitle = document.createElement('div');
headerTitle.style.cssText = `
  color: var(--subtle);
  font-weight: 500;
  font-size: 14px;
  margin-bottom: 3px;
`;
headerTitle.textContent = 'Model';

const helpIcon = document.createElement('span');
helpIcon.innerHTML = `<i class="far fa-circle-question" style="float: right; opacity: 0.7;"></i>`;
headerTitle.appendChild(helpIcon);

dropdownHeader.appendChild(headerTitle);
dropdownMenu.appendChild(dropdownHeader);

document.body.appendChild(dropdownMenu);

// Populate dropdown with options
const dropdownOptions = [
  {
    value: 'task',
    text: 'Agent Task',
    description: 'Great for performing tasks on the web',
    badge: ''
  },
  {
    value: 'interactive-task',
    text: 'Interactive Agent Task',
    description: 'Ask the agent to follow up with you',
    badge: 'BETA'
  },
  {
    value: 'chat',
    text: 'Chat',
    description: 'Good for writing and exploring ideas',
    badge: 'RESEARCH PREVIEW'
  },
  {
    value: 'chat-this-page',
    text: 'Chat on this Page',
    description: 'Great for discussing current website content',
    badge: ''
  }
];

// Function to update dropdown checkmarks and selection
function updateDropdownSelection(selectedValue: string) {
    const modeSelect = document.getElementById('modeSelect');
    if (modeSelect) (modeSelect as HTMLSelectElement).value = selectedValue; // Cast when accessing value

    const agentDropdownBtn = document.getElementById('agentDropdownBtn');
    const selectedOption = dropdownOptions.find(opt => opt.value === selectedValue);
    if (agentDropdownBtn && selectedOption) {
        const span = agentDropdownBtn.querySelector('span');
        if (span) span.textContent = selectedOption.text;
    }

    // Remove existing checkmarks
    dropdownMenu.querySelectorAll('.dropdown-checkmark').forEach(check => check.remove());

    // Add checkmark to the selected item and update background
    dropdownMenu.querySelectorAll('.dropdown-option').forEach(optionDiv => {
        const div = optionDiv as HTMLDivElement;
        const optionValue = div.dataset['value'];
        // eslint-disable-next-line @typescript-eslint/no-unnecessary-type-assertion
        const rightContainer = div.querySelector('.dropdown-right-container') as HTMLElement | null;

        if (optionValue === selectedValue) {
            div.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
            if (rightContainer) {
                const checkmark = document.createElement('span');
                checkmark.innerHTML = '<i class="fas fa-check"></i>';
                checkmark.className = 'dropdown-checkmark'; // Add class for easier removal
                checkmark.style.cssText = `
                    color: var(--primary);
                    width: 16px;
                    text-align: center;
                    margin-left: 10px; // Add some space
                `;
                rightContainer.appendChild(checkmark);
            }
        } else {
            div.style.backgroundColor = '';
        }
    });
}


// Fill the dropdown menu
dropdownOptions.forEach((option, index) => {
  const optionDiv = document.createElement('div');
  optionDiv.dataset['value'] = option.value; // Use bracket notation
  optionDiv.className = 'dropdown-option'; // Add class for easier selection
  optionDiv.style.cssText = `
    padding: 12px 15px;
    cursor: pointer;
    color: var(--text);
    transition: background-color 0.2s ease;
    user-select: none;
    border-radius: 0;
    position: relative;
    display: flex;
    flex-direction: column;
  `;
 
  // Title and badge container
  const titleContainer = document.createElement('div');
  titleContainer.style.cssText = `
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
    width: 100%;
  `;
 
  // Left side: Title
  const titleSpan = document.createElement('span');
  titleSpan.textContent = option.text;
  titleSpan.style.cssText = `
    font-weight: 500;
    font-size: 15px;
  `;
 
  // Right side: Container for badge and checkmark
  const rightContainer = document.createElement('div');
  rightContainer.className = 'dropdown-right-container'; // Add class for selection
  rightContainer.style.cssText = `
    display: flex;
    align-items: center;
    gap: 10px;
  `;
 
  // Badge
  if (option.badge) {
    const badge = document.createElement('span');
    badge.textContent = option.badge;
    badge.dataset['badge'] = option.badge; // Use bracket notation
    badge.style.cssText = `
      background-color: rgba(255, 255, 255, 0.1);
      color: var(--subtle);
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.5px;
      border: 1px solid rgba(255, 255, 255, 0.15);
    `;
   
    // Add different styles based on badge type
    if (option.badge === 'BETA') {
      badge.style.cssText += `
        background-color: rgba(139, 92, 246, 0.15);
        color: rgba(139, 92, 246, 0.9);
        border: 1px solid rgba(139, 92, 246, 0.3);
      `;
    } else if (option.badge === 'RESEARCH PREVIEW') {
      badge.style.cssText += `
        background-color: rgba(59, 130, 246, 0.15);
        color: rgba(59, 130, 246, 0.9);
        border: 1px solid rgba(59, 130, 246, 0.3);
      `;
    }
   
    rightContainer.appendChild(badge);
  }
 
  titleContainer.appendChild(titleSpan);
  titleContainer.appendChild(rightContainer); // Add right container
  optionDiv.appendChild(titleContainer);
 
  // Description
  const descriptionDiv = document.createElement('div');
  descriptionDiv.textContent = option.description;
  descriptionDiv.style.cssText = `
    color: var(--subtle);
    font-size: 13px;
  `;
  optionDiv.appendChild(descriptionDiv);
 
  optionDiv.onmouseover = () => {
    const modeSelect = document.getElementById('modeSelect');
    // Cast only when accessing value, use optional chaining
    if ((modeSelect as HTMLSelectElement)?.value !== option.value) {
    optionDiv.style.backgroundColor = 'var(--hover-bg)';
    }
  };
 
  optionDiv.onmouseout = () => {
    const modeSelect = document.getElementById('modeSelect');
    // Cast only when accessing value, use optional chaining
    if ((modeSelect as HTMLSelectElement)?.value !== option.value) {
      optionDiv.style.backgroundColor = '';
    }
  };
 
  optionDiv.onclick = () => {
    // Use the selectMode function instead
    selectMode(option.value, option.text);
   
    // Update the dropdown selection visual feedback
    updateDropdownSelection(option.value);
   
    if (option.value === "chat-this-page" || option.value === "chat") {
      if (playPauseButton) {
      playPauseButton.innerHTML = '<i class="fas fa-rocket"></i>';
      }
      taskRunning = false;
      isPaused = false;
    }
   
    dropdownMenu.style.display = 'none';
  };
 
  dropdownMenu.appendChild(optionDiv);
 
  // Add separator after the second option
  if (index === 1) {
    const separator = document.createElement('div');
    separator.style.cssText = `
      height: 1px;
      background-color: rgba(255, 255, 255, 0.1);
      margin: 8px 0;
    `;
    dropdownMenu.appendChild(separator);
  }
});

// Initialize dropdown selection
const initialMode = (document.getElementById('modeSelect') as HTMLSelectElement | null)?.value || 'task';
updateDropdownSelection(initialMode);


// Add "More models" at the bottom
const moreModelsDiv = document.createElement('div');
moreModelsDiv.style.cssText = `
  padding: 12px 15px;
  cursor: pointer;
  color: var(--text);
  transition: background-color 0.2s ease;
  user-select: none;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;
moreModelsDiv.innerHTML = `
  <span style="font-weight: 500;">More models</span>
  <i class="fas fa-chevron-right" style="font-size: 12px; opacity: 0.7;"></i>
`;

moreModelsDiv.onmouseover = () => {
  moreModelsDiv.style.backgroundColor = 'var(--hover-bg)';
};

moreModelsDiv.onmouseout = () => {
  moreModelsDiv.style.backgroundColor = '';
};

dropdownMenu.appendChild(moreModelsDiv);

// Toggle dropdown on button click
const agentDropdownBtn = document.getElementById('agentDropdownBtn');
if (agentDropdownBtn) {
  console.log('Found agentDropdownBtn, adding click event');
  agentDropdownBtn.addEventListener('click', function(e) {
    console.log('Task Mode button clicked');
    e.preventDefault();
    e.stopPropagation();
 
  const rect = this.getBoundingClientRect();
  dropdownMenu.style.top = (rect.bottom + 5) + 'px';
  dropdownMenu.style.left = rect.left + 'px';
 
    // Toggle dropdown visibility
  if (dropdownMenu.style.display === 'none' || dropdownMenu.style.display === '') {
    dropdownMenu.style.display = 'block';
      console.log('Dropdown menu opened');
  } else {
    dropdownMenu.style.display = 'none';
      console.log('Dropdown menu closed');
  }
  });
}

// Close dropdown when clicking elsewhere
document.addEventListener('click', function(e) {
  if (e.target instanceof Node) {
    // Log click target for debugging
    console.log('Document click detected on:', e.target);
    
  // Check if the click target is a Node before calling contains
    const clickedOnMenu = dropdownMenu.contains(e.target);
    const clickedOnButton = agentDropdownBtn && agentDropdownBtn.contains(e.target);
    
    console.log('Click on menu:', clickedOnMenu);
    console.log('Click on button:', clickedOnButton);
    
    // Close only if click is outside menu and button
    if (!clickedOnMenu && !clickedOnButton) {
      console.log('Clicked outside menu, closing dropdown');
    dropdownMenu.style.display = 'none';
    }
  }
});

// הוספת פונקציונליות התפריט הנפתח - שלב 1: בחירת האפשרות
// Function to handle mode selection
function selectMode(mode: string, displayText: string) {
  const modeSelect = document.getElementById('modeSelect') as HTMLSelectElement;
  if (modeSelect) {
    modeSelect.value = mode;
  }
  
  const btnTextSpan = agentDropdownBtn?.querySelector('span');
  if (btnTextSpan) {
    btnTextSpan.textContent = displayText;
  }
  
  dropdownMenu.style.display = 'none';
}

// Planet animation code was moved to browzee_planet_animation.ts
// and replaced with a custom element

// Add server connection check function
function checkServerConnection() {
  fetch(`${SERVER_URL}/run-task`, {
    method: 'HEAD'
  })
  .then(response => {
    if (!response.ok) {
      appendMessage("Server connection warning: The agent server is not responding correctly", "warning");
    }
  })
  .catch(() => {
    appendMessage("Server connection error: Cannot connect to the agent server", "error");
  });
}

// Check server connection on page load
window.addEventListener('load', () => {
  checkServerConnection();
  
  // Initial focus on input
  if (input) {
    setTimeout(() => {
      input.focus();
    }, 500);
  }
});

// בדיקת חיבור לשרת באופן יזום בעת טעינת הדף
window.addEventListener('DOMContentLoaded', () => {
  console.log('DOMContentLoaded event fired');
  
  // בדיקה אם כל האלמנטים הנחוצים קיימים
  console.log('Checking essential elements:');
  console.log('- Input element:', input ? 'found' : 'missing');
  console.log('- Play/Pause button:', playPauseButton ? 'found' : 'missing');
  console.log('- Stop button:', stopButton ? 'found' : 'missing');
  console.log('- Output container:', output ? 'found' : 'missing');
  console.log('- agentDropdownBtn:', agentDropdownBtn ? 'found' : 'missing');
  
  // ניסיון חיבור ראשוני לשרת
  console.log(`Testing connection to server at ${SERVER_URL}`);
  fetch(`${SERVER_URL}`, {
    method: 'GET',
    mode: 'no-cors'
  })
  .then(response => {
    console.log('Server responded with status:', response.status);
    if (response.ok) {
      console.log('Successfully connected to server');
        } else {
      console.warn('Server connection issue:', response.status, response.statusText);
    }
  })
  .catch(error => {
    console.error('Server connection error:', error);
    appendMessage(`Server connection error: ${error.message}. Check if the server is running at ${SERVER_URL}`, "error");
  });
  
  // מיקוד על האלמנט input
  if (input) {
    setTimeout(() => {
      input.focus();
      console.log('Input field focused');
    }, 500);
  }
});