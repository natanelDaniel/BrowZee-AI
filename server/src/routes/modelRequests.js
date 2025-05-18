import express from 'express';
import { getModelRequests, getModelRequest } from '../controllers/modelRequests.js';
import { protect } from '../middleware/auth.js';

const router = express.Router();

router.route('/')
  .get(protect, getModelRequests);

router.route('/:id')
  .get(protect, getModelRequest);

export default router; 