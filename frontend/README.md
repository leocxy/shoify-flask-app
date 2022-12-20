## Brief

All the frontend stuffs should keep in this folder.
No matter the Admin UI or the Docs for the user.

The `node_modules` have been move to the root folder, because the Shopify extensions.

### Structure 

├── README.md
├── config # Webpack Configs
│   ├── admin.js
│   ├── common.js
│   └── front.js
├── dist
│   └── admin
├── package.json
├── src # All Source Files
│   ├── admin
│   └── front
├── vue.config.js
├── yarn-error.log
└── yarn.lock

### Reference

- [VueJS Configuration Reference](https://cli.vuejs.org/config/).
- [VuePress](https://vuepress.vuejs.org/)