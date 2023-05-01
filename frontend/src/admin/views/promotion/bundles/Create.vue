<template>
    <PLayoutAnnotatedSection title="Bundles">
        <PTextContainer slot="description">
            Shopify Bundles, add one variant to the cart, it will expend multiple items on the checkout page
        </PTextContainer>
    </PLayoutAnnotatedSection>
</template>

<script>
import common from "../../../utils/common"
import {getApi} from "../../../store/getters"

export default {
    name: "BundleDetail",
    mixins: [common],
    data: () => ({
        table_fields: [{
            name: '__slot:title',
            title: 'Title',
            titleClass: 'left aligned',
            dataClass: 'left aligned'
        }, {
            name: '__slot:status',
            title: 'Status',
            titleClass: 'center aligned',
            dataClass: 'center aligned'
        }, {
            name: 'updated_at',
            title: 'Updated At',
            titleClass: 'left aligned',
            dataClass: 'left aligned'
        }, {
            name: '__slot:actions',
            title: 'Action',
            titleClass: 'left aligned',
            dataClass: 'left aligned'
        }],
        params: {
            name: null,
        },
        isSaving: false,
    }),
    methods: {},
    mounted: function () {

    }
}
</script>
