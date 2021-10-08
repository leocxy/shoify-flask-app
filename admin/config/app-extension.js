'use strict'
const path = require('path');
const ESLintPlugin = require('eslint-webpack-plugin');
const CopyPlugin = require("copy-webpack-plugin");
const extensionRooot = path.resolve(path.dirname(__dirname), 'app-extension')
const {CleanWebpackPlugin} = require('clean-webpack-plugin');

module.exports = {
    mode: process.env.NODE_ENV || 'production',
    entry: './src/app-extensions/src/index.ts',
    devtool: false,
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            }
        ],
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js'],
    },
    output: {
        path: path.resolve(extensionRooot, 'assets'),
        library: 'ThemeAppExtension',
        libraryExport: 'default',
        globalObject: 'this',
        libraryTarget: 'window',
        chunkFilename: '[name].js',
        filename: 'app.js',
    },
    plugins: [
        new ESLintPlugin({files: 'src/*.(ts|tsx)'}),
        new CleanWebpackPlugin({
            dry: false,
            verbose: false,
            cleanStaleWebpackAssets: false,
            protectWebpackAssets: false,
            cleanOnceBeforeBuildPatterns: [
                '*',
                '!.gitignore',
                `${path.resolve(extensionRooot, 'blocks')}/*.liquid`,
                `${path.resolve(extensionRooot, 'snippets')}/*.liquid`,
            ],
        }),
        new CopyPlugin({
            patterns: [
                {from: './src/app-extensions/assets', to: path.resolve(extensionRooot, 'assets'), noErrorOnMissing: true},
                {from: './src/app-extensions/blocks', to: path.resolve(extensionRooot, 'blocks'), noErrorOnMissing: true},
                {from: './src/app-extensions/snippets', to: path.resolve(extensionRooot, 'snippets'), noErrorOnMissing: true},
            ]
        })
    ],
}
