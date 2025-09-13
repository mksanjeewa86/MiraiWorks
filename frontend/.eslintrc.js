const { createRequire } = require('module');
const require = createRequire(import.meta.url);

module.exports = {
  extends: ['next/core-web-vitals'],
  rules: {
    // Relax some rules for faster CI and better developer experience
    '@typescript-eslint/no-unused-vars': ['warn', { 
      'argsIgnorePattern': '^_',
      'varsIgnorePattern': '^_'
    }],
    'react-hooks/exhaustive-deps': 'warn', // Change from error to warning
    // Allow console logs in development
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn'
  }
};