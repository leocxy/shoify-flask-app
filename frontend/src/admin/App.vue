<template>
    <PPage :title="title" full-width>
        <router-view @title="updateTitle"></router-view>
        <PFooterHelp v-if="change"><PLink @click="reinstall()">Update</PLink> App permissions to get full functionality.</PFooterHelp>
    </PPage>
</template>

<script>
import {mutation} from "@/store";
import {errorCB, redirectRemote} from "@/store/actions";
import {getApi} from "@/store/getters";

export default {
    name: 'App',
    data: () => ({
        change: false,
        title: "Pocket Square App"
    }),
    methods: {
        initial: function () {
            // Init App Bridge
            const apiKey = window?.AppInfo.apiKey,
                host = window?.AppInfo.host;
            this.$set(this.$http.defaults.headers.common, 'Authorization', `Bearer ${window?.AppInfo.jwtToken}`)
            if (apiKey && apiKey !== '{{ apiKey }}' && host) mutation.initAppBridge({apiKey, host})
        },
        checkUpdate: function () {
            this.$http.get(getApi('check', 'status')).then(({data}) => this.change = data?.data.change).catch(errorCB)
        },
        reinstall: function () {
            this.$http.get(getApi('check', 'reinstall')).then(({data}) => {
                if (window.self === window.top) return window.location.href = data?.data
                redirectRemote(data?.data)
            }).catch(errorCB)
        },
        updateTitle: function (e) {
            this.title = e
        },
    },
    mounted() {
        this.initial()
        this.checkUpdate()
    }
}
</script>
