'use strict';
import Vue from 'vue'

export default Vue.observable({
    bridge: {}, // App Bridge
    rest_api: [
        {name: 'themes', url: '/api/themes'},
    ]
})
