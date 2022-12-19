<template>
    <PLayout>
        <PLayoutSection>
            <PCard sectioned title="Amount off order">
                <div slot="children">
                    Order discount
                </div>
                <PFormLayout>
                    <PStack vertical alignment="leading" spacing="extraTight">
                        <PStackItem>
                            <PRadioButton id="discount_code" label="Discount code" name="method"
                                          :checked="form.method === 'code'" value="code"
                                          @change="changeMethod"/>
                        </PStackItem>
                        <PStackItem>
                            <PRadioButton id="auto_discount" label="Automatic discount" name="method"
                                          :checked="form.method !== 'code'" value="auto"
                                          @change="changeMethod"/>
                        </PStackItem>
                    </PStack>
                    <PTextField v-if="form.method === 'code'" label="Discount code" v-model="form.code"
                                help-text="Customers must enter this code at checkout" connected>
                        <PButton slot="connectedRight">Generate</PButton>
                    </PTextField>
                    <PTextField v-else label="Title"
                                help-text="Customers will see this in their cart and at checkout"
                                v-model="form.title"/>
                </PFormLayout>
            </PCard>
            <PCard sectioned title="Value">
                <PFormLayout>
                    <PFormLayoutGroup>
                        <PButtonGroup segmented>
                            <PButton :pressed="form.type === 'percentage'" @click="changeValueType('percentage')">
                                Percentage
                            </PButton>
                            <PButton :pressed="form.type === 'fixed'" @click="changeValueType('fixed')">Fixed amount
                            </PButton>
                        </PButtonGroup>
                        <PTextField type="number" :value="form.value" @input="changeValue">
                            <div slot="suffix" v-show="form.type === 'percentage'">%</div>
                            <div slot="prefix" v-show="form.type === 'fixed'">$</div>
                        </PTextField>
                    </PFormLayoutGroup>
                </PFormLayout>
            </PCard>
            <PCard sectioned title="Minimum purchase requirements">
                TODO - Default None
                Cost, Currency, Amount, Attributes, etc.
                https://shopify.dev/api/functions/reference/order-discounts/graphql/common-objects/cart
            </PCard>
            <PCard sectioned title="Customer eligibility">
                TODO - amountSpend, hasAnyTag, numberOfOrders, metafield, etc.
                https://shopify.dev/api/functions/reference/order-discounts/graphql/common-objects/customer
            </PCard>
            <PCard sectioned title="Combinations">
                TODO - Default None
                Product Discount, Order Discount and Shipping Discount.
                I assume it could only allow applying one of each above.
            </PCard>
            <PCard sectioned title="Active dates">
                TODO - Start and End Date
            </PCard>
            <PCard style="background: transparent; box-shadow: none;">
                <PButtonGroup>
                    <PButton>Discard</PButton>
                    <PButton primary>Save</PButton>
                </PButtonGroup>
            </PCard>
        </PLayoutSection>
        <PLayoutSection secondary>
            <PCard sectioned title="Summary">
                <div>Summary TODO</div>
            </PCard>
        </PLayoutSection>
    </PLayout>
</template>

<script>
import throttle from "lodash/throttle";

export default {
    name: "Discount",
    data: () => ({
        summary: [],
        form: {
            method: 'code',
            code: null,
            title: null,
            type: 'percentage',
            value: 0,
        }
    }),
    methods: {
        changeMethod: function (e) {
            this.form.method = e.value
            console.log(this.form.method)
            this.form.method === 'code' ? this.form.title = null : this.form.code = null
        },
        changeValueType: function (v) {
            this.form.type = v
            this.form.value = 0
        },
        changeValue: function (v) {
            v = parseFloat(v)
            if (!this.checkValue(v)) return
            this.form.value = parseFloat(v.toFixed(2))
        },
        checkValue: function (v) {
            if (v <= 0) {
                this.form.value = 0
                this.negativeValue(v)
                return false
            }
            if (this.form.type === 'percentage' && v > 100) {
                this.form.value = 100
                this.invalidPercentage(v)
                return false
            }
            return true
        }
    },
    mounted: function () {
        this.negativeValue = throttle((v) => {
            this.$pToast.open({message: `Value should be greater than 0. Got "${v}"`, error: true, duration: 5000})
        }, 5000)
        this.invalidPercentage = throttle((v) => {
            this.$pToast.open({message: `Value should not greater than 0. Got "${v}"`, error: true, duration: 5000})
        }, 5000)
        this.$emit('title', 'Create discount code')
    }
}
</script>
