// eslint.config.mjs
import path from 'node:path';
import { defineConfig, globalIgnores } from 'eslint/config';
import typescriptEslint from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import svelteParser from 'svelte-eslint-parser';
import sveltePlugin from 'eslint-plugin-svelte';
import globals from 'globals';
import js from '@eslint/js';
import { FlatCompat } from '@eslint/eslintrc';
import { includeIgnoreFile } from '@eslint/compat';

const gitignorePath = path.resolve('.gitignore');

const compat = new FlatCompat({
  baseDirectory: new URL('.', import.meta.url).pathname,
});

export default defineConfig([
  globalIgnores([
    '**/node_modules/',
    '**/dist/',
    '**/build/',
    '**/server/',
    '**/*.py',
    '**/*.pyc',
    '**/__pycache__/',
    '**/*.min.js',
    '**/*.min.css',
    '**/*.config.js',
    '**/*.config.ts',
    '**/*.pdf',
    '**/public/',
  ]),
  includeIgnoreFile(gitignorePath),

  {
    files: ['**/*.js', '**/*.ts'],
    plugins: {
      '@typescript-eslint': typescriptEslint,
    },
    languageOptions: {
      parser: tsParser,
      ecmaVersion: 2020,
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node,
      },
      parserOptions: {
        extraFileExtensions: ['.svelte'],
      },
    },
    rules: {
      ...js.configs.recommended.rules,
      ...typescriptEslint.configs.recommended.rules,
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_' },
      ],
      '@typescript-eslint/no-explicit-any': 'warn',
    },
  },

  {
    files: ['**/*.svelte'],
    plugins: {
      svelte: sveltePlugin,
      '@typescript-eslint': typescriptEslint,
    },
    languageOptions: {
      parser: svelteParser,
      ecmaVersion: 2020,
      sourceType: 'module',
      parserOptions: {
        parser: '@typescript-eslint/parser',
      },
    },
    rules: {
      'svelte/no-unused-svelte-ignore': 'error',
      'svelte/no-target-blank': 'error',
    },
  },
]);
