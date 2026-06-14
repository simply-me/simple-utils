const js = require("@eslint/js");
const globals = require("globals");

module.exports = [
  // Base ESLint recommended rules
  js.configs.recommended,

  // Global configuration
  {
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "commonjs",
      globals: {
        ...globals.node,
        ...globals.es2021,
      },
    },
  },

  // Custom rules
  {
    rules: {
      "no-console": ["warn", { allow: ["log", "warn", "error"] }],
      "no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
        },
      ],
    },
  },

  // Ignore patterns
  {
    ignores: ["node_modules/", "dist/", "build/", "coverage/"],
  },
];
