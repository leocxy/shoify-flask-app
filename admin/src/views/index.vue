<template>
    <polaris-layout>
        <theme-setting :init-themes="false" ref="themes"></theme-setting>
    </polaris-layout>
</template>

<script>
    import ThemeSetting from '@/components/ThemeSetting'
    import mixins from '@/utils/mixins'

    export default {
        name: "AdminPanel",
        mixins: [mixins],
        data: () => ({
            title: 'Configuration',
            desc: 'You can upload your postcode configuration here',
            card_title: 'Configuration',
        }),
        methods: {
            loadThemes: function () {
                this.$http.get(this.getApi('themes')).then(({data}) => {
                    this.$refs['themes'].setThemes(data.data)
                })
            },
        },
        mounted: function () {
            // Load themes
            this.loadThemes();
        },
        components: {ThemeSetting},
    }
</script>
