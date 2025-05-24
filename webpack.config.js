const path = require('path');

module.exports = {
  mode: 'development',
  entry: {
    index: './catalog/static/catalog/js/react/index.js'
  },
  output: {
    path: path.resolve(__dirname, 'catalog/static/catalog/js/react/dist'),
    filename: 'bundle.js',
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react']
          }
        }
      },
      {
        test: /\.css$/,
        use: [
          'style-loader', 
          'css-loader'
        ],
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  }
};