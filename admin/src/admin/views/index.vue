<template>
    <PPage title="Sample Page">
        <PEmptyState
                heading="Empty State Page"
                :primaryAction='{onAction: testAlert, content: "PrimaryButton"}'
                :secondaryAction='{onAction: testAlert, content: "SecondaryButton"}'
                image="https://cdn.shopify.com/s/files/1/0757/9955/files/empty-state.svg">
            <p>Track and receive your incoming inventory from suppliers.</p>
        </PEmptyState>
    </PPage>
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
