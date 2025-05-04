# BrowZee AI Assistant - Smart Autocomplete with Gemini API

This extension provides a smart autocomplete feature for the BrowZee AI Assistant, powered by Google's Gemini API. It offers context-aware suggestions based on user input, conversation history, and current mode.

## Features

- Powered by Google's Gemini API for intelligent suggestions
- Automatic server startup with the extension
- Automatic environment configuration
- Context-aware suggestions based on current mode (task, search, etc.)
- Conversation history integration
- Real-time loading indicators
- Smooth animations and transitions
- Keyboard navigation support
- Mobile-friendly design
- Graceful fallback for API errors

## Setup

1. Install dependencies:
```bash
cd extensions/browzee_assistant
npm install
```

2. Build the extension:
```bash
npm run build
```

3. Load the extension in Chrome:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `extensions/browzee_assistant` directory

The server will automatically start when the extension is loaded and stop when the extension is uninstalled or disabled. The environment configuration is handled automatically.

## Usage

1. Type in the input field to see AI-powered suggestions
2. Use arrow keys (↑/↓) to navigate through suggestions
3. Press Enter to select a suggestion
4. Click on a suggestion to select it
5. Press Escape to close the suggestions

## Development

The autocomplete feature consists of these main components:

1. `index.js` - Frontend implementation with the SmartAutocomplete class
2. `styles.css` - Styling for the autocomplete interface
3. `server.js` - Backend API using Gemini for generating suggestions
4. `background.js` - Manages the server process and environment configuration
5. `webpack.config.js` - Bundles the background script

### Gemini API Integration

The server uses Google's Gemini API to generate intelligent suggestions. The API key and other environment variables are automatically configured when the extension starts. The configuration is stored in the `.env` file, which is managed automatically by the background script.

## Customization

You can customize the appearance by modifying the CSS in `styles.css`. The main classes to modify are:

- `.autocomplete-loading` - Loading indicator
- `.autocomplete-item` - Individual suggestion items
- `#autocompleteContainer` - Suggestions container
- `#input` - Input field

## Contributing

Feel free to submit issues and enhancement requests! 