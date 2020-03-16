'use strict';

const path = require('path');
const merge = require('webpack-merge');
const commonConfig = require('./common.js');

module.exports = merge(commonConfig, {
    pages: {
        index: {
            entry: 'src/main.js',
            template: 'public/index.html',
            filename: 'index.html',
            title: 'Community Organics App',
            chunks: ['chunk-vendors', 'chunk-common', 'index']
        }
    },
    publicPath: process.env.NODE_ENV === 'production' ? '/admin' : '/',
    outputDir: 'dist',
    devServer: {
        proxy: 'http://127.0.0.1:5000'
    },
    configureWebpack: config => {
        config.resolve.alias['@'] = path.resolve('src/');
        config.devtool = 'source-map'
    },
});
