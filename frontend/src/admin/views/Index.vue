<template>
    <PEmptyState
        heading="Empty State Page"
        :primaryAction='{onAction: testAlert, content: "PrimaryButton"}'
        :secondaryAction='{onAction: testAlert, content: "SecondaryButton"}'
        image="https://cdn.shopify.com/s/files/1/0757/9955/files/empty-state.svg">
        <p>Track and receive your incoming inventory from suppliers.</p>
    </PEmptyState>
</template>


<script>
import {getApi} from "../store/getters"

export default {
    name: "SamplePage",
    methods: {
        testAlert: function () {
            console.log(this.$router, 'test');
            this.$http.get(getApi('test_jwt')).then((res) => {
                this.$pToast.open({message: res.data['message']})
            });
        }
    }
}
</script>
