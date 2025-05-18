import express from 'express';
import cors from 'cors';
import connectDB from './config/db.js';
import config from './config/config.js';
import errorHandler from './middleware/error.js';

// Route files
import authRoutes from './routes/auth.js';
import modelRoutes from './routes/models.js';
import requestRoutes from './routes/modelRequests.js';

// Connect to database
connectDB();

const app = express();

// Body parser
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Configure CORS for external access
const corsOptions = {
  origin: '*', // Allow all origins
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'x-api-key'],
  exposedHeaders: ['Content-Range', 'X-Content-Range'],
  credentials: true,
  maxAge: 86400 // 24 hours
};

// Enable CORS
app.use(cors(corsOptions));

// Mount routers
app.use('/api/auth', authRoutes);
app.use('/api/models', modelRoutes);
app.use('/api/requests', requestRoutes);

// Simple health check route
app.get('/', (req, res) => {
  res.status(200).json({
    success: true,
    message: 'API is running',
    version: '1.0.0'
  });
});

// Error handler middleware
app.use(errorHandler);

const PORT = config.port;
const HOST = '0.0.0.0'; // Listen on all network interfaces

const server = app.listen(PORT, HOST, () => {
  console.log(`Server running in ${config.nodeEnv} mode on port ${PORT}`);
  console.log(`Server accessible at http://${HOST}:${PORT}`);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (err, promise) => {
  console.log(`Error: ${err.message}`);
  // Close server & exit process
  server.close(() => process.exit(1));
}); 