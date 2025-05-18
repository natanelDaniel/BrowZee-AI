import mongoose from 'mongoose';

const ModelSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Please add a model name'],
    unique: true,
    trim: true
  },
  description: {
    type: String,
    required: [true, 'Please add a description']
  },
  endpoint: {
    type: String,
    required: [true, 'Please add an endpoint URL']
  },
  parameters: {
    type: Object,
    default: {}
  },
  provider: {
    type: String,
    enum: ['OPENAI', 'GROK', 'XAI', 'GEMINI', 'OTHER'],
    default: 'OTHER'
  },
  apiKey: {
    type: String,
    default: null
  },
  isPublic: {
    type: Boolean,
    default: false
  },
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

export default mongoose.model('Model', ModelSchema); 