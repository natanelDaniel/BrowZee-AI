import Model from '../models/Model.js';
import ErrorResponse from '../utils/errorHandler.js';

// @desc    Get all models
// @route   GET /api/models
// @access  Private
export const getModels = async (req, res, next) => {
  try {
    // Get all public models and models that belong to the user
    const models = await Model.find({
      $or: [
        { isPublic: true },
        { user: req.user.id }
      ]
    });

    res.status(200).json({
      success: true,
      count: models.length,
      data: models
    });
  } catch (err) {
    next(err);
  }
};

// @desc    Get single model
// @route   GET /api/models/:id
// @access  Private
export const getModel = async (req, res, next) => {
  try {
    const model = await Model.findById(req.params.id);

    if (!model) {
      return next(
        new ErrorResponse(`Model not found with id of ${req.params.id}`, 404)
      );
    }

    // Make sure user is model owner or model is public
    if (!model.isPublic && model.user.toString() !== req.user.id && req.user.role !== 'admin') {
      return next(
        new ErrorResponse(`User ${req.user.id} is not authorized to access this model`, 403)
      );
    }

    res.status(200).json({
      success: true,
      data: model
    });
  } catch (err) {
    next(err);
  }
};

// @desc    Create new model
// @route   POST /api/models
// @access  Private/Admin
export const createModel = async (req, res, next) => {
  try {
    // Add user to req.body
    req.body.user = req.user.id;

    const model = await Model.create(req.body);

    res.status(201).json({
      success: true,
      data: model
    });
  } catch (err) {
    next(err);
  }
};

// @desc    Update model
// @route   PUT /api/models/:id
// @access  Private/Admin
export const updateModel = async (req, res, next) => {
  try {
    let model = await Model.findById(req.params.id);

    if (!model) {
      return next(
        new ErrorResponse(`Model not found with id of ${req.params.id}`, 404)
      );
    }

    // Make sure user is admin
    if (req.user.role !== 'admin') {
      return next(
        new ErrorResponse(`User ${req.user.id} is not authorized to update this model`, 403)
      );
    }

    model = await Model.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true
    });

    res.status(200).json({
      success: true,
      data: model
    });
  } catch (err) {
    next(err);
  }
};

// @desc    Delete model
// @route   DELETE /api/models/:id
// @access  Private/Admin
export const deleteModel = async (req, res, next) => {
  try {
    const model = await Model.findById(req.params.id);

    if (!model) {
      return next(
        new ErrorResponse(`Model not found with id of ${req.params.id}`, 404)
      );
    }

    // Make sure user is admin
    if (req.user.role !== 'admin') {
      return next(
        new ErrorResponse(`User ${req.user.id} is not authorized to delete this model`, 403)
      );
    }

    await model.deleteOne();

    res.status(200).json({
      success: true,
      data: {}
    });
  } catch (err) {
    next(err);
  }
}; 