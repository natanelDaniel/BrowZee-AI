import express from 'express';
import { 
  getModels, 
  getModel, 
  createModel, 
  updateModel, 
  deleteModel 
} from '../controllers/models.js';
import { 
  createModelRequest, 
  createVisionRequest, 
  createStructuredVisionRequest,
  createStructuredRequest
} from '../controllers/modelRequests.js';
import { protect, authorize } from '../middleware/auth.js';

const router = express.Router();

router.route('/')
  .get(protect, getModels)
  .post(protect, authorize('admin'), createModel);

router.route('/:id')
  .get(protect, getModel)
  .put(protect, authorize('admin'), updateModel)
  .delete(protect, authorize('admin'), deleteModel);

// Route for making model requests
router.post('/:id/request', protect, createModelRequest);

// Route for vision requests
router.post('/:id/vision', protect, createVisionRequest);

// Route for structured vision requests with schema
router.post('/:id/structured_vision', protect, createStructuredVisionRequest);

// Route for structured text requests with schema
router.post('/:id/structured', protect, createStructuredRequest);

export default router; 