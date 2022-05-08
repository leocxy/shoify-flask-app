<template>
    <PPage title="Pocket Square App">
        <router-view></router-view>
        <PFooterHelp v-if="change"><PLink @click="reinstall()">Update</PLink> App permissions to get full functionality.</PFooterHelp>
    </PPage>
</template>

<script>
import {mutation} from "@/store";
import {errorCB} from "@/store/actions";
import {getApi} from "@/store/getters";

export default {
    name: 'App',
    data: () => ({
        change: false
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
            this.$http.get(getApi('check', 'reinstall')).then(({data}) => window.location.href = data?.data).catch(errorCB)
        }
    },
    mounted() {
        this.initial()
        this.checkUpdate()
    }
}
</script>
