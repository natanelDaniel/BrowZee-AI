import axios from 'axios';
import ModelRequest from '../models/ModelRequest.js';
import Model from '../models/Model.js';
import ErrorResponse from '../utils/errorHandler.js';
import { getModelHeaders } from '../utils/apiKeys.js';

// @desc    Create new model request
// @route   POST /api/models/:id/request
// @access  Private
export const createModelRequest = async (req, res, next) => {
  try {
    const model = await Model.findById(req.params.id);

    if (!model) {
      return next(
        new ErrorResponse(`Model not found with id of ${req.params.id}`, 404)
      );
    }

    // Make sure user is authorized to use the model
    if (!model.isPublic && model.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return next(
        new ErrorResponse(`User ${req.user.id} is not authorized to use this model`, 403)
      );
    }

    // Create the initial request
    const modelRequest = await ModelRequest.create({
      user: req.user.id,
      model: model._id,
      input: req.body
    });

    // Get the model provider
    const modelType = model.provider || 'OTHER';
    
    // Get headers for the model type
    const headers = getModelHeaders(modelType);
    
    // Add custom API key from model if available
    if (model.apiKey) {
      if (modelType === 'XAI') {
        headers['x-api-key'] = model.apiKey;
      } else {
        headers['Authorization'] = `Bearer ${model.apiKey}`;
      }
    }

    try {
      // Format request body based on provider
      let requestBody = {
        ...req.body,
        ...model.parameters
      };
      
      // Specific formatting for different providers
      if (modelType === 'OPENAI') {
        // If not already formatted for OpenAI
        if (!requestBody.messages && requestBody.prompt) {
          requestBody = {
            model: model.parameters.model || 'gpt-3.5-turbo',
            messages: [{ role: 'user', content: requestBody.prompt }],
            temperature: model.parameters.temperature || 0.7,
            max_tokens: requestBody.max_tokens || model.parameters.max_tokens || 1000
          };
        }
      } else if (modelType === 'GEMINI') {
        // Format for Gemini API
        if (!requestBody.contents && requestBody.prompt) {
          requestBody = {
            contents: [{ parts: [{ text: requestBody.prompt }] }],
            generationConfig: {
              temperature: model.parameters.temperature || 0.7,
              maxOutputTokens: requestBody.max_tokens || model.parameters.max_tokens || 1000
            }
          };
        }
        
        // For Gemini API, we need to add the API key as a URL parameter instead of header
        const apiKey = headers['x-goog-api-key'];
        delete headers['x-goog-api-key']; // Remove from headers
        
        // Add API key to the endpoint URL
        const endpoint = model.endpoint.includes('?') 
          ? `${model.endpoint}&key=${apiKey}` 
          : `${model.endpoint}?key=${apiKey}`;
          
        // Make the actual API call to the model with URL parameter for API key
        const modelResponse = await axios.post(endpoint, requestBody, { headers });
        
        // Update the model request with the response
        modelRequest.output = modelResponse.data;
        modelRequest.status = 'success';
        modelRequest.completedAt = Date.now();
        await modelRequest.save();
        
        res.status(200).json({
          success: true,
          data: modelRequest
        });
        return; // Exit early since we've already handled the Gemini case
      }
      
      // For non-Gemini models, make the normal API call
      const modelResponse = await axios.post(model.endpoint, requestBody, { headers });

      // Update the model request with the response
      modelRequest.output = modelResponse.data;
      modelRequest.status = 'success';
      modelRequest.completedAt = Date.now();
      await modelRequest.save();

      res.status(200).json({
        success: true,
        data: modelRequest
      });
    } catch (error) {
      // Update the model request with the error
      modelRequest.status = 'error';
      modelRequest.error = error.message || 'Error calling external model API';
      modelRequest.completedAt = Date.now();
      await modelRequest.save();

      return next(
        new ErrorResponse(`Error calling model API: ${error.message}`, 500)
      );
    }
  } catch (err) {
    next(err);
  }
};

// @desc    Create vision request (without schema)
// @route   POST /api/models/:id/vision
// @access  Private
export const createVisionRequest = async (req, res, next) => {
  try {
    const model = await Model.findById(req.params.id);

    if (!model) {
      return next(
        new ErrorResponse(`Model not found with id of ${req.params.id}`, 404)
      );
    }

    // Make sure user is authorized to use the model
    if (!model.isPublic && model.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return next(
        new ErrorResponse(`User ${req.user.id} is not authorized to use this model`, 403)
      );
    }

    // Extract parameters from the request body
    const { prompt, image_url, max_tokens } = req.body;

    if (!prompt || !image_url) {
      return next(
        new ErrorResponse('Please provide prompt and image_url', 400)
      );
    }

    // Create the initial request
    const modelRequest = await ModelRequest.create({
      user: req.user.id,
      model: model._id,
      input: req.body
    });

    // Get the model provider
    const modelType = model.provider || 'OTHER';
    
    // Get headers for the model type
    const headers = getModelHeaders(modelType);
    
    // Add custom API key from model if available
    if (model.apiKey) {
      if (modelType === 'XAI') {
        headers['x-api-key'] = model.apiKey;
      } else {
        headers['Authorization'] = `Bearer ${model.apiKey}`;
      }
    }

    try {
      let requestBody = {
        ...model.parameters
      };
      
      // Format based on provider
      if (modelType === 'OPENAI') {
        // Format for OpenAI vision model
        requestBody = {
          model: model.parameters.model || 'gpt-4-vision-preview',
          messages: [
            {
              role: 'user',
              content: [
                { type: 'text', text: prompt },
                { type: 'image_url', image_url: { url: image_url } }
              ]
            }
          ],
          max_tokens: max_tokens || model.parameters.max_tokens || 1000
        };
      } else if (modelType === 'GEMINI') {
        // Format for Gemini Vision model
        // Check if we need to handle a URL or a base64 image
        const imageData = image_url.startsWith('data:') ? 
          image_url.split(',')[1] : 
          image_url.startsWith('http') ? 
            { uri: image_url } : 
            image_url;
        
        // Use the appropriate format based on whether we have a URL or data
        const imagePart = image_url.startsWith('http') ? 
          { 
            inline_data: { 
              mime_type: "image/jpeg",
              data: imageData 
            }
          } : 
          { 
            inlineData: { 
              mimeType: "image/jpeg",
              data: imageData
            }
          };
        
        requestBody = {
          generationConfig: {
            temperature: model.parameters.temperature || 0.7,
            maxOutputTokens: max_tokens || model.parameters.max_tokens || 1000
          },
          safetySettings: [
            {
              category: "HARM_CATEGORY_DANGEROUS_CONTENT",
              threshold: "BLOCK_NONE" 
            }
          ],
          contents: [
            {
              parts: [
                { text: prompt },
                imagePart
              ]
            }
          ]
        };
        
        // For Gemini API, we need to add the API key as a URL parameter instead of header
        const apiKey = headers['x-goog-api-key'];
        delete headers['x-goog-api-key']; // Remove from headers
        
        // Add API key to the endpoint URL
        const endpoint = model.endpoint.includes('?') 
          ? `${model.endpoint}&key=${apiKey}` 
          : `${model.endpoint}?key=${apiKey}`;
          
        // Make the actual API call to the model with URL parameter for API key
        const modelResponse = await axios.post(endpoint, requestBody, { headers });
        
        // Update the model request with the response
        modelRequest.output = modelResponse.data;
        modelRequest.status = 'success';
        modelRequest.completedAt = Date.now();
        await modelRequest.save();
        
        res.status(200).json({
          success: true,
          data: modelRequest
        });
        return; // Exit early since we've already handled the Gemini case
      }
      
      // For non-Gemini models, make the normal API call
      const modelResponse = await axios.post(model.endpoint, requestBody, { headers });

      // Update the model request with the response
      modelRequest.output = modelResponse.data;
      modelRequest.status = 'success';
      modelRequest.completedAt = Date.now();
      await modelRequest.save();

      res.status(200).json({
        success: true,
        data: modelRequest
      });
    } catch (error) {
      // Update the model request with the error
      modelRequest.status = 'error';
      modelRequest.error = error.message || 'Error calling external model API';
      modelRequest.completedAt = Date.now();
      await modelRequest.save();

      return next(
        new ErrorResponse(`Error calling model API: ${error.message}`, 500)
      );
    }
  } catch (err) {
    next(err);
  }
};

// @desc    Create structured vision request with schema
// @route   POST /api/models/:id/structured_vision
// @access  Private
export const createStructuredVisionRequest = async (req, res, next) => {
  try {
    const model = await Model.findById(req.params.id);

    if (!model) {
      return next(
        new ErrorResponse(`Model not found with id of ${req.params.id}`, 404)
      );
    }

    // Make sure user is authorized to use the model
    if (!model.isPublic && model.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return next(
        new ErrorResponse(`User ${req.user.id} is not authorized to use this model`, 403)
      );
    }

    // Extract parameters from the request body
    const { prompt, image_url, schema, max_tokens } = req.body;

    if (!prompt || !image_url || !schema) {
      return next(
        new ErrorResponse('Please provide prompt, image_url, and schema', 400)
      );
    }

    // Create the initial request
    const modelRequest = await ModelRequest.create({
      user: req.user.id,
      model: model._id,
      input: req.body
    });

    // Get the model provider
    const modelType = model.provider || 'OTHER';
    
    // Get headers for the model type
    const headers = getModelHeaders(modelType);
    
    // Add custom API key from model if available
    if (model.apiKey) {
      if (modelType === 'XAI') {
        headers['x-api-key'] = model.apiKey;
      } else {
        headers['Authorization'] = `Bearer ${model.apiKey}`;
      }
    }

    try {
      let requestBody = {
        ...model.parameters
      };
      
      // Format based on provider
      if (modelType === 'OPENAI') {
        // Format for OpenAI vision model with schema and structured output
        requestBody = {
          model: model.parameters.model || 'gpt-4-vision-preview',
          messages: [
            {
              role: 'user',
              content: [
                { type: 'text', text: prompt },
                { type: 'image_url', image_url: { url: image_url } }
              ]
            }
          ],
          max_tokens: max_tokens || model.parameters.max_tokens || 1000,
          response_format: { type: 'json_object', schema: schema }
        };
      } else if (modelType === 'GEMINI') {
        // Format for Gemini Vision model with schema
        // Check if we need to handle a URL or a base64 image
        const imageData = image_url.startsWith('data:') ? 
          image_url.split(',')[1] : 
          image_url.startsWith('http') ? 
            { uri: image_url } : 
            image_url;
        
        // Use the appropriate format based on whether we have a URL or data
        const imagePart = image_url.startsWith('http') ? 
          { 
            inline_data: { 
              mime_type: "image/jpeg",
              data: imageData 
            }
          } : 
          { 
            inlineData: { 
              mimeType: "image/jpeg",
              data: imageData
            }
          };
          
        requestBody = {
          generationConfig: {
            temperature: model.parameters.temperature || 0.7,
            maxOutputTokens: max_tokens || model.parameters.max_tokens || 1000
          },
          // Add the schema for structured output using safety settings to control output format
          safetySettings: [
            {
              category: "HARM_CATEGORY_DANGEROUS_CONTENT",
              threshold: "BLOCK_NONE" 
            }
          ],
          // Use a better prompt technique for structured output with Gemini
          contents: [
            {
              parts: [
                { 
                  text: `${prompt}\n\nAnalyze this image and return your response as a JSON object following this schema exactly:\n${JSON.stringify(schema, null, 2)}\n\nYour response must be valid JSON with no explanation or other text.` 
                },
                imagePart
              ]
            }
          ]
        };
        
        // For Gemini API, we need to add the API key as a URL parameter instead of header
        const apiKey = headers['x-goog-api-key'];
        delete headers['x-goog-api-key']; // Remove from headers
        
        // Add API key to the endpoint URL
        const endpoint = model.endpoint.includes('?') 
          ? `${model.endpoint}&key=${apiKey}` 
          : `${model.endpoint}?key=${apiKey}`;
          
        // Make the actual API call to the model with URL parameter for API key
        const modelResponse = await axios.post(endpoint, requestBody, { headers });
        
        // Update the model request with the response
        modelRequest.output = modelResponse.data;
        modelRequest.status = 'success';
        modelRequest.completedAt = Date.now();
        await modelRequest.save();
        
        res.status(200).json({
          success: true,
          data: modelRequest
        });
        return; // Exit early since we've already handled the Gemini case
      }
      
      // For non-Gemini models, make the normal API call
      const modelResponse = await axios.post(model.endpoint, requestBody, { headers });

      // Update the model request with the response
      modelRequest.output = modelResponse.data;
      modelRequest.status = 'success';
      modelRequest.completedAt = Date.now();
      await modelRequest.save();

      res.status(200).json({
        success: true,
        data: modelRequest
      });
    } catch (error) {
      // Update the model request with the error
      modelRequest.status = 'error';
      modelRequest.error = error.message || 'Error calling external model API';
      modelRequest.completedAt = Date.now();
      await modelRequest.save();

      return next(
        new ErrorResponse(`Error calling model API: ${error.message}`, 500)
      );
    }
  } catch (err) {
    next(err);
  }
};

// @desc    Create structured text request with schema
// @route   POST /api/models/:id/structured
// @access  Private
export const createStructuredRequest = async (req, res, next) => {
  try {
    const model = await Model.findById(req.params.id);

    if (!model) {
      return next(
        new ErrorResponse(`Model not found with id of ${req.params.id}`, 404)
      );
    }

    // Make sure user is authorized to use the model
    if (!model.isPublic && model.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return next(
        new ErrorResponse(`User ${req.user.id} is not authorized to use this model`, 403)
      );
    }

    // Extract parameters from the request body
    const { prompt, schema, max_tokens } = req.body;

    if (!prompt || !schema) {
      return next(
        new ErrorResponse('Please provide prompt and schema', 400)
      );
    }

    // Create the initial request
    const modelRequest = await ModelRequest.create({
      user: req.user.id,
      model: model._id,
      input: req.body
    });

    // Get the model provider
    const modelType = model.provider || 'OTHER';
    
    // Get headers for the model type
    const headers = getModelHeaders(modelType);
    
    // Add custom API key from model if available
    if (model.apiKey) {
      if (modelType === 'XAI') {
        headers['x-api-key'] = model.apiKey;
      } else {
        headers['Authorization'] = `Bearer ${model.apiKey}`;
      }
    }

    try {
      let requestBody = {
        ...model.parameters
      };
      
      // Format based on provider
      if (modelType === 'OPENAI') {
        // Format for OpenAI with structured output
        requestBody = {
          model: model.parameters.model || 'gpt-4o',
          messages: [
            {
              role: 'user',
              content: prompt
            }
          ],
          max_tokens: max_tokens || model.parameters.max_tokens || 1000,
          response_format: { type: 'json_object', schema: schema }
        };
      } else if (modelType === 'GEMINI') {
        // Format for Gemini with schema
        requestBody = {
          generationConfig: {
            temperature: model.parameters.temperature || 0.7,
            maxOutputTokens: max_tokens || model.parameters.max_tokens || 1000
          },
          // Add the schema for structured output using safety settings to control output format
          safetySettings: [
            {
              category: "HARM_CATEGORY_DANGEROUS_CONTENT",
              threshold: "BLOCK_NONE" 
            }
          ],
          // Use a better prompt technique for structured output with Gemini
          contents: [
            {
              parts: [
                { 
                  text: `${prompt}\n\nReturn your response as a JSON object following this schema exactly:\n${JSON.stringify(schema, null, 2)}\n\nYour response must be valid JSON with no explanation or other text.` 
                }
              ]
            }
          ]
        };
        
        // For Gemini API, we need to add the API key as a URL parameter instead of header
        const apiKey = headers['x-goog-api-key'];
        delete headers['x-goog-api-key']; // Remove from headers
        
        // Add API key to the endpoint URL
        const endpoint = model.endpoint.includes('?') 
          ? `${model.endpoint}&key=${apiKey}` 
          : `${model.endpoint}?key=${apiKey}`;
          
        // Make the actual API call to the model with URL parameter for API key
        const modelResponse = await axios.post(endpoint, requestBody, { headers });
        
        // Update the model request with the response
        modelRequest.output = modelResponse.data;
        modelRequest.status = 'success';
        modelRequest.completedAt = Date.now();
        await modelRequest.save();
        
        res.status(200).json({
          success: true,
          data: modelRequest
        });
        return; // Exit early since we've already handled the Gemini case
      }
      
      // For non-Gemini models, make the normal API call
      const modelResponse = await axios.post(model.endpoint, requestBody, { headers });

      // Update the model request with the response
      modelRequest.output = modelResponse.data;
      modelRequest.status = 'success';
      modelRequest.completedAt = Date.now();
      await modelRequest.save();

      res.status(200).json({
        success: true,
        data: modelRequest
      });
    } catch (error) {
      // Update the model request with the error
      modelRequest.status = 'error';
      modelRequest.error = error.message || 'Error calling external model API';
      modelRequest.completedAt = Date.now();
      await modelRequest.save();

      return next(
        new ErrorResponse(`Error calling model API: ${error.message}`, 500)
      );
    }
  } catch (err) {
    next(err);
  }
};

// @desc    Get all model requests for a user
// @route   GET /api/requests
// @access  Private
export const getModelRequests = async (req, res, next) => {
  try {
    const modelRequests = await ModelRequest.find({ user: req.user.id })
      .populate('model', 'name description')
      .sort('-createdAt');

    res.status(200).json({
      success: true,
      count: modelRequests.length,
      data: modelRequests
    });
  } catch (err) {
    next(err);
  }
};

// @desc    Get single model request
// @route   GET /api/requests/:id
// @access  Private
export const getModelRequest = async (req, res, next) => {
  try {
    const modelRequest = await ModelRequest.findById(req.params.id)
      .populate('model', 'name description endpoint');

    if (!modelRequest) {
      return next(
        new ErrorResponse(`Model request not found with id of ${req.params.id}`, 404)
      );
    }

    // Make sure user owns the request or is admin
    if (modelRequest.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return next(
        new ErrorResponse(`User ${req.user.id} is not authorized to access this request`, 403)
      );
    }

    res.status(200).json({
      success: true,
      data: modelRequest
    });
  } catch (err) {
    next(err);
  }
}; 