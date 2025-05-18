import jwt from 'jsonwebtoken';
import { promisify } from 'util';
import User from '../models/User.js';
import config from '../config/config.js';

// Protect routes
export const protect = async (req, res, next) => {
  let token;
  
  if (
    req.headers.authorization &&
    req.headers.authorization.startsWith('Bearer')
  ) {
    // Set token from Bearer token in header
    token = req.headers.authorization.split(' ')[1];
  } else if (req.cookies?.token) {
    // Set token from cookie
    token = req.cookies.token;
  } else if (req.headers['x-api-key']) {
    // Set user from API key
    const apiKey = req.headers['x-api-key'];
    const user = await User.findOne({ apiKey });
    
    if (!user) {
      return res.status(401).json({
        success: false,
        error: 'Invalid API key'
      });
    }
    
    req.user = user;
    return next();
  }

  // Make sure token exists
  if (!token) {
    return res.status(401).json({
      success: false,
      error: 'Not authorized to access this route'
    });
  }

  try {
    // Verify token
    const decoded = await promisify(jwt.verify)(token, config.jwtSecret);

    req.user = await User.findById(decoded.id);
    next();
  } catch (err) {
    return res.status(401).json({
      success: false,
      error: 'Not authorized to access this route'
    });
  }
};

// Grant access to specific roles
export const authorize = (...roles) => {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        error: `User role ${req.user.role} is not authorized to access this route`
      });
    }
    next();
  };
}; 