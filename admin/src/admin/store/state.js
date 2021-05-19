'use strict';
import Vue from 'vue'

export default Vue.observable({
    bridge: {}, // App Bridge
    rest_api: [
        {name: 'test_jwt', url: '/admin/test_jwt'},
        {name: 'themes', url: '/admin/themes'},
    ]
})
