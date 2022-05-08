'use strict';
import Vue from 'vue'

export default Vue.observable({
    bridge: {}, // App Bridge
    rest_api: [
        {name: 'check', url: '/admin/check'},
        {name: 'test_jwt', url: '/admin/test_jwt'},
    ]
})
