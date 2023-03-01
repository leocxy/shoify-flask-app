## Instruction

This is Shopify Function which generate by @shopify/cli + @shopify/app

### Packages

- @shopify/cli: ^3.20.1
- @shopify/app: ^3.20.1


### Environment

- OS: MacOX


### Pre requirement

1. Install Rust
2. Install Cargo-wasi
3. Install NodeJS

### Install

When I said `root folder`, mean the root folder for this project, not the current folder.
When I said `current folder`, mean the current folder.

1. Make sure you create the shopify.app.toml at the `root folder`
2. Install the node packages at the `root folder`
3. Using the @shopify/cli to generate the extension, such as `yarn shopify app generate`
4. Set up the `shopify.function.extension.toml`
5. On the `current folder`, run `cargo init`
6. Config `Cargo.toml` on the `current folder`
7. Create the `src folder` in the `current folder`
8. Create the `main.rs` and `api.rs` in the `src folder`
9. On the `root folder` run `yarn shopify app env pull` and generate the env file on `root folder`
10. For Shopify Function ID, you should be able to find it via partner portal.
11. Happy coding

### Reference

1. [Build a discount experience](https://shopify.dev/apps/discounts/create)
2. [Automatic discount tutorial](https://github.com/Shopify/function-examples/tree/main/sample-apps/discount-functions-sample-app)
3. [Discount tutorial](https://github.com/Shopify/function-examples/tree/main/sample-apps/discounts-tutorial)

### Example with crate shopify_function
// https://github.com/Shopify/shopify-function-rust/blob/main/example/src/main.rs
// https://github.com/Shopify/shopify-function-rust/blob/main/example/src/tests.rs

cargo test -- --show-output
