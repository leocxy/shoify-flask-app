'use strict';
import isEmpty from 'lodash/isEmpty'
import state from './state'
import {Toast, ResourcePicker, Redirect} from "@shopify/app-bridge/actions";

export default {
    toastNotice(payload) {
        if (isEmpty(state.bridge)) return;
        let toastMsg = Toast.create(state.bridge, payload);
        toastMsg.dispatch(Toast.Action.SHOW);
    },
    redirectAdmin(path) {
        if (isEmpty(state.bridge)) return;
        let redirect = Redirect.create(state.bridge);
        redirect.dispatch(Redirect.Action.ADMIN_PATH, path)
    },
    productPicker(payload) {
        if (isEmpty(state.bridge)) return;
        let picker = ResourcePicker.create(state.bridge, {
                options: {showVariants: false, selectMultiple: payload['selectMultiple'] || false},
                resourceType: ResourcePicker.ResourceType.Product
            }),
            cancel_cb = (payload && payload['cancel_cb'] && typeof payload['cancel_cb'] === 'function') ? payload['cancel_cb'] : () => {
                picker.unsubscribe()
            },
            select_cb = (payload && payload['select_cb'] && typeof payload['select_cb'] === 'function') ? ({selection}) => {
                payload['select_cb'](selection), picker.unsubscribe()
            } : () => {
                picker.unsubscribe()
            };
        // selection callback
        picker.subscribe(ResourcePicker.Action.SELECT, select_cb);
        // cancel callback
        picker.subscribe(ResourcePicker.Action.CANCEL, cancel_cb);
        // dispatch picker
        picker.dispatch(ResourcePicker.Action.OPEN)
    },
    collectionPicker(payload) {
        if (isEmpty(state.bridge)) return;
        let picker = ResourcePicker.create(state.bridge, {
                options: {showVariants: false, selectMultiple: payload['selectMultiple'] || false},
                resourceType: ResourcePicker.ResourceType.Collection
            }),
            cancel_cb = (payload && payload['cancel_cb'] && typeof payload['cancel_cb'] === 'function') ? payload['cancel_cb'] : () => {
                picker.unsubscribe()
            },
            select_cb = (payload && payload['select_cb'] && typeof payload['select_cb'] === 'function') ? ({selection}) => {
                payload['select_cb'](selection), picker.unsubscribe()
            } : () => {
                picker.unsubscribe()
            };
        // selection callback
        picker.subscribe(ResourcePicker.Action.SELECT, select_cb);
        // cancel callback
        picker.subscribe(ResourcePicker.Action.CANCEL, cancel_cb);
        // dispatch picker
        picker.dispatch(ResourcePicker.Action.OPEN)
    },
}
