module.exports =  {
    parser:  '@typescript-eslint/parser',  // Specifies the ESLint parser
    extends:  [
        'plugin:@typescript-eslint/recommended',  // Uses the recommended rules from @typescript-eslint/eslint-plugin
    ],
    parserOptions:  {
        ecmaVersion:  2020,  // Allows for the parsing of modern ECMAScript features
        sourceType:  'module',  // Allows for the use of imports
    },
    rules: {
        'no-console': 'warn',
        'no-debugger': 'warn',
        '@typescript-eslint/no-explicit-any': 'off',
        indent: [2, 4]
    },
    settings:  {},
};
