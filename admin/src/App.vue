<template>
    <polaris-page title="">
        <router-view></router-view>
    </polaris-page>
</template>

<script>
    export default {
        name: "Home",
        data: () => ({}),
        methods: {},
        mounted() {
            let key = this.$cookies.get('apiKey'),
                shop = this.$cookies.get('shop');
            if (key && shop) {
                this.$store.commit('initAppBridge', {apiKey: key, shopOrigin: shop})
            }
        },
        components: {}
    }
</script>
