'use strict';
import isUndefined from 'lodash/isUndefined'
import isString from 'lodash/isString'

export default {
    getApi: (state) => (name, params) => {
        let rs = state.rest_api ? state.rest_api.find(v => v.name == name) : {url: '/'};
        params = isUndefined(params) ? '' : '/' + (isString(params) ? params : params.join('/'));
        return rs.url + params
    },
    getRule: function(field_name) {
        return this.rules ? (this.rules[field_name] || '') : '';
    }
}
