module.exports = {
  root: true,
  env: {
    node: true,
  },
  extends: [
    'plugin:vue/essential',
  ],
  parserOptions: {
    parser: "@babel/eslint-parser",
  },
  rules: {
    'import/extensions': 0,
    'linebreak-style': 0,
    'no-console': 0,
    'no-plusplus': 0,
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
  },
};
