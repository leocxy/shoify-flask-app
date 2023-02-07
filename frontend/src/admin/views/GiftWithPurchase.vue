<template>
    <ValidationObserver ref="form" class="Polaris-Layout">
        <PLayoutAnnotatedSection title="Step 1: Choosing the method">
            <div slot="description">This guy is lazy, he leave nothing here.</div>
            <PCard sectioned title="Method">
                <PButton slot="children" :loading="isSaving" @click="generateScript" primary size="slim">
                    Generate Ruby Script
                </PButton>
                <PFormLayout>
                    <PCheckbox
                        id="gwp_status"
                        :checked="form.enable === true"
                        label="Enable GWP function"
                        help-text="You still need to enable the Checkout UI via Theme Editor and paste the ruby script on Script Editor."
                        @change="form.enable = $event.checked"/>
                    <PStack vertical alignment="leading" spacing="extraTight">
                        <PStackItem>
                            <PRadioButton
                                id="quantity"
                                label="Quantity"
                                help-text="Based on the total quantity of eligible products"
                                name="method"
                                :checked="form.method === 1"
                                value="1"
                                @change="changeMethod"/>
                        </PStackItem>
                        <PStackItem>
                            <PRadioButton
                                id="total_amount"
                                label="Total amount"
                                help-text="Based on the total amount of the eligible products"
                                name="method"
                                :checked="form.method === 2"
                                value="2"
                                @change="changeMethod"/>
                        </PStackItem>
                    </PStack>
                    <ValidationProvider
                        v-if="form.method === 1"
                        name="Quantity"
                        rules="required|min_value:1"
                        v-slot="{errors}">
                        <PTextField
                            label="Quantity"
                            v-model="form.value"
                            help-text="The total quantity of eligible products"
                            :error="errors[0]" type="number"/>
                    </ValidationProvider>
                    <ValidationProvider
                        v-else
                        name="Total amount"
                        rules="required|min_value:0"
                        v-slot="{errors}">
                        <PTextField
                            label="Total amount"
                            v-model="form.value"
                            :error="errors[0]"
                            help-text="Up to 2 digits after the decimal point"
                            type="number"
                            connected>
                            <PButton slot="connectedLeft" disabled>$</PButton>
                        </PTextField>
                    </ValidationProvider>
                    <PCheckbox
                        id="force_remove"
                        :checked="form.force_remove === true"
                        label="Force remove"
                        help-text="Remove the gift product form the cart automatic unless meeting the requirement"
                        @change="form.force_remove = $event.checked"/>
                    <ValidationProvider
                        name="Discount message"
                        rules="required"
                        v-slot="{errors}">
                        <PTextField
                            v-model="form.message"
                            label="Discount message"
                            :error="errors[0]"/>
                    </ValidationProvider>
                    <ValidationProvider
                        name="Secret number"
                        rules="required|integer"
                        v-slot="{errors}">
                        <PTextField
                            v-model="form.secret_number"
                            label="Secret number"
                            help-text="Integer number"
                            type="number"
                            :error="errors[0]"/>
                    </ValidationProvider>
                </PFormLayout>
            </PCard>
        </PLayoutAnnotatedSection>
        <PLayoutAnnotatedSection title="Step 2: Pre requirements">
            <div slot="description">This guy is lazy, he leave nothing here.</div>
            <PCard sectioned title="Pre Requirements">
                <PButton primary :loading="isSaving" @click="pickProduct" size="slim" slot="children">Pick products
                </PButton>
                <div class="product-blocks">
                    <div class="product-block" v-for="(v, i) in form.pre_requirements" :key="i">
                        <div class="product-content">
                            <div class="product-image">
                                <PThumbnail :source="v.image" v-if="v.image"/>
                                <PSkeletonThumbnail v-else/>
                            </div>
                            <div class="product-action">
                                <PLink @click="toProductPage(v.pid)" class="product-title">{{ v.title }}</PLink>
                                <PButton destructive plain
                                         @click="removeProduct(i)"
                                         :loading="isSaving" size="slim">Remove
                                </PButton>
                            </div>
                        </div>
                    </div>
                </div>
                <PButtonGroup slot="footer">
                    <PButton primary :loading="isSaving" @click="pickProduct">Pick products</PButton>
                </PButtonGroup>
            </PCard>
        </PLayoutAnnotatedSection>
        <PLayoutAnnotatedSection title="Step 3: Free Gfit">
            <div slot="description">This guy is lazy, he leave nothing here.</div>
            <PCard sectioned title="Gfit Product">
                <PButton primary :loading="isSaving" @click="selectTarget" size="slim" slot="children">Pick product
                </PButton>
                <div class="product-blocks" v-if="form.target !== null">
                    <div class="product-block">
                        <div class="product-content">
                            <div class="product-image">
                                <PThumbnail :source="form.target.image" v-if="form.target.image"/>
                                <PSkeletonThumbnail v-else/>
                            </div>
                            <div class="product-action">
                                <PLink @click="toProductPage(form.target.pid)" class="product-title">{{
                                        form.target.title
                                    }}
                                </PLink>
                                <PButton destructive plain :loading="isSaving" @click="form.target = null">Remove
                                </PButton>
                            </div>
                        </div>
                    </div>
                </div>
                <PTextContainer v-else>
                    <PTextStyle variation="negative">No Data</PTextStyle>
                    <ValidationProvider
                        name="Gift Product"
                        rules="required"
                        v-slot="{errors}">
                        <input v-model="form.target" type="hidden"/>
                        <PFieldError v-if="errors.length > 0">{{ errors[0] }}</PFieldError>
                    </ValidationProvider>
                </PTextContainer>
                <PButtonGroup slot="footer" segmented>
                    <PButton primary :loading="isSaving" @click="selectTarget">Pick product</PButton>
                </PButtonGroup>
            </PCard>
        </PLayoutAnnotatedSection>
        <PLayoutAnnotatedSection title="Step 4: Ruby Script for Script Editor">
            <div slot="description">This guy is lazy, he leave nothing here.</div>
            <PCard sectioned title="Ruby Script">
                <PButton slot="children" :loading="isSaving" @click="generateScript" primary size="slim">
                    Generate Ruby Script
                </PButton>
                <PTextContainer v-if="ruby_script === ''">
                    <PTextStyle variation="negative">No Data</PTextStyle>
                </PTextContainer>
                <div v-else>
                    <PTextStyle variation="positive">### Start Here ###</PTextStyle>
                    <div v-html="compileMarkdown" class="code-container"></div>
                    <PTextStyle variation="positive">### End Here ###</PTextStyle>
                </div>
                <PButtonGroup slot="footer">
                    <PButton primary :loading="isSaving" @click="saveData">Save</PButton>
                    <PButton :loading="isSaving" @click="$router.go(-1)">Cancel</PButton>
                </PButtonGroup>
            </PCard>
        </PLayoutAnnotatedSection>
    </ValidationObserver>
</template>

<script>
import {ValidationObserver, ValidationProvider, extend} from "vee-validate"
import {required} from 'vee-validate/dist/rules'
import {marked} from 'marked'
import {getApi} from "../store/getters"
import common from "../utils/common"
import {redirectAdmin, productPicker} from "../store/actions"
import isEmpty from 'lodash/isEmpty'

extend('required', required)
extend('min_value', {
    validate(value, {min}) {
        value = parseFloat(value)
        min = parseFloat(min)
        if (isNaN(value) || isNaN(min)) return false
        return value >= min
    },
    params: ['min']
})
extend('integer', {
    validate(value) {
        return parseFloat(value) === parseInt(value)
    }
})

export default {
    name: "GiftWithPurchase",
    mixins: [common],
    components: {ValidationObserver, ValidationProvider},
    data: () => ({
        form: {
            enable: false,
            method: 1, // 1 for quantity, 2 for total amount
            value: null,
            pre_requirements: [],
            target: null,
            message: 'Gift with purchase', // discount message
            force_remove: false, // remove the target product automatic ?
            secret_number: null, // Script for script editor, need this to verify the discount price
        },
        ruby_script: '',
        ruby_template: `\`\`\`ruby\n{nil}\n\`\`\`\n`,
        markdown: null,
        isSaving: false
    }),
    computed: {
        compileMarkdown: function () {
            return marked(this.ruby_script, {sanitize: true})
        }
    },
    methods: {
        changeMethod: function (e) {
            e = parseInt(e.value)
            if (e !== this.form.method) this.form.value = null
            this.form.method = e
        },
        toProductPage: function (pid) {
            redirectAdmin(`/products/${pid}`)
        },
        pickProduct: function () {
            productPicker({
                showVariants: false,
                selectMultiple: true,
                initialSelectionIds: [],
                select_cb: (products) => {
                    let olds = this.form.pre_requirements.filter(obj => !products.find(product => product.id.includes(obj.pid)))
                    this.form.pre_requirements = products.map(product => ({
                        pid: parseInt(product.id.split('/').pop()),
                        title: product.title,
                        handle: product.handle,
                        image: product.images.length > 0 ? product.images[0].originalSrc : null
                    }))
                    this.form.pre_requirements.push(...olds)
                    console.log(this.form.pre_requirements)
                }
            })
        },
        removeProduct: function (index) {
            this.form.pre_requirements.splice(index, 1)
        },
        selectTarget: function () {
            productPicker({
                showVariants: false,
                selectMultiple: false,
                select_cb: (products) => {
                    if (products.length === 0) return this.form.target = null
                    let product = products[0]
                    this.form.target = {
                        pid: parseInt(product.id.split('/').pop()),
                        vid: parseInt(product.variants[0].id.split('/').pop()),
                        title: product.title,
                        handle: product.handle,
                        image: product.images.length > 0 ? product.images[0].originalSrc : null
                    }
                }
            })
        },
        generateScript: async function () {
            let valid = await this.$refs.form.validate()
            if (!valid) return
            this.isSaving = true
            this.$http.post(getApi('gwp', 'script'), this.form).then(({data}) => {
                this.ruby_script = this.ruby_template.replace('{nil}', data.data)
                this.$pToast.open({message: 'Ruby script updated!'})
                this.isSaving = false
            }).catch(this.errorHandle)
        },
        saveData: async function () {
            let valid = await this.$refs.form.validate()
            if (!valid) return
            this.isSaving = true
            this.$http.post(getApi('gwp'), this.form).then(({data}) => {
                data = data.data
                this.ruby_script = this.ruby_template.replace('{nil}', data.script)
                delete data['script']
                this.form = {...this.form, ...data}
                this.$pToast.open({message: 'Gift with purchase data hav been saved!'})
                this.isSaving = false
            }).catch(this.errorHandle)
        },
        loadData: function () {
            this.isSaving = true
            this.$http.get(getApi('gwp')).then(({data}) => {
                data = data.data
                if (isEmpty(data)) return this.isSaving = false
                if (data?.script !== undefined) this.ruby_script = this.ruby_template.replace('{nil}', data.script)
                delete data['script']
                this.form = {...this.form, ...data}
                this.isSaving = false
            }).catch(this.errorHandle)
        }
    },
    mounted: function () {
        this.loadData()
        this.$emit('title', 'Gift with Purchase')
    }
}
</script>

<style lang="scss" scoped>
$grey: #cacccf;
@mixin media($max: false, $min: false) {
    @if $max {
        @if $min {
            @media screen and (max-width: $max - 1) and (min-width: $min) {
                @content;
            }
        } @else {
            @media screen and (max-width: $max - 1) {
                @content;
            }
        }
    } @else {
        @media screen and (min-width: $min) {
            @content;
        }
    }
}

.product-blocks {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    width: 100%;

    .product-block {
        padding: 10px;
        width: 100%;

        .product-content {
            padding: 10px;
            margin: 0;
            border: 1px solid $grey;
            width: 100%;
            display: flex;

            .product-image {
                margin-right: 1rem;
            }

            .product-action {
                display: flex;
                flex-direction: column;

                .Polaris-Button--plain {
                    padding: 0.3rem 0;
                    margin: 0;
                    justify-content: start;
                }
            }

            .product-title {
                width: 100%;
                max-width: 150px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
            }
        }

        @include media($min: 640px) {
            width: 50%;
        }

        @include media($min: 1024px) {
            width: 33.33%;
        }

        @include media($min: 1680px) {
            width: 25%;
        }
    }
}

.code-container {
    background: $grey;
    padding: 0 1.5rem;
}
</style>
