<template>
    <polaris-page title="">
        <polaris-empty-state
                heading="Empty State Page"
                :action="{content: 'Add transfer', onAction: testAlert}"
                :secondary-action="{content: 'Learn more', url: 'https://help.shopify.com'}"
                image="https://cdn.shopify.com/s/files/1/0757/9955/files/empty-state.svg">
            <p>Track and receive your incoming inventory from suppliers.</p>
        </polaris-empty-state>
    </polaris-page>
</template>


<script>
    import {getter, action} from '@/store';

    export default {
        name: "SamplePage",
        methods: {
            testAlert: function () {
                this.$http.get(getter.getApi('test_jwt')).then((res) => {
                    action.toastNotice({message: res.data['message']})
                });
            }
        }
    }
</script>
