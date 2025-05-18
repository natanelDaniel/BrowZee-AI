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