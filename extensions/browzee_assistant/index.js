const isExtension = window.location.protocol === 'chrome-extension:';

const BACKEND_HTTP = isExtension ? 'http://new-server-name:8000' : 'http://127.0.0.1:8000';
const BACKEND_WS = isExtension ? 'ws://new-server-name:8000/ws/status' : 'ws://127.0.0.1:8000/ws/status';
document.addEventListener('DOMContentLoaded', () => {
  // Safe element references - add null checks
  const output = document.getElementById('output');
  const input = document.getElementById('input');
  const playPauseButton = document.getElementById('playPause');
  const stopButton = document.getElementById('stop');
  const themeIconBtn = document.getElementById('themeIconBtn');
  const newChatBtn = document.getElementById('newChatBtn');
  const modeSelect = document.getElementById('modeSelect');
  const modeButton = document.getElementById('modeButton');
  const modeMenuDropdown = document.getElementById('modeMenuDropdown');
  
  // Global state variables
  let socket = null;
  let taskRunning = false;
  let awaitingResponse = false;
  let isPaused = false;
  let loadingIndicator = null;
  let currentMode = "task";

  // Initialize mode selector functionality
  if (modeButton && modeMenuDropdown) {
    // Toggle dropdown visibility when button is clicked
    modeButton.addEventListener('click', (e) => {
      e.stopPropagation();
      modeMenuDropdown.classList.toggle('show');
    });

    // Close dropdown when clicking elsewhere
    document.addEventListener('click', () => {
      if (modeMenuDropdown.classList.contains('show')) {
        modeMenuDropdown.classList.remove('show');
      }
    });

    // Handle mode selection
    const modeItems = document.querySelectorAll('.mode-item');
    modeItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.stopPropagation();
        
        // Update selected mode
        currentMode = item.getAttribute('data-value');
        
        // Update modeSelect to keep in sync
        if (modeSelect) {
          modeSelect.value = currentMode;
        }
        
        // Update active state in UI
        modeItems.forEach(mi => mi.classList.remove('active'));
        item.classList.add('active');
        
        // Update button icon/appearance based on mode
        updateModeButtonAppearance(currentMode);
        
        // Close dropdown
        modeMenuDropdown.classList.remove('show');
      });
    });
  }

  // Update mode button appearance based on selected mode
  function updateModeButtonAppearance(mode) {
    if (!modeButton) return;
    
    // Remove previous icon classes
    modeButton.querySelector('i').className = '';
    
    // Set appropriate icon for the mode
    let iconClass = 'fas ';
    switch (mode) {
      case 'task':
        iconClass += 'fa-tasks';
        modeButton.title = 'Agent Task';
        break;
      case 'interactive-task':
        iconClass += 'fa-exchange-alt';
        modeButton.title = 'Interactive Task';
        break;
      case 'chat':
        iconClass += 'fa-comment';
        modeButton.title = 'Chat';
        break;
      case 'chat-this-page':
        iconClass += 'fa-file-alt';
        modeButton.title = 'Chat on this Page';
        break;
      default:
        iconClass += 'fa-tasks';
        modeButton.title = 'Agent Task';
    }
    
    modeButton.querySelector('i').className = iconClass;
  }

  // Initialize with the current mode
  if (modeSelect && modeSelect.value) {
    currentMode = modeSelect.value;
    updateModeButtonAppearance(currentMode);
  }

  // Add theme toggle functionality
  if (themeIconBtn) {
    themeIconBtn.addEventListener('click', toggleTheme);
  }

  function toggleTheme() {
    document.body.classList.toggle('light-mode');
    const isLight = document.body.classList.contains('light-mode');
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
      themeIcon.style.transform = isLight ? 'rotate(180deg)' : 'rotate(0deg)';
    }
  }

  // Create loading indicator function
  function createLoadingIndicator() {
    if (!output) return null;
    
    removeLoadingIndicator();
    
    loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = `
      <div class="dot-typing">
        <div></div>
        <div></div>
        <div></div>
      </div>
    `;
    output.appendChild(loadingIndicator);
    scrollToBottom(false);
    return loadingIndicator;
  }

  // Create agent thinking indicator between messages
  function createAgentThinkingIndicator() {
    if (!output) return null;
    
    const thinkingIndicator = document.createElement('div');
    thinkingIndicator.className = 'agent-thinking-indicator';
    thinkingIndicator.innerHTML = `
      <div class="typing-dots">
        <div></div>
        <div></div>
        <div></div>
      </div>
    `;
    output.appendChild(thinkingIndicator);
    
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

  // Initialize WebSocket connection
  function connectWebSocket() {
    // Try both localhost and 127.0.0.1
    socket = new WebSocket(BACKEND_WS);
    
    socket.onopen = () => {
      console.log('WebSocket connected');
    };
    
    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      // Fallback to 127.0.0.1 if localhost fails
      if (socket.url.includes('localhost')) {
        socket = new WebSocket('ws://127.0.0.1:8000/ws/status');
      }
    };
    
    socket.onmessage = (event) => {
      if (!output || !playPauseButton) return;
      
      const msg = event.data;
      
      removeLoadingIndicator();
      
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
          playPauseButton.innerHTML = '<i class="fas fa-rocket"></i>';
          playPauseButton.classList.remove('task-running');
          taskRunning = false;
          isPaused = false;
          document.body.classList.remove('processing');
        }
        
        document.body.classList.remove('processing');
      }, 1200);
    };
    
    socket.onclose = () => {
      console.log('WebSocket closed. Trying to reconnect in 5 seconds...');
      setTimeout(connectWebSocket, 5000);
    };
  }
  
  // Initial connection
  connectWebSocket();

  // Play/Pause button functionality
  if (playPauseButton) {
    playPauseButton.addEventListener('click', function() {
      if (!input || !output) return;
      
      const text = input.value.trim();
      // Use currentMode instead of reading directly from modeSelect
      const mode = currentMode;
      
      if (!taskRunning) {
        if (!text) return;
        
        // Enter chat mode
        document.body.classList.add('chat-active');
        document.body.classList.remove('initial-screen');
        
        // Show processing indicator
        document.body.classList.add('processing');
        
        input.value = '';
        appendMessage(text, "task");
        
        // Send request to server
        fetch(`${BACKEND_HTTP}/run-task`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ task: text, mode: mode })
        }).catch(error => {
          console.error('Error:', error);
          // Fallback to 127.0.0.1
          fetch('http://127.0.0.1:8000/run-task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: text, mode: mode })
          }).catch(e => console.error('Error:', e));
        });
        
        playPauseButton.innerHTML = '<i class="fas fa-pause"></i>';
        playPauseButton.classList.add('task-running');
        taskRunning = true;
        isPaused = false;
      } else {
        if (awaitingResponse) {
          if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(text);
          }
          appendMessage(text, "task");
          input.value = '';
          awaitingResponse = false;
          document.body.classList.add('processing');
        } else {
          isPaused = !isPaused;
          const action = isPaused ? "pause" : "resume";
          playPauseButton.innerHTML = isPaused ? '<i class="fas fa-play" style="transform: rotate(0deg);"></i>' : '<i class="fas fa-pause"></i>';
          
          fetch(`${BACKEND_HTTP}/${action}-task`, {
            method: 'POST'
          }).catch(() => {
            fetch(`http://127.0.0.1:8000/${action}-task`, {
              method: 'POST'
            });
          });
        }
      }
    });
  }

  // Stop button functionality 
  if (stopButton) {
    stopButton.addEventListener('click', () => {
      fetch(`${BACKEND_HTTP}/stop-task`, {
        method: 'POST'
      }).then(res => res.json())
        .then(data => {
          const msg = data.status === "stopped"
            ? "🚩 Task stopped"
            : "⚠️ No active task to stop";
          appendMessage(msg, "stopped");
          if (playPauseButton) {
            playPauseButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
          }
          taskRunning = false;
          isPaused = false;
          
          removeLoadingIndicator();
          
          document.body.classList.remove('processing');
        }).catch(error => console.error('Error:', error));
    });
  }

  // Input enter key handler
  if (input) {
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey && playPauseButton) {
        e.preventDefault();
        playPauseButton.click();
      }
    });
  }

  // Ensure message is scrolled into view properly
  function scrollToBottom(smooth = true) {
    if (!output) return;
    
    const lastMessage = output.lastElementChild;
    if (lastMessage) {
      lastMessage.scrollIntoView({
        behavior: smooth ? 'smooth' : 'auto',
        block: 'start'
      });
      
      setTimeout(() => {
        output.scrollTop += 120; // Adjusted for side panel
      }, smooth ? 150 : 0);
    }
  }

  function adjustOutputPadding() {
    const inputContainer = document.getElementById('inputContainer');
    
    if (inputContainer && output) {
      const inputHeight = inputContainer.offsetHeight + 25; // Reduced padding
      output.style.paddingBottom = `${inputHeight}px`;
    }
  }

  if (window) {
    window.addEventListener('load', adjustOutputPadding);
    window.addEventListener('resize', adjustOutputPadding);
  }

  function appendMessage(text, className) {
    if (!output) return;
    
    const msg = document.createElement('div');
    
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
      
      // Add all buttons to the action container
      messageActions.appendChild(likeBtn);
      messageActions.appendChild(dislikeBtn);
      messageActions.appendChild(copyBtn);
      
      // Add the action container to the message
      msg.appendChild(messageActions);
    }
    
    msg.textContent = text;
    msg.innerHTML = text.replace(/\n/g, '<br>');
    output.appendChild(msg);
    adjustOutputPadding();
    scrollToBottom();
  }

  // Create planet animation - simplified for side panel
  (function() {
    const planetSystem = document.getElementById('planetSystem');
    if (!planetSystem) return;
    
    const colors = ['#f9a8d4', '#93c5fd', '#67e8f9', '#a78bfa'];
    
    // Clear existing stars first
    planetSystem.innerHTML = '';
    
    // Add the planet
    const planet = document.createElement('div');
    planet.id = 'planet';
    planetSystem.appendChild(planet);
    
    // Add fewer stars for side panel
    for (let i = 0; i < 12; i++) {
      const wrapper = document.createElement('div');
      wrapper.className = 'orbit-wrapper';

      const star = document.createElement('div');
      star.className = 'star';

      const size = 4 + Math.random() * 5; // Smaller stars
      star.style.width = `${size}px`;
      star.style.height = `${size}px`;

      const color = colors[Math.floor(Math.random() * colors.length)];
      star.style.backgroundColor = color;
      star.style.boxShadow = `0 0 8px ${color}`;

      const radius = 60 + Math.random() * 40; // Smaller radius
      const yOffset = -30 + Math.random() * 60; // Smaller offset
      star.style.left = `${radius}px`;
      star.style.top = `${yOffset}px`;

      const duration = 15 + Math.random() * 25;
      wrapper.style.animationDuration = `${duration}s`;
      wrapper.style.animationDelay = `-${Math.random() * duration}s`;

      wrapper.appendChild(star);
      planetSystem.appendChild(wrapper);
    }
  })();

  // New Chat button functionality - with null checks
  if (newChatBtn) {
    newChatBtn.addEventListener('click', () => {
      newChatBtn.disabled = true;
      
      fetch(`${BACKEND_HTTP}/stop-task`, {
        method: 'POST'
      })
      .then(res => res.json())
      .then(() => {
        // Reset the UI state
        if (output) output.innerHTML = '';
        if (input) input.value = '';
        taskRunning = false;
        isPaused = false;
        awaitingResponse = false;
        
        // Reset UI to initial state
        document.body.className = 'initial-screen light-mode';
        
        // Make welcome message visible
        const welcomeMsg = document.getElementById('welcomeMessage');
        if (welcomeMsg) {
          welcomeMsg.style.display = 'block';
          welcomeMsg.style.visibility = 'visible';
        }
        
        // Reset planet animation
        const planetSystem = document.getElementById('planetSystem');
        if (planetSystem) {
          planetSystem.style.display = 'block';
          planetSystem.style.visibility = 'visible';
          planetSystem.style.opacity = '1';
        }
        
        // Reset play button
        if (playPauseButton) {
          playPauseButton.innerHTML = '<i class="fas fa-rocket"></i>';
        }
        
        // Re-enable button
        newChatBtn.disabled = false;
      })
      .catch(error => {
        console.error('Error stopping task:', error);
        newChatBtn.disabled = false;
      });
    });
  }

  // Smart Autocomplete functionality
  class SmartAutocomplete {
    constructor() {
      this.container = document.getElementById('autocompleteContainer');
      this.input = document.getElementById('input');
      this.selectedIndex = -1;
      this.suggestions = [];
      this.setupEventListeners();
      this.debounceTimeout = null;
      this.loadingIndicator = this.createLoadingIndicator();
    }

    createLoadingIndicator() {
      const indicator = document.createElement('div');
      indicator.className = 'autocomplete-loading';
      indicator.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i>';
      this.input.parentNode.appendChild(indicator);
      return indicator;
    }

    setupEventListeners() {
      this.input.addEventListener('input', this.handleInput.bind(this));
      this.input.addEventListener('keydown', this.handleKeyDown.bind(this));
      this.container.addEventListener('click', this.handleClick.bind(this));
      document.addEventListener('click', this.handleDocumentClick.bind(this));
    }

    handleInput(event) {
      const query = event.target.value.trim();
      
      // Clear previous timeout
      if (this.debounceTimeout) {
        clearTimeout(this.debounceTimeout);
      }
      
      if (query.length > 0) {
        // Show loading indicator
        this.loadingIndicator.classList.add('visible');
        
        // Debounce the API call
        this.debounceTimeout = setTimeout(() => {
          this.fetchSuggestions(query);
        }, 200);
      } else {
        this.hideSuggestions();
        this.loadingIndicator.classList.remove('visible');
      }
    }

    async fetchSuggestions(query) {
      try {
        updateFeedbackIndicator('waiting');
        
        // Try fetching from multiple endpoints - first attempt
        let response;
        let fetchError;
        
        try {
          // Try new-server-name first (if in extension)
          if (isExtension) {
            response = await fetch('http://new-server-name:8000/api/autocomplete', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                prompt: query,
                context: this.getContext(),
                history: this.getHistory()
              })
            });
          } else {
            // Try localhost if not in extension
            response = await fetch('http://localhost:8000/api/autocomplete', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                prompt: query,
                context: this.getContext(),
                history: this.getHistory()
              })
            });
          }
        } catch (error) {
          console.log('First endpoint failed, trying fallback:', error);
          fetchError = error;
        }
        
        // If first attempt failed, try the fallback
        if (!response || !response.ok) {
          console.log('Trying fallback endpoint...');
          try {
            response = await fetch('http://127.0.0.1:8000/api/autocomplete', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                prompt: query,
                context: this.getContext(),
                history: this.getHistory()
              })
            });
          } catch (error) {
            console.error('Both endpoints failed:', error);
            throw fetchError || error;
          }
        }
        
        if (!response.ok) {
          throw new Error(`Failed to fetch suggestions: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        this.suggestions = data.suggestions;
        this.showSuggestions();
        updateFeedbackIndicator('connected');
      } catch (error) {
        console.error('Error fetching suggestions:', error);
        this.hideSuggestions();
        updateFeedbackIndicator('error');
      } finally {
        this.loadingIndicator.classList.remove('visible');
      }
    }

    getContext() {
      // Get the current mode and any other relevant context
      const modeSelect = document.getElementById('modeSelect');
      const currentMode = modeSelect ? modeSelect.value : 'task';
      
      // Get current page context if available
      const pageContext = {
        url: window.location.href,
        title: document.title,
        // Add any other page-specific context
      };
      
      return {
        mode: currentMode,
        page: pageContext,
        timestamp: new Date().toISOString(),
        // Add any other context information here
      };
    }

    getHistory() {
      // Get recent messages or interactions for context
      const messages = document.querySelectorAll('.message');
      const recentMessages = Array.from(messages)
        .slice(-5) // Get last 5 messages
        .map(msg => ({
          role: msg.classList.contains('agent') ? 'assistant' : 'user',
          content: msg.textContent,
          timestamp: msg.dataset.timestamp || new Date().toISOString()
        }));
      
      return recentMessages;
    }

    showSuggestions() {
      this.container.innerHTML = '';
      this.suggestions.forEach((suggestion, index) => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.dataset.index = index;

        const title = document.createElement('div');
        title.className = 'title';
        title.textContent = suggestion.title;
        item.appendChild(title);

        if (suggestion.subtitle) {
          const subtitle = document.createElement('div');
          subtitle.className = 'subtitle';
          subtitle.textContent = suggestion.subtitle;
          item.appendChild(subtitle);
        }

        this.container.appendChild(item);
      });
      this.container.classList.add('visible');
    }

    hideSuggestions() {
      this.container.classList.remove('visible');
      this.selectedIndex = -1;
    }

    handleKeyDown(event) {
      if (!this.container.classList.contains('visible')) return;

      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          this.selectNext();
          break;
        case 'ArrowUp':
          event.preventDefault();
          this.selectPrevious();
          break;
        case 'Enter':
          event.preventDefault();
          this.selectCurrent();
          break;
        case 'Escape':
          this.hideSuggestions();
          break;
      }
    }

    selectNext() {
      this.selectedIndex = (this.selectedIndex + 1) % this.suggestions.length;
      this.updateSelection();
    }

    selectPrevious() {
      this.selectedIndex = (this.selectedIndex - 1 + this.suggestions.length) % this.suggestions.length;
      this.updateSelection();
    }

    updateSelection() {
      const items = this.container.querySelectorAll('.autocomplete-item');
      items.forEach((item, index) => {
        item.classList.toggle('selected', index === this.selectedIndex);
      });
    }

    selectCurrent() {
      if (this.selectedIndex >= 0 && this.selectedIndex < this.suggestions.length) {
        this.input.value = this.suggestions[this.selectedIndex].title;
        this.hideSuggestions();
        // Trigger input event to update the UI
        this.input.dispatchEvent(new Event('input'));
      }
    }

    handleClick(event) {
      const item = event.target.closest('.autocomplete-item');
      if (item) {
        this.selectedIndex = parseInt(item.dataset.index);
        this.selectCurrent();
      }
    }

    handleDocumentClick(event) {
      if (!this.container.contains(event.target) && event.target !== this.input) {
        this.hideSuggestions();
      }
    }
  }

  // Initialize Smart Autocomplete when the page loads
  new SmartAutocomplete();

  // Add feedback micro-indicator
  const feedbackIndicator = document.createElement('div');
  feedbackIndicator.id = 'feedbackIndicator';
  feedbackIndicator.style.position = 'fixed';
  feedbackIndicator.style.bottom = '10px';
  feedbackIndicator.style.right = '10px';
  feedbackIndicator.style.padding = '5px 10px';
  feedbackIndicator.style.borderRadius = '5px';
  feedbackIndicator.style.fontSize = '12px';
  feedbackIndicator.style.color = '#fff';
  feedbackIndicator.style.zIndex = '10001';
  document.body.appendChild(feedbackIndicator);

  function updateFeedbackIndicator(status) {
    switch (status) {
      case 'connected':
        feedbackIndicator.textContent = '🟢 מחובר';
        feedbackIndicator.style.backgroundColor = '#10b981';
        break;
      case 'waiting':
        feedbackIndicator.textContent = '🟡 ממתין לשרת autocomplete';
        feedbackIndicator.style.backgroundColor = '#f59e0b';
        break;
      case 'error':
        feedbackIndicator.textContent = '🔴 שגיאה';
        feedbackIndicator.style.backgroundColor = '#ef4444';
        break;
    }
  }

  // Example usage
  updateFeedbackIndicator('connected');
}); 