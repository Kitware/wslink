var path = require('path');
var HtmlWebpackPlugin = require('html-webpack-plugin');
const entry = path.join(__dirname, './test/main.js');

module.exports = {
  context: path.resolve(__dirname),
  entry,
  output: {
    filename: 'test.js',
    path: path.resolve(__dirname, 'dist/test'),
  },
  devServer: {
    contentBase: path.resolve(__dirname, 'dist/test'),
  },
  module: {
    rules: [
      { test: entry, loader: 'expose-loader?app' },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        options: {
          presets: [
            [ 'es2015', { modules: false } ]
          ]
        }
      }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin(),
  ]
};
