'use strict';
import Vue from 'vue'
import state from './state'
import createApp from "@shopify/app-bridge"

export default {
    initAppBridge({apiKey, shopOrigin, jwtToken}) {
        if (apiKey && shopOrigin) {
            let app = createApp({apiKey, shopOrigin});
            Vue.set(state, 'bridge', app);
            if (jwtToken) Vue.prototype.$http.defaults.headers.common['Authorization'] = `Bearer ${jwtToken}`
        }
    },
    updateState({key, val}) {
        if (key && val) {
            Vue.set(state, key, val)
        }
    }
}
