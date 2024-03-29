'use strict';
const path = require('path');
const { merge } = require('webpack-merge');
const commonConfig = require('./common.js');

module.exports = merge(commonConfig, {
    pages: {
        index: {
            entry: 'src/admin/main.js',
            template: 'src/admin/public/index.html',
            filename: 'index.html',
            title: 'Pocket Square',
            chunks: ['chunk-vendors', 'chunk-common', 'index']
        }
    },
    outputDir: '../dist/admin',
    publicPath: process.env.npm_lifecycle_event.includes('build') ? '/admin' : '/',
    devServer: {
        // Redirect all api path to backend
        proxy: {'/admin': {target: 'http://127.0.0.1:5000'}}
    },
    chainWebpack: config => {
        config.resolve.alias.set('@', path.resolve('src/admin/'))
        config.merge({ devtool: 'source-map' })
    },
});
