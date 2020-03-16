'use strict';
import Vue from 'vue'
import createApp from '@shopify/app-bridge'

export default {
    initAppBridge(state, {apiKey, shopOrigin}) {
        if (apiKey && shopOrigin) {
            try {
                let app = createApp({apiKey, shopOrigin})
                Vue.set(state, 'bridge', app);
            } catch (err) {
                console.error(err)
            }
        }
    },
    updateState(state, {key, val}) {
        if (key && val) {
            Vue.set(state, key, val)
        }
    }
}
