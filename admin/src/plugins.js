'use strict';
import Axios from 'axios'
import PolarisVue from '@eastsideco/polaris-vue'
import '@eastsideco/polaris-vue/lib/polaris-vue.css'
import { Plugin } from 'vue-fragment'
import VueCookie from 'vue-cookies'

export default {
    install: (Vue) => {
        Axios.interceptors.response.use(function(response) {
            if (response.data.status !== 0) {
                console.error('There is something wrong!', response)
            }
            return response
        }, function(error) {
            return Promise.reject(error)
        });
        Vue.prototype.$http = Axios;
        Vue.use(PolarisVue);
        Vue.use(VueCookie);
        Vue.use(Plugin);
    }
}
