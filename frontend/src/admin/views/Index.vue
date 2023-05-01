<template>
    <PEmptyState
        heading="Scaffold Example"
        image="https://cdn.shopify.com/s/files/1/0757/9955/files/empty-state.svg">
        <PTextContainer>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor.
            Aenean massa. Cum
            sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis,
            ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo,
            fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae,
            justo. Nullam dictum felis eu pede mollis pretium.
        </PTextContainer>
        <PStack slot="actions" spacing="tight" distribution="center" alignment="center">
            <PStackItem>
                <PButton primary @click="testAlert">Test Alert</PButton>
            </PStackItem>
            <PStackItem>
                <PButton @click="$router.push({name: 'gwp'})">Gift with purchase</PButton>
            </PStackItem>
            <PStackItem>
                <PButton @click="$router.push({name: 'bundleSale'})">Bundles</PButton>
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
