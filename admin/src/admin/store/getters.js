'use strict';
import isString from 'lodash/isString'
import isUndefined from 'lodash/isUndefined'
import state from './state'

let getApi = function (name, params) {
    let rs = state.rest_api ? state.rest_api.find(v => v.name == name) : {url: '/'};
    params = isUndefined(params) ? '' : '/' + (isString(params) ? params : params.join('/'));
    return rs.url + params
}

let getRule = function (name) {
    return this.rules ? (this.rules[name] || '') : ''
}

export {getApi, getRule}

export default {getApi: getApi, getRule: getRule}
