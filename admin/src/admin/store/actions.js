'use strict';
import isEmpty from 'lodash/isEmpty'
import state from './state'
import {Toast, ResourcePicker, Redirect, Loading} from "@shopify/app-bridge/actions";

const toastNotice = function (payload) {
    if (isEmpty(state.bridge)) return;
    const toastMsg = Toast.create(state.bridge, payload);
    toastMsg.dispatch(Toast.Action.SHOW);
}

const redirectAdmin = function (path) {
    if (isEmpty(state.bridge)) return;
    const redirect = Redirect.create(state.bridge);
    redirect.dispatch(Redirect.Action.ADMIN_PATH, path)
}

const productPicker = function (payload) {
    if (isEmpty(state.bridge)) return;
    const picker = ResourcePicker.create(state.bridge, {
            options: {
                showVariants: payload['showVariants'] || false,
                selectMultiple: payload['selectMultiple'] || false,
                initialSelectionIds: payload['initialSelectionIds'] || []
            },
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
}

const variantPicker = function (payload) {
    if (isEmpty(state.bridge)) return;
    const picker = ResourcePicker.create(state.bridge, {
            options: {
                selectMultiple: payload['selectMultiple'] || false,
                initialSelectionIds: payload['initialSelectionIds'] || []
            },
            resourceType: ResourcePicker.ResourceType.ProductVariant
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
}

const collectionPicker = function (payload) {
    if (isEmpty(state.bridge)) return;
    const picker = ResourcePicker.create(state.bridge, {
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
}

const triggerLoading = function (v) {
    if (isEmpty(state.bridge)) return;
    const loading = Loading.create(state.bridge);
    v ? loading.dispatch(Loading.Action.START) : loading.dispatch(Loading.Action.STOP)
}

const errorCB = function (err) {
    console.error(err)
    if (err.data?.message) return toastNotice({message: err.data.message, isError: true})
    return toastNotice({message: 'Unknown error!', isError: true})
}

export {toastNotice, redirectAdmin, productPicker, variantPicker, collectionPicker, triggerLoading, errorCB}

export default {
    toastNotice: toastNotice,
    redirectAdmin: redirectAdmin,
    productPicker: productPicker,
    variantPicker: variantPicker,
    collectionPicker: collectionPicker,
    triggerLoading: triggerLoading,
    errorCB: errorCB,
}
