'use strict';
import Axios from "axios"
import PolarisVue from '@eastsideco/polaris-vue'
import '@eastsideco/polaris-vue/lib/polaris-vue.css'
import {Plugin} from 'vue-fragment'


export default {
    install: (Vue) => {
        Axios.interceptors.response.use(function (response) {
            if (response.status === 200 && response.data instanceof Blob) return response;
            if (response.data.status !== 0) return Promise.reject(response);
            return response
        }, function (error) {
            return Promise.reject(error)
        });
        Vue.prototype.$http = Axios;
        Vue.use(PolarisVue);
        Vue.use(Plugin);
    }
}