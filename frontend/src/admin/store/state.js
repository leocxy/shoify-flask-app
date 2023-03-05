'use strict';
import Vue from 'vue'

export default Vue.observable({
    bridge: {}, // App Bridge
    rest_api: [
        {name: 'check', url: '/admin/check'},
        {name: 'test_jwt', url: '/admin/test_jwt'},
        {name: 'generate_code', url: '/admin/common/generate_code'},
        {name: 'discount_code', url: '/admin/discount_code'},
        {name: 'gwp', url: '/admin/gift_with_purchase'},
    ]
})
