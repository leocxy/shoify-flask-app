## Brief

All the frontend stuffs should keep in this folder.

### Structure 

├── README.md
├── app-extension # Shopify Theme Extension dist folder - You need to create this by Shopify CLI
│   ├── assets
│   ├── blocks
│   └── snippets
├── babel.config.js
├── config # Webpack Configs
│   ├── admin.js
│   ├── app-extension.js
│   ├── common.js
│   └── front.js
├── dist
│   └── admin
├── package.json
├── public
│   ├── favicon.ico
│   └── index.html
├── src # All Source Files
│   ├── admin
│   ├── app-extensions
│   └── front
├── tsconfig.json
├── vue.config.js
├── yarn-error.log
└── yarn.lock

---

## Theme App Extension

- Date: 2021-10-08
- Author: Leo Chen <leo.cxy88@gmail.com>
- Shopify Cli: 2.6.3

You can't upload theme app extension to Shopify directly. You must use [Shopify CLI](https://shopify.dev/apps/tools/cli).

You can find the theme app extension structure from this [article](https://shopify.dev/apps/online-store/theme-app-extensions/extensions-framework)

You can find the [starter project from here](https://github.com/Shopify/theme-extension-getting-started)

### Development

- You need to install Shopify CLI and connect to Shopify
- You need to create an empty theme extension via below script

```shell
# 1. get to frontend root folder
cd PROJECT/admin
# 2. create the empty theme app extension
shopify extension create --type=THEME_APP_EXTENSION --name=app-extension
# 3. follow the instruction to finish remain process
```

### Deployment

You need to push your code to Shopify. Otherwise, you will not able to see it.
Once you pushed your code to Shopify, you are able to review your change in Development Store.
You need to publish your code at Shopify Partner Portal, otherwise, it will not show on the merchants store.

```shell
# 1. go to the app-extension folder
cd PROJECT/admin/app-extension
# 2. Push your code to Shopify
shopify extension push
# 3. Go the Partner Portal and Publish your code
```

---

## Reference

- [VueJS Configuration Reference](https://cli.vuejs.org/config/).
- [VuePress](https://vuepress.vuejs.org/)