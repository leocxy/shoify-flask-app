<template>
    <router-view></router-view>
</template>

<script>
    import {mutation} from "@/store";

    export default {
        name: 'App',
        data: () => ({}),
        methods: {},
        mounted() {
            let key = this.$cookies.get('apiKey'), shop = this.$cookies.get('shop');
            // Init App Bridge
            if (key && shop) mutation.initAppBridge({apiKey: key, shopOrigin: shop})
        }
    }
</script>
