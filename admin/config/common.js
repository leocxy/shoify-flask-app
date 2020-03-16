'use strict';
const fs = require('fs');
const os = require('os');
const https = process.argv.indexOf('--ssl') !== -1 ? {
    key: fs.readFileSync(os.homedir() + '/.localhost_ssl/server.key'),
    cert: fs.readFileSync(os.homedir() + '/.localhost_ssl/server.crt')
} : false;

module.exports = {
    devServer: {
        disableHostCheck: true,
        allowedHosts: ['0.0.0.0', 'localhost', (process.env.APP_ADDRESS ? process.env.APP_ADDRESS.split('://')[1] : '127.0.0.1')],
        https: https,
    },
    lintOnSave: process.env.NODE_ENV !== 'production',
};
