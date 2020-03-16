<template>
    <fragment>
        <polaris-layout-annotated-section :title="title" :description="desc">
            <polaris-card :title="card_title">
                <polaris-card-section>
                    <polaris-resource-list :items="installedThemes">
                        <template slot="item" slot-scope="val">
                            <div class="resource_list_item">
                                <div class="item_title">
                                    <b>{{ val.item.theme_name }}</b> - {{ val.item.theme_id }}
                                </div>
                                <polaris-button-group class="btn_group">
                                    <polaris-button-group-item>
                                        <polaris-button destuctive size="slim" @click="deleteTheme(val.item)"
                                                        :loading="deleting">
                                            Uninstall
                                        </polaris-button>
                                    </polaris-button-group-item>
                                </polaris-button-group>
                            </div>
                        </template>
                    </polaris-resource-list>
                </polaris-card-section>
                <div class="Polaris-Card__Footer">
                    <polaris-button-group>
                        <polaris-button slot="2" primary :loading="loading" @click="toggleModel">
                            Install to a new theme
                        </polaris-button>
                    </polaris-button-group>
                </div>
            </polaris-card>
        </polaris-layout-annotated-section>
        <modal v-if="showModal">
            <div slot="header">
                <h3>Select Theme</h3>
            </div>
            <div slot="body">
                <polaris-select
                        v-model="form.theme_id"
                        :options="themeList"
                        placeholder="Select a theme to install"
                        :error="themeIdError">
                    <div slot="helpText">
                        Required assets will be added to your theme. It is strongly advised to
                        <a @click="redirectToThemePanel">duplicate a theme</a> if it is active on a live store.
                    </div>
                </polaris-select>
            </div>
            <div slot="footer">
                <polaris-button-group>
                    <polaris-button slot="1" @click="showModal = false">Close</polaris-button>
                    <polaris-button slot="2" primary @click="installTheme" :loading="loading">Install</polaris-button>
                </polaris-button-group>
            </div>
        </modal>
    </fragment>
</template>

<script>
    import mixins from '@/utils/mixins'
    import Modal from './Modal.vue'

    export default {
        name: "ThemeSetting",
        mixins: [mixins],
        data: () => ({
            title: "Active Installation",
            desc: "Add the required files to your theme for Laybuy breakdown.",
            card_title: "Installed Themes",
            installedThemes: [],
            themeList: [],
            loading: true,
            deleting: false,
            showModal: false,
            form: {theme_id: null},
            themeIdError: null,
        }),
        props: {
            initThemes: {type: Boolean, default: true}
        },
        methods: {
            toggleModel() {
                this.$http.get(this.getApi('available_themes')).then(({data}) => {
                    this.$set(this, 'themeList', data.data);
                    this.showModal = !this.showModal
                })
            },
            redirectToThemePanel() {
                this.$store.dispatch('redirectAdmin', '/themes')
            },
            installTheme() {
                if (this.form.theme_id == null) return;
                this.loading = true;
                this.$http.post(this.getApi('themes'), this.form).then(() => {
                    this.showModal = false;
                    this.$store.dispatch('toastNotice', {message: 'Installed Successful'});
                    this.loadThemeSetting();
                })
            },
            deleteTheme(item) {
                this.deleting = true;
                this.$http.delete(this.getApi('themes') + '/' + item.theme_id).then(() => {
                    this.deleting = false;
                    this.$store.dispatch('toastNotice', {message: 'Revert Successful'});
                    this.loadThemeSetting();
                })
            },
            loadThemeSetting() {
                this.loading = true;
                this.$http.get(this.getApi('themes')).then(({data}) => {
                    this.installedThemes = data.data;
                    this.loading = false;
                })
            },
            setThemes: function (themes) {
                this.$set(this, 'installedThemes', themes)
            },
        },
        mounted() {
            this.initThemes ? this.loadThemeSetting() : this.loading = false;
        },
        components: {Modal}
    }
</script>

<style lang="scss" scoped>
    .resource_list_item {
        background-color: #eff0f8;
        padding: 15px;
        position: relative;

        .item_title {
            padding-left: 10px;
        }

        .btn_group {
            position: absolute;
            top: 10.5px;
            right: 15px;
        }
    }
</style>