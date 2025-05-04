const path = require('path');

module.exports = {
  mode: 'production',
  entry: './background.js',
  output: {
    filename: 'background.bundle.js',
    path: path.resolve(__dirname, 'dist')
  },
  target: 'node',
  node: {
    __dirname: false,
    __filename: false
  },
  externals: {
    'chrome': 'chrome'
  }
}; 