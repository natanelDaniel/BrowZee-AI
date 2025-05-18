import express from 'express';
import { 
  getModels, 
  getModel, 
  createModel, 
  updateModel, 
  deleteModel 
} from '../controllers/models.js';
import { createModelRequest } from '../controllers/modelRequests.js';
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

export default router; 