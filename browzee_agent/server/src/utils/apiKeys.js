// API keys for various AI models

export const AI_API_KEYS = {
  OPENAI: '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',
  GROK: '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',
  XAI: 'xai-CXLn9LJRVLjaQvAhHEvIQeaQ6xlRZkdYVUUrBLCxhNWBlHUhNRe4VOs2GXUFdMLIsPPZrFnUzMnnzLHe',
  GEMINI: 'AIzaSyAQ29sFDclVfg40kHzArE7jpmBc8h3AdoU'
};

// Function to get API key for a specific model
export const getApiKey = (modelType) => {
  return AI_API_KEYS[modelType.toUpperCase()] || null;
};

// Get headers with API key for a specific model
export const getModelHeaders = (modelType) => {
  const key = getApiKey(modelType);
  if (!key) return {};
  
  // Different APIs use different header formats
  switch(modelType.toUpperCase()) {
    case 'OPENAI':
      return {
        'Authorization': `Bearer ${key}`,
        'Content-Type': 'application/json'
      };
    case 'GROK':
      return {
        'Authorization': `Bearer ${key}`,
        'Content-Type': 'application/json'
      };
    case 'XAI':
      return {
        'x-api-key': key,
        'Content-Type': 'application/json'
      };
    case 'GEMINI':
      return {
        'x-goog-api-key': key,
        'Content-Type': 'application/json'
      };
    default:
      return {
        'Authorization': `Bearer ${key}`,
        'Content-Type': 'application/json'
      };
  }
}; 