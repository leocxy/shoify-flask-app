<template>
    <PPage title="Pocket Square App">
        <router-view></router-view>
    </PPage>
</template>

<script>
import {mutation} from "@/store";

export default {
    name: 'App',
    data: () => ({}),
    mounted() {
        // Init App Bridge
        const apiKey = window?.AppInfo.apiKey,
            host = window?.AppInfo.host;
        this.$set(this.$http.defaults.headers.common, 'Authorization', `Bearer ${window?.AppInfo.jwtToken}`)
        if (apiKey && host) mutation.initAppBridge({apiKey, host})
    }
}
</script>
