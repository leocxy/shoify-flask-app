<template>
    <ValidationObserver ref="observer" slim>
        <PLayoutAnnotatedSection title="Bundles detail">
            <PTextContainer slot="description">
                Shopify Bundles, add one variant to the cart, it will expend multiple items on the checkout page
            </PTextContainer>
            <PCard sectioned>
                <PHeading slot="title" element="h2">
                    Settings
                </PHeading>
                <PFormLayout>
                    <ValidationProvider
                        name="Bundles' name"
                        rules="required"
                        v-slot="{ errors }">
                        <PTextField
                            label="Bundles' Name"
                            v-model="name"
                            :error="errors[0]"
                            help-text="Name of the bundles, you can search this record via the name."/>
                    </ValidationProvider>
                    <PStack vertical>
                        <PStackItem>
                            <PRadioButton
                                id="disable" label="Disable"
                                help-text="Disabled the bundles"
                                name="status" :checked="status === 0"/>
                        </PStackItem>
                        <PStackItem>
                            <PRadioButton
                                id="enable" label="Enable"
                                help-text="Enable the bundles"
                                name="status" :checked="status === 1"/>
                        </PStackItem>
                    </PStack>
                </PFormLayout>
                <PButtonGroup slot="footer">
                    <PButton :loading="isSaving" primary @click="saveRecord">Save</PButton>
                </PButtonGroup>
            </PCard>
            <PCard sectioned>
                <PHeading slot="title" element="h2">
                    Parent Variant
                </PHeading>
                <PTextContainer slot="short_description">
                    A variant only allow have one bundles record. <br/>
                    A parent variant should associate with multiple child variants. <br/>
                    <PTextStyle variation="negative">The parent variant's price will be updated once the record is
                        saved!
                    </PTextStyle>
                </PTextContainer>
                <div>
                    <ValidationProvider
                        name="Product variant"
                        rules="required"
                        v-slot="{ errors }">
                        <input v-model="parent.pid" type="hidden"/>
                        <PFieldError v-show="errors.length > 0" :error="errors[0]"/>
                    </ValidationProvider>
                    <PStack v-if="parent.pid">
                        <PStackItem>
                            <PThumbnail v-if="parent.image" :source="parent.image"/>
                            <PSkeletonThumbnail v-else/>
                        </PStackItem>
                        <PStackItem>
                            <PStack vertical spacing="extraTight">
                                <PStackItem>
                                    Title:
                                    <PLink @click="openVariantPage(parent)">{{ parent.product_title }}</PLink>
                                </PStackItem>
                                <PStackItem>
                                    SKU:
                                    <PTextStyle>{{ parent.sku }}</PTextStyle>
                                </PStackItem>
                                <PStackItem>
                                    <PButton size="slim" destructive @click="removeParentVariant">Remove</PButton>
                                </PStackItem>
                            </PStack>
                        </PStackItem>
                    </PStack>
                </div>
                <PButtonGroup slot="footer">
                    <PButton :loading="isSaving" @click="pickParentVariant">Pick a variant</PButton>
                    <PButton :loading="isSaving" primary @click="saveRecord">Save</PButton>
                </PButtonGroup>
            </PCard>
            <PCard sectioned>
                <PHeading slot="title" element="h2">
                    Child Variants
                </PHeading>
                <PTextContainer slot="short_description">
                    The child variant should not be a parent variant (prevent the recursion). <br/>
                    But the same child variant could be assign to multiple parent variants.
                </PTextContainer>
                <ChildVariants
                    :is-saving="isSaving"
                    :variants="children"
                    :total_price="total_price"
                    :total_discount="total_discount"
                    @edit-price="editTotalPrice"
                    @edit-discount="editDiscount"
                    @edit-quantity="editChildVariantQuantity"
                    @refresh-item="refreshChildVariant"
                    @remove-item="removeChildVariant"/>
                <PButtonGroup slot="footer">
                    <PButton :loading="isSaving" @click="pickChildVariants">Pick variants</PButton>
                    <PButton :loading="isSaving" primary @click="saveRecord">Save</PButton>
                </PButtonGroup>
            </PCard>
        </PLayoutAnnotatedSection>
    </ValidationObserver>
</template>

<script>
import {extend} from 'vee-validate'
import {required} from 'vee-validate/dist/rules'
import cloneDeep from "lodash/cloneDeep"
import multiply from 'lodash/multiply'
import divide from 'lodash/divide'
import common from "../../../utils/common"
import curd from "../../../utils/curd"
import {variantPicker, redirectAdmin} from "../../../store/actions"
import ChildVariants from "./ChildVariants"

extend('required', required)

export default {
    name: "BundleDetail",
    mixins: [common, curd],
    components: {ChildVariants},
    data: () => ({
        name: null,
        status: 0,
        total_price: 0,
        total_discount: 0,
        parent: {pid: null, vid: null, product_title: null, image: null, sku: null, barcode: null},
        children: [],
        isSaving: false
    }),
    methods: {
        openVariantPage: function (obj) {
            return redirectAdmin({
                path: `/products/${obj.pid}/variants/${obj.vid}`,
                newContext: true
            })
        },
        removeParentVariant: function () {
            this.parent = {pid: null, vid: null, product_title: null, image: null, sku: null, barcode: null}
        },
        pickParentVariant: function () {
            variantPicker({
                selectMultiple: false,
                select_cb: (variants) => {
                    variants = variants.map(v => {
                        return {
                            pid: parseInt(v.product.id.split('/').pop()),
                            vid: parseInt(v.id.split('/').pop()),
                            product_title: v.title,
                            image: v.image?.id ? v.image.originalSrc : null,
                            sku: v.sku,
                            barcode: v.barcode,
                        }
                    })
                    if (variants.length > 0) this.parent = Object.assign(this.parent, variants[0])
                }
            })
        },
        removeChildVariant: function (i) {
            this.children.splice(i, 1)
            this.recalculate()
        },
        refreshChildVariant: function (i, vid) {
            console.log(i, vid)
        },
        editChildVariantQuantity: function (i, val) {
            this.children[i]['quantity'] = val
            this.recalculate()
        },
        pickChildVariants: function () {
            variantPicker({
                selectMultiple: true,
                select_cb: (variants) => {
                    let children = cloneDeep(this.children)
                    variants = variants.map(v => {
                        let vid, found, price;
                        vid = parseInt(v.id.split('/').pop())
                        price = parseInt(multiply(v.price, 100))
                        found = this.children.find(v => v.vid === vid)
                        // Remove it
                        if (found) children = children.filter(v => v.vid !== found.vid)
                        return {
                            pid: parseInt(v.product.id.split('/').pop()),
                            vid: vid,
                            title: v.title,
                            image: v.image?.id ? v.image.originalSrc : null,
                            sku: v.sku,
                            barcode: v.barcode,
                            origin_price: price,
                            price: found ? found.price : price,
                            quantity: found ? found.quantity : 1,
                            discount: null,
                        }
                    })
                    Array.prototype.push.apply(variants, children)
                    // re-calculate the discount
                    variants = this.recalculate(variants)
                    this.$set(this, 'children', variants)
                }
            })
        },
        recalculate: function (variants) {
            return this.total_discount === 0 ? this.calculateByTotal(variants) : this.calculateByDiscount(variants)
        },
        calculateByTotal: function (variants) {
            variants = variants ? variants : this.children
            let total_price, origin_total = 0, total_discount;
            variants.forEach(v => {
                origin_total += multiply(v.origin_price, v.quantity)
            })
            total_price = this.total_price === 0 ? origin_total : this.total_price
            if (total_price > origin_total) {
                total_price = origin_total
                this.$pToast.open({message: 'Total price can`t greater than original total price!', error: true})
            }
            total_discount = parseFloat(divide(total_price, origin_total).toFixed(4))
            this.total_discount = parseFloat(multiply(total_discount, 100).toFixed(2))
            console.log('debug', total_discount, this.total_discount, total_price, origin_total)
            this.total_price = total_price
            variants.forEach(v => {
                v.price = parseInt(multiply(v.origin_price, total_discount))
                v.discount = this.total_discount
            })
            // @todo 补差价 0.01 之类的
            return variants
        },
        calculateByDiscount: function (variants) {
            variants = variants ? variants : this.children
            let total_price = 0, discount = multiply(this.total_discount, 0.01);
            variants.forEach(v => {
                v.price = parseInt(multiply(v.origin_price, discount))
                v.discount = this.total_discount
                total_price += parseInt(multiply(v.price, v.quantity))
            })
            this.total_price = total_price
            // @todo 补差价 0.01 之类的
            return variants
        },
        editTotalPrice: function (v) {
            this.total_price = v
            this.calculateByTotal()
        },
        editDiscount: function (v) {
            this.total_discount = v
            this.calculateByDiscount()
        },
        saveRecord: function () {
            this.$refs.observer.validate().then(res => {
                console.log(res, 'test')
                if (!res) return this.$pToast.open({message: 'Something wrong with the form!', error: true})
                // this.isSaving = true
                // Create or Update
            })
        },
        createRecord: function () {

        },
        updateRecord: function () {

        }
    },
    mounted: function () {
        this.parent = {
            pid: 8257514406196,
            vid: 45010329174324,
            product_title: "Selling Plans Ski Wax",
            image: "https://cdn.shopify.com/s/files/1/0760/7985/7972/products/snowboard_wax.png?v=1682981701",
            sku: "",
            barcode: null
        }
        this.children = [
            {
                "pid": 8257514012980,
                "vid": 45010328486196,
                "title": "Ice",
                "image": null,
                "sku": "",
                "barcode": null,
                "origin_price": 69995,
                "price": 69995,
                "quantity": 1,
                "discount": null
            },
            {
                "pid": 8257514012980,
                "vid": 45010328584500,
                "title": "Powder",
                "image": null,
                "sku": "",
                "barcode": null,
                "origin_price": 69995,
                "price": 69995,
                "quantity": 1,
                "discount": null
            },
            {
                "pid": 8257514406196,
                "vid": 45010329272628,
                "title": "Sample Selling Plans Ski Wax",
                "image": "https://cdn.shopify.com/s/files/1/0760/7985/7972/products/sample-normal-wax.png?v=1682981701",
                "sku": "",
                "barcode": null,
                "origin_price": 994,
                "price": 994,
                "quantity": 1,
                "discount": null
            },
            {
                "pid": 8257514406196,
                "vid": 45010329174324,
                "title": "Selling Plans Ski Wax",
                "image": "https://cdn.shopify.com/s/files/1/0760/7985/7972/products/snowboard_wax.png?v=1682981701",
                "sku": "",
                "barcode": null,
                "origin_price": 2495,
                "price": 2495,
                "quantity": 1,
                "discount": null
            },
            {
                "pid": 8257514406196,
                "vid": 45010329207092,
                "title": "Special Selling Plans Ski Wax",
                "image": "https://cdn.shopify.com/s/files/1/0760/7985/7972/products/wax-special.png?v=1682981701",
                "sku": "",
                "barcode": null,
                "origin_price": 4995,
                "price": 4995,
                "quantity": 1,
                "discount": null
            }
        ]
    }
}
</script>
