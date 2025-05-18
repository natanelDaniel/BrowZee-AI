import mongoose from 'mongoose';

const ModelRequestSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  model: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Model',
    required: true
  },
  input: {
    type: Object,
    required: true
  },
  output: {
    type: Object
  },
  status: {
    type: String,
    enum: ['success', 'error', 'pending'],
    default: 'pending'
  },
  error: {
    type: String
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  completedAt: {
    type: Date
  }
});

export default mongoose.model('ModelRequest', ModelRequestSchema); 