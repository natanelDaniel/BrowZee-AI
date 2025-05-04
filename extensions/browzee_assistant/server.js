require('dotenv').config();
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const app = express();
const port = process.env.PORT || 8010;

app.use(cors({
  origin: '*',
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json());

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';

const generateGeminiRequest = (input, context, history) => {
  let systemPrompt = "You are a helpful AI assistant providing smart autocomplete suggestions. ";
  systemPrompt += "Always respond with exactly 5 suggestions in JSON format: [{ \"title\": \"...\", \"subtitle\": \"...\" }]. ";
  systemPrompt += "Make suggestions relevant to the input and context.";

  let userPrompt = `Input: "${input}"\n`;
  
  if (context.mode) {
    userPrompt += `Mode: ${context.mode}\n`;
  }
  
  if (history && history.length > 0) {
    userPrompt += "Recent conversation:\n";
    history.slice(-3).forEach(msg => {
      userPrompt += `${msg.role}: ${msg.content.substring(0, 50)}...\n`;
    });
  }

  return {
    contents: [
      {
        role: "user",
        parts: [
          { text: systemPrompt },
          { text: userPrompt }
        ]
      }
    ],
    generationConfig: {
      temperature: 0.7,
      topK: 40,
      topP: 0.95,
      maxOutputTokens: 1024,
    }
  };
};

app.post('/api/autocomplete', async (req, res) => {
  const { prompt, context, history } = req.body;
  
  if (!prompt) {
    return res.status(400).json({ error: 'Prompt is required' });
  }

  try {
    const response = await axios.post(
      `${GEMINI_API_URL}?key=${GEMINI_API_KEY}`,
      generateGeminiRequest(prompt, context, history)
    );

    // Extract and parse the JSON response from Gemini
    const responseText = response.data.candidates[0].content.parts[0].text;
    let suggestions;
    
    try {
      suggestions = JSON.parse(responseText);
    } catch (parseError) {
      console.error('Error parsing Gemini response:', parseError);
      throw new Error('Invalid response format from Gemini');
    }

    // Validate the suggestions format
    if (!Array.isArray(suggestions) || suggestions.length === 0) {
      throw new Error('Invalid suggestions format');
    }

    // Ensure each suggestion has the required fields
    suggestions = suggestions.map(suggestion => ({
      title: suggestion.title || '',
      subtitle: suggestion.subtitle || ''
    }));

    res.json({ suggestions });
  } catch (error) {
    console.error('Error generating suggestions:', error);
    
    // Fallback to basic suggestions if Gemini API fails
    const fallbackSuggestions = [
      {
        title: `Search for "${prompt}"`,
        subtitle: 'Perform a web search'
      },
      {
        title: `Explain "${prompt}"`,
        subtitle: 'Get a detailed explanation'
      }
    ];
    
    res.json({ suggestions: fallbackSuggestions });
  }
});

app.listen(port, () => {
  console.log(`BrowZee Autocomplete API running on port ${port}`);
}); 