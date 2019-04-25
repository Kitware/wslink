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
  mode: 'development',
  devtool: 'inline-source-map',
  devServer: {
    contentBase: path.resolve(__dirname, 'dist/test'),
  },
  module: {
    rules: [
      { test: entry, loader: 'expose-loader?app' },
      {
        test: /\.js$/,
        use: [
          {
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env'],
            },
          },
        ],
      },
    ]
  },
  plugins: [
    new HtmlWebpackPlugin(),
  ]
};
