## Brief

All the frontend stuffs should keep in this folder. No matter the Admin UI or the Docs for the user.

The `node_modules` have been move to the root folder, because the Shopify extensions.

### Temporary but Important

1. The `docs` are using `vitepress` which using Vue3, but the Admin UI still using Vue2. Therefore, it will cause a
   conflict.
2. You can run `yarn install & yarn build` under `frontend` folder. Then you need to DELETE the `node_modules`,
   otherwise the Admin UI build will not success.
3. We should use React to build the Admin UI, so it will not more conflict in the future.

### Reference

- [VueJS Configuration Reference](https://cli.vuejs.org/config/).
- [VitePress](https://vitepress.dev/)