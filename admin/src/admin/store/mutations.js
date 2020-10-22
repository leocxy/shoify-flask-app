'use strict';
import Vue from 'vue';
import state from './state'
import createApp from "@shopify/app-bridge";

export default {
    initAppBridge({apiKey, shopOrigin}) {
        if (apiKey && shopOrigin) {
            let app = createApp({apiKey, shopOrigin});
            Vue.set(state, 'bridge', app);
        }
    },
    updateState({key, val}) {
        if (key && val) {
            Vue.set(state, key, val)
        }
    }
}
