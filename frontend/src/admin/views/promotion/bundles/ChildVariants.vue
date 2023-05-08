<template>
    <div class="vue-table-container">
        <PFormLayout style="margin-bottom: 1.5rem;">
            <div>
                <div class="Polaris-Connected">
                    <div class="Polaris-Connected__Item Polaris-Connected__Item--primary">
                        <input type="text" class="Polaris-TextField__Input" v-model="query_string"
                               @keyup.enter="queryItem">
                        <div class="Polaris-TextField__Backdrop"></div>
                    </div>
                    <div class="Polaris-Connected__Item Polaris-Connected__Item--connection">
                        <PButtonGroup segmented>
                            <PButton primary :loading="isSaving" @click="queryItem">Query</PButton>
                        </PButtonGroup>
                    </div>
                </div>
                <div class="Polaris-Labelled__HelpText">Query via title, sku, and barcode ...</div>
                <PFieldError :error="query_error" v-if="query_error !== null"/>
            </div>
        </PFormLayout>
        <VueTable
            :api-mode="false"
            :fields="table_fields"
            :per-page="per_page"
            pagination-path="pagination"
            :data-manager="dataManager"
            ref="datatable"
            :css="tableCss"
            @vuetable:pagination-data="onPaginationData">
            <template slot="variant" slot-scope="{rowData}">
                <PStack spacing="tight">
                    <PStackItem>
                        <PThumbnail v-if="rowData.image" :source="rowData.image"/>
                        <PSkeletonThumbnail v-else/>
                    </PStackItem>
                    <PStackItem>
                        <PStack vertical alignment="leading" spacing="tight">
                            <PStackItem>
                                Title:
                                <PLink @click="openVariantPage(rowData)">{{ rowData.title }}</PLink>
                            </PStackItem>
                            <PStackItem>
                                <PTextStyle>SKU: {{ rowData.sku }}</PTextStyle>
                            </PStackItem>
                        </PStack>
                    </PStackItem>
                </PStack>
            </template>
            <template slot="origin_price" slot-scope="{rowData}">
                ${{ formatPrice(rowData.origin_price) }}
            </template>
            <template slot="price" slot-scope="{rowData}">
                ${{ formatPrice(rowData.price) }}
            </template>
            <template slot="quantity" slot-scope="{rowData, rowIndex}">
                <PTextField
                    type="number"
                    :value="rowData.quantity"
                    @input="editQuantity(rowIndex, $event)">
                </PTextField>
            </template>
            <PButtonGroup slot="action" slot-scope="{rowData, rowIndex}">
                <PButton icon="DeleteMinor" destructive icon-only :loading="isSaving" @click="removeItem(rowIndex)"/>
                <PButton icon="RefreshMinor" primary icon-only :loading="isSaving" @click="refreshItem(rowIndex, rowData.vid)"/>
            </PButtonGroup>
        </VueTable>
        <div style="overflow:auto;margin-top: 0.8rem;">
            <VueTablePagination ref="pagination" @vuetable-pagination:change-page="onChangePage"/>
        </div>
        <PFormLayout style="margin-top: -0.5rem">
            <PFormLayoutGroup>
                <PTextField
                    id="total_price"
                    type="number"
                    :value="formatPrice(total_price)"
                    @input="editTotal"
                    prefix="$">
                    <PLabel slot="label" id="total_price">
                        Total RRP: ${{ formatPrice(origin_price) }}
                    </PLabel>
                </PTextField>
                <PTextField
                    label="Discount"
                    type="number"
                    :value="total_discount"
                    @input="editDiscount"
                    prefix="%" />
            </PFormLayoutGroup>
        </PFormLayout>
    </div>
</template>

<script>
import common from "../../../utils/common"
import table from "../../../utils/table"
import {redirectAdmin} from "../../../store/actions"
import {slice, orderBy} from "lodash"

export default {
    name: "ChildVariants",
    props: ['isSaving', 'variants', 'total_price', 'origin_price', 'total_discount'],
    mixins: [common, table],
    data: () => ({
        query_string: '',
        query_error: null,
        per_page: 10,
        table_data: [],
        table_fields: [{
            name: '__slot:variant',
            title: 'Variant',
            titleClass: 'center aligned',
            dataClass: 'center aligned'
        }, {
            name: '__slot:origin_price',
            title: 'RRP',
            titleClass: 'center aligned',
            dataClass: 'center aligned',
        }, {
            name: '__slot:price',
            title: 'Price',
            titleClass: 'center aligned',
            dataClass: 'center aligned'
        }, {
            name: '__slot:quantity',
            title: 'Quantity',
            titleClass: 'center aligned',
            dataClass: 'center aligned'
        }, {
            name: '__slot:action',
            title: 'Action',
            titleClass: 'center aligned',
            dataClass: 'center aligned'
        }]
    }),
    watch: {
        variants: function (vals) {
            this.table_data = vals
            this.$refs.datatable.refresh()
        }
    },
    methods: {
        openVariantPage: function (obj) {
            return redirectAdmin({
                path: `/products/${obj.pid}/variants/${obj.vid}`,
                newContext: true
            })
        },
        dataManager: function (sortOrder, pagination) {
            let local = this.table_data, total = local.length;
            if (sortOrder.length > 0) {
                // console.log("orderBy:", sortOrder[0].sortField, sortOrder[0].direction);
                local = orderBy(
                    local,
                    sortOrder[0].sortField,
                    sortOrder[0].direction
                );
            }
            pagination = this.$refs.datatable.makePagination(
                total,
                this.per_page,
            )
            // console.log(pagination)
            let from = pagination.from - 1, to = from + this.per_page;
            return {
                pagination,
                data: slice(local, from, to)
            }
        },
        queryItem: function () {
            let val = this.query_string.toString().toLowerCase().trim()
            if (val.length < 3) {
                this.query_error = 'Enter at least three strings!'
                this.table_data = this.variants
                this.$refs.datatable.refresh()
            }
            this.query_error = null
            this.table_data = this.variants.filter(v => {
                let title = v.title === null ? false : v.title.toLowerCase().includes(val),
                    sku = v.sku === null ? false : v.sku.toLowerCase().includes(val),
                    barcode = v.barcode === null ? false : v.barcode.toLowerCase().includes(val);
                return title || sku || barcode
            })
            this.$refs.datatable.refresh()
        },
        removeItem: function (i) {
            this.$emit('remove-item', i)
        },
        refreshItem: function (i, vid) {
            this.$emit('refresh-item', i, vid)
        },
        editTotal: function (v) {
            v = parseInt(parseFloat(Math.abs(v)).toFixed(2) * 100)
            this.$emit('edit-price', v)
        },
        editDiscount: function (v) {
            v = parseFloat(parseFloat(Math.abs(v)).toFixed(2))
            if (v > 100) {
                v = 100
                this.$pToast.open({message: 'Discount can`t greater than 100%!', error: true})
            }
            this.$emit('edit-discount', v)
        },
        editQuantity: function (i, val) {
            val = Math.ceil(Math.abs(val))
            if (val < 0) {
                val = 1
                this.$pToast.open({message: 'Quantity could not less than zero!', error: true})
            }
            this.$emit('edit-quantity', i, val)
        },
    }
}
</script>
