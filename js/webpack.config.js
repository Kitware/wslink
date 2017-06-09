var path = require('path');

module.exports = {
  context: path.resolve(__dirname),
  entry: ['./src/index.js'],
  output: {
    filename: 'wslink.js',
    path: path.resolve(__dirname, 'dist'),
    library: "wslink",
    libraryTarget: "umd"
  },
  module: {
    rules: [
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
};
