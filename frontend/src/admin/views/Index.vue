<template>
    <PEmptyState
        heading="Empty State Page"
        image="https://cdn.shopify.com/s/files/1/0757/9955/files/empty-state.svg">
        <p>Track and receive your incoming inventory from suppliers.</p>
        <PStack slot="actions" spacing="tight" distribution="center" alignment="center">
            <PStackItem>
                <PButton primary @click="testAlert">Test Alert</PButton>
            </PStackItem>
            <PStackItem>
                <PButton @click="$router.push({name: 'gift-with-purchase'})">GWP</PButton>
            </PStackItem>
        </PStack>
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
