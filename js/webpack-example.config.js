var path = require('path');
var HtmlWebpackPlugin = require('html-webpack-plugin');
const entry = path.join(__dirname, './examples/main.js');

module.exports = {
  context: path.resolve(__dirname),
  entry,
  output: {
    filename: 'example.js',
    path: path.resolve(__dirname, 'dist/examples'),
  },
  devServer: {
    contentBase: path.resolve(__dirname, 'dist/examples'),
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
