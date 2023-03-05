<template>
    <PLayout>
        <ValidationObserver ref="form" slim>
            <PLayoutSection>
                <PCard sectioned title="Amount off order">
                    <div slot="children">
                        Order discount
                    </div>
                    <PFormLayout>
                        <PStack vertical alignment="leading" spacing="extraTight" v-if="code_id === undefined">
                            <PStackItem>
                                <PRadioButton id="discount_code" label="Discount code" name="type"
                                              :checked="form.type === 'code'" value="code"
                                              @change="changeMethod"/>
                            </PStackItem>
                            <PStackItem>
                                <PRadioButton id="auto_discount" label="Automatic discount" name="method"
                                              :checked="form.type !== 'code'" value="auto"
                                              @change="changeMethod"/>
                            </PStackItem>
                        </PStack>
                        <ValidationProvider
                            v-if="form.type === 'code'"
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
                                    :pressed="form.method === 'percentage'"
                                    @click="changeDiscountMethod('percentage')" :disabled="isSaving">Percentage
                                </PButton>
                                <PButton
                                    :pressed="form.method === 'fixed'"
                                    @click="changeDiscountMethod('fixed')" :disabled="isSaving">Fixed amount
                                </PButton>
                            </PButtonGroup>
                            <div>
                                <ValidationProvider
                                    v-show="form.method === 'percentage'"
                                    name="Value"
                                    rules="between:0,100"
                                    v-slot="{errors}">
                                    <PTextField type="number" v-model="form.value" @input="changeValue"
                                                :error="errors[0]">
                                        <div slot="suffix">%</div>
                                    </PTextField>
                                </ValidationProvider>
                                <ValidationProvider
                                    v-show="form.method === 'fixed'"
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
                        <PFormLayoutGroup>
                            <PTextField value="5" label="Quantity Threshold" disabled help-text="Just hardcode this for demo"/>
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
                        <PButton destructive :loading="isSaving" v-if="code_id" @click="showModal()">Delete discount
                        </PButton>
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
        <PModal
            :open="modal.open"
            sectioned>
            <PTextContainer slot="title">
                <PTextStyle variation="strong">{{ modal.title }}</PTextStyle>
            </PTextContainer>
            <PTextContainer>
                {{ modal.content }}
            </PTextContainer>
            <PButtonGroup slot="footer">
                <PButton @click="modal.open = false">Cancel</PButton>
                <PButton :loading="isSaving" @click="deleteCode" destructive>Delete discount</PButton>
            </PButtonGroup>
        </PModal>
    </PLayout>
</template>

<script>
import {ValidationProvider, ValidationObserver, extend} from "vee-validate"
import {required} from "vee-validate/dist/rules"
import {getApi} from "../store/getters"
import common from "../utils/common"
import {redirectAdmin} from "../store/actions"

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
            type: 'code',
            code: null,
            title: null,
            method: 'percentage',
            value: 0,
        },
        modal: {
            open: false,
            title: null,
            content: null,
        },
        isSaving: false,
    }),
    methods: {
        changeMethod: function (e) {
            this.form.type = e.value
            this.form.type === 'code' ? this.form.title = null : this.form.code = null
        },
        changeDiscountMethod: function (v) {
            this.form.method = v
            this.form.value = 0
        },
        changeValue: function (v) {
            v = parseFloat(v)
            if (isNaN(v)) return
            this.form.value = parseFloat(v.toFixed(2))
        },
        generateCode: function () {
            this.isSaving = true
            this.$http.get(getApi('generate_code')).then(({data}) => {
                this.form.code = data.data
                this.isSaving = false
            }).catch(this.errorHandle)
        },
        createCode: function (form) {
            this.isSaving = true
            this.$http.post(getApi('discount_code', 'create'), form).then(({data}) => {
                this.isSaving = false
                this.$pToast.open({message: 'Discount code created!'})
                // redirect to discount code detail page
                this.$router.push({name: 'discount.edit', params: {code_id: data.data.code_id}})
            }).catch(this.errorHandle)
        },
        updateCode: function (form) {
            this.isSaving = true
            this.$http.put(getApi('discount_code', `${this.code_id}`), form).then(({data}) => {
                this.formatData(data.data)
                this.$pToast.open({message: 'Discount code updated!'})
                this.isSaving = false
            }).catch(this.errorHandle)
        },
        deleteCode: function () {
            this.isSaving = true
            this.$confirm('Are you sure you want to delete this code?').then(() => {
                this.$http.delete(getApi('discount_code', `${this.code_id}`)).then(() => {
                    this.$pToast.open({message: 'Discount code has been deleted!'})
                    this.isSaving = false
                    redirectAdmin({path: '/discounts', newContext: false})
                }).catch(this.errorHandle)
            }).catch(() => this.isSaving = false)
        },
        showModal: function () {
            let name = this.form.code || this.form.title
            this.modal.title = `Delete ${name}`
            this.modal.content = `Are you sure you want to delete the discount ${name}? This can’t be undone.`
            this.modal.open = true
        },
        saveData: async function () {
            let valid = await this.$refs.form.validate()
            if (!valid) return
            let form = Object.assign({}, this.form)
            form.type === 'code' ? delete form['title'] : delete form['code']
            return this.code_id === undefined ? this.createCode(form) : this.updateCode(form)
        },
        formatData: function (data) {
            this.$emit('title', data?.code_name || 'Unknown code')
            this.form.method = data.method === 1 ? 'percentage' : 'fixed'
            this.form.value = data.value
            if (data.code_type === 0) {
                this.form.type = 'code'
                this.form.code = data.code_name
            } else {
                this.form.type = 'auto'
                this.form.title = data.code_name
            }
        },
        loadData: function () {
            this.isSaving = true
            this.$http.get(getApi('discount_code', `${this.code_id}`)).then(({data}) => {
                this.formatData(data.data)
                this.isSaving = false
            }).catch(this.errorHandle)
        }
    },
    mounted: function () {
        if (this.code_id) return this.loadData()
        this.$emit('title', 'Create discount code')
    }
}
</script>
