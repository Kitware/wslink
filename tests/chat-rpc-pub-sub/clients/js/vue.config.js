module.exports = {
  chainWebpack: (config) => {
    // Add project name as alias
    config.resolve.alias.set('wslink-pubsub', __dirname);
  },
  publicPath: './',
  outputDir: '../../www',
};
