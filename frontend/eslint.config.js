import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
  },
  {
    // Compatibility screen retains the original effects; new modules use current rules.
    files: ['src/LegacyProvador.jsx'],
    rules: {'react-hooks/immutability':'off','react-hooks/set-state-in-effect':'off'},
  },
  {files:['src/features/commerce/Store.jsx'],rules:{'react-refresh/only-export-components':'off'}},
])
