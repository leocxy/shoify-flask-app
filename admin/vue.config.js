'use strict'
let target_app = (process.env.NODE_APP || 'admin').trim();

module.exports = require(`./config/${target_app}.js`);
