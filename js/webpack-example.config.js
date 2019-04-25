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
  mode: 'development',
  devtool: 'inline-source-map',
  devServer: {
    contentBase: path.resolve(__dirname, 'dist/examples'),
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
