import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// Load environment variables
dotenv.config();

// For ES module support with __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// MongoDB Atlas connection string
const atlasUri = 'mongodb+srv://netanel:LdwM41XfmTeN9wlm@cluster0.utf4e8z.mongodb.net/model-api?retryWrites=true&w=majority&appName=Cluster0';

const config = {
  port: process.env.PORT || 5000,
  mongoUri: process.env.MONGODB_URI || atlasUri,
  jwtSecret: process.env.JWT_SECRET || 'fallback_jwt_secret',
  jwtExpire: process.env.JWT_EXPIRE || '30d',
  nodeEnv: process.env.NODE_ENV || 'development'
};

export default config; 