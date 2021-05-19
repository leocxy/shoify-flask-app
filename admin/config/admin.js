'use strict';
const path = require('path');
const { merge } = require('webpack-merge');
const commonConfig = require('./common.js');

module.exports = merge(commonConfig, {
    pages: {
        index: {
            entry: 'src/admin/main.js',
            template: 'public/index.html',
            filename: 'index.html',
            title: 'Pocket Square',
            chunks: ['chunk-vendors', 'chunk-common', 'index']
        }
    },
    outputDir: 'dist/admin',
    publicPath: process.env.NODE_ENV === 'production' ? '/admin' : '/',
    devServer: {
        // Redirect all api path to backend
        proxy: {'/admin': {target: 'http://127.0.0.1:5000'}}
    },
    configureWebpack: config => {
        config.resolve.alias['@'] = path.resolve('src/admin/')
        config.devtool = 'source-map'
    },
});
