'use strict';
import Vue from 'vue'
import state from './state'
import createApp from "@shopify/app-bridge"

export default {
    initAppBridge({apiKey, host}) {
        if (apiKey && host) {
            let app = createApp({apiKey, host});
            Vue.set(state, 'bridge', app);
        }
    },
    updateState({key, val}) {
        if (key && val) {
            Vue.set(state, key, val)
        }
    }
}
