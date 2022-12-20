<template>
    <PLayout>
        <ValidationObserver ref="form" slim>
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
                        <ValidationProvider
                            v-if="form.method === 'code'"
                            name="Discount code"
                            rules="required"
                            v-slot="{errors}">
                            <PTextField label="Discount code" v-model="form.code" :error="errors[0]"
                                        help-text="Customers must enter this code at checkout" connected>
                                <PButton slot="connectedRight" :disabled="isSaving" @click="generateCode">Generate
                                </PButton>
                            </PTextField>
                        </ValidationProvider>
                        <ValidationProvider
                            v-else
                            name="Title"
                            rules="required"
                            v-slot="{errors}">
                            <PTextField label="Title" :error="errors[0]"
                                        help-text="Customers will see this in their cart and at checkout"
                                        v-model="form.title"/>
                        </ValidationProvider>
                    </PFormLayout>
                </PCard>
                <PCard sectioned title="Value">
                    <PFormLayout>
                        <PFormLayoutGroup>
                            <PButtonGroup segmented>
                                <PButton
                                    :pressed="form.type === 'percentage'"
                                    @click="changeValueType('percentage')" :disabled="isSaving">Percentage
                                </PButton>
                                <PButton
                                    :pressed="form.type === 'fixed'"
                                    @click="changeValueType('fixed')" :disabled="isSaving">Fixed amount
                                </PButton>
                            </PButtonGroup>
                            <div>
                                <ValidationProvider
                                    v-show="form.type === 'percentage'"
                                    name="Value"
                                    rules="between:0,100"
                                    v-slot="{errors}">
                                    <PTextField type="number" v-model="form.value" @input="changeValue"
                                                :error="errors[0]">
                                        <div slot="suffix">%</div>
                                    </PTextField>
                                </ValidationProvider>
                                <ValidationProvider
                                    v-show="form.type === 'fixed'"
                                    name="Value"
                                    rules="min_value:0"
                                    v-slot="{errors}">
                                    <PTextField type="number" v-model="form.value" @input="changeValue"
                                                :error="errors[0]">
                                        <div slot="prefix">$</div>
                                    </PTextField>
                                </ValidationProvider>
                            </div>
                        </PFormLayoutGroup>
                    </PFormLayout>
                </PCard>
                <PCard sectioned title="Minimum purchase requirements">
                    TODO - Default None
                    Cost, Currency, Amount, Attributes, etc.
                    https://shopify.dev/api/functions/reference/order-discounts/graphql/common-objects/cart
                </PCard>
                <PCard sectioned title="Product eligibility">
                    TODO - metafield, inAnyCollection, isGiftCard, productType, vendor, etc.
                    https://shopify.dev/api/functions/reference/order-discounts/graphql/common-objects/product
                </PCard>
                <PCard sectioned title="Customer eligibility">
                    TODO - amountSpend, hasAnyTag, numberOfOrders, metafield, etc.
                    https://shopify.dev/api/functions/reference/order-discounts/graphql/common-objects/customer
                </PCard>
                <PCard sectioned title="Maximum discount uses" v-show="form.code === 'code'">
                    TODO
                    appliesOncePerCustomer
                    customerSelection -> Customer Segment
                    usageLimit
                </PCard>
                <PCard sectioned title="Combinations">
                    TODO - Default None
                    Product Discount, Order Discount and Shipping Discount.
                    I assume it could only allow applying one of each above.
                </PCard>
                <PCard sectioned title="Active dates">
                    TODO - Default active from now
                    Start and End Date
                </PCard>
                <PCard style="background: transparent; box-shadow: none;">
                    <PButtonGroup>
                        <PButton :loading="isSaving">Discard</PButton>
                        <PButton primary :loading="isSaving" @click="saveData">Save</PButton>
                    </PButtonGroup>
                </PCard>
            </PLayoutSection>
        </ValidationObserver>
        <PLayoutSection secondary>
            <PCard sectioned title="Summary">
                <div>Summary TODO</div>
            </PCard>
        </PLayoutSection>
    </PLayout>
</template>

<script>
import {ValidationProvider, ValidationObserver, extend} from "vee-validate"
import {required} from "vee-validate/dist/rules"
import {getApi} from "../store/getters"
import common from "../utils/common"

extend('required', required)
extend('between', {
    validate(value, {min, max}) {
        value = parseFloat(value)
        min = parseFloat(min)
        max = parseFloat(max)
        if (isNaN(value) || isNaN(min) || isNaN(max)) return false
        return value > min && value <= max
    },
    params: ['min', 'max'],
})
extend('min_value', {
    validate(value, {min}) {
        value = parseFloat(value)
        min = parseFloat(min)
        if (isNaN(value) || isNaN(min)) return false
        return value > min
    },
    params: ['min']
})

export default {
    name: "Discount",
    mixins: [common],
    props: ['code_id'],
    components: {ValidationObserver, ValidationProvider},
    data: () => ({
        summary: [],
        form: {
            method: 'code',
            code: null,
            title: null,
            type: 'percentage',
            value: 0,
        },
        isSaving: false,
    }),
    methods: {
        changeMethod: function (e) {
            this.form.method = e.value
            this.form.method === 'code' ? this.form.title = null : this.form.code = null
        },
        changeValueType: function (v) {
            this.form.type = v
            this.form.value = 0
        },
        changeValue: function (v) {
            v = parseFloat(v)
            if (isNaN(v)) return
            this.form.value = parseFloat(v.toFixed(2))
        },
        generateCode: function () {
            this.isSaving = true
            this.$http.get(getApi('discount_code', 'generate')).then(({data}) => {
                this.form.code = data.data
                this.isSaving = false
            }).catch(this.errorHandle)
        },
        createCode: function (form) {
            this.isSaving = true
            this.$http.post(getApi('discount_code', 'create'), form).then(({data}) => {
                console.log(data)
                this.isSaving = false
                this.$pToast.open({message: 'Discount code created!'})
            }).catch(this.errorHandle)
        },
        updateCode: function (form) {
            this.isSaving = true
            this.$http.put(getApi('discount_code', `${this.record_id}`), form).then(({data}) => {
                console.log(data)
                this.isSaving = false
                this.$pToast.open({message: 'Discount code updated!'})
            }).catch(this.errorHandle)
        },
        saveData: async function () {
            let valid = await this.$refs.form.validate()
            if (!valid) return
            let form = Object.assign({}, this.form)
            form.method === 'code' ? delete form['title'] : delete form['code']
            return this.code_id === undefined ? this.createCode(form) : this.updateCode(form)
        }
    },
    mounted: function () {
        this.$emit('title', 'Create discount code')
    }
}
</script>
