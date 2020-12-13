<template>
    <router-view></router-view>
</template>

<script>
    import {mutation, action} from "@/store";

    export default {
        name: 'App',
        data: () => ({}),
        methods: {},
        mounted() {
            // Init App Bridge
            let key = window.AppInfo['apiKey'] || null,
                shop = window.AppInfo['shop'] || null,
                jwtToken = window.AppInfo['jwtToken'] || null;
            if (key && shop) mutation.initAppBridge({apiKey: key, shopOrigin: shop, jwtToken: jwtToken});
            action.toastNotice({message: 'Hello World'});
        }
    }
</script>
