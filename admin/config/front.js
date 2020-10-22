'use strict';
const path = require('path');
const merge = require('webpack-merge');
const commonConfig = require('./common.js');

module.exports = merge(commonConfig, {
    pages: {
        index: {
            entry: 'src/front/main.js',
            template: 'public/index.html',
            filename: 'index.html',
            title: 'Pocket Square Docs',
            chunks: ['chunk-vendors', 'chunk-common', 'index']
        }
    },
    outputDir: 'dist/front',
    publicPath: process.env.NODE_ENV === 'production' ? '/front' : '/',
    devServer: {
        proxy: {'/api': {target: 'http://127.0.0.1:5000'}}
    },
    configureWebpack: config => {
        config.resolve.alias['@'] = path.resolve('src/front/')
    }
});
