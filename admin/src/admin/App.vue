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
        const key = window.AppInfo['apiKey'] || null,
            shop = window.AppInfo['shop'] || null;
        this.$set(this.$http.defaults.headers.common, 'Authorization', `Bearer ${window.AppInfo['jwtToken'] || null}`)
        if (key && shop) mutation.initAppBridge({apiKey: key, shopOrigin: shop})
    }
}
</script>
