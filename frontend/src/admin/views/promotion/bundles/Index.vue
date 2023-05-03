<template>
    <PLayoutAnnotatedSection title="Bundles">
        <PTextContainer slot="description">
            Shopify Bundles.<br/>Add one variant to the cart, it will expend multiple items on the checkout page.
        </PTextContainer>
        <MetaDefinition :is-saving="isSaving" @change="btnStatus"/>
        <PCard>
            <div class="Polaris-Card__Header">
                <PStack alignment="baseline">
                    <PStackItem fill>
                        <PHeading element="h2">Bundles records</PHeading>
                    </PStackItem>
                    <PStackItem>
                        <PButtonGroup>
                            <PButton plain icon="ExportMinor">Export</PButton>
                            <PButton plain icon="ImportMinor">Import</PButton>
                            <input style="display: none" type="file" ref="import_file" @change="importExcel"/>
                        </PButtonGroup>
                    </PStackItem>
                </PStack>
            </div>
            <PCardSection>
                <PFormLayout style="margin-bottom: 1.5rem;">
                    <div>
                        <div class="Polaris-Connected">
                            <div class="Polaris-Connected__Item Polaris-Connected__Item--primary">
                                <input type="text" class="Polaris-TextField__Input" v-model="params.name"
                                       @keyup.enter="queryData">
                                <div class="Polaris-TextField__Backdrop"></div>
                            </div>
                            <div class="Polaris-Connected__Item Polaris-Connected__Item--connection">
                                <PButtonGroup segmented>
                                    <PButton primary :loading="isSaving" @click="queryData">Query</PButton>
                                </PButtonGroup>
                            </div>
                        </div>
                        <div class="Polaris-Labelled__HelpText">Query via title,product title, and sku ...</div>
                    </div>
                </PFormLayout>
                <VueTable
                    :api-url="getApi('bundles')"
                    :load-on-start="true"
                    :fields="table_fields"
                    data-path="data.data"
                    pagination-path="data"
                    :per-page="15"
                    :http-options="tableHeaders"
                    ref="datatable"
                    :css="tableCss"
                    :append-params="params"
                    @vuetable:pagination-data="onPaginationData">
                    <template slot="title" slot-scope="{rowData}">
                        <PStack spacing="tight">
                            <PStackItem>
                                <PSkeletonThumbnail v-if="rowData.image === null"/>
                                <PThumbnail v-else :source="rowData.image"/>
                            </PStackItem>
                            <PStackItem>
                                <PStack vertical alignment="leading" spacing="tight">
                                    <PStackItem>
                                        ID:
                                        <PTextStyle variation="positive">{{ rowData.id }}</PTextStyle>
                                    </PStackItem>
                                    <PStackItem>
                                        Title: {{
                                            rowData.title.length > 50 ? rowData.title.substring(0, 47) + '...' : rowData.title
                                        }}
                                    </PStackItem>
                                    <PStackItem>
                                        Product Title: {{
                                            rowData.product_title.length > 50 ? rowData.product_title.substring(0, 47) + '...' : rowData.product_title
                                        }}
                                    </PStackItem>
                                </PStack>
                            </PStackItem>
                        </PStack>
                    </template>
                    <div slot="status" slot-scope="{rowData}">
                        <PIcon source="TickMinor" color="primary" v-if="rowData.status === 1"/>
                        <PIcon source="CancelSmallMinor" color="critical" v-else/>
                    </div>
                    <div slot="actions" slot-scope="{rowData}">
                        <PButtonGroup segmented>
                            <PButton icon="EditMinor" outline icon-only @click="editRecord(rowData.id)"
                                     :loading="isSaving">
                            </PButton>
                            <PButton icon="RefreshMinor" primary icon-only @click="refreshRecord(rowData.id)"
                                     :loading="isSaving">
                            </PButton>
                            <PButton :icon="rowData.status === 1 ? 'PauseCircleMajor' : 'PlayMajor'" icon-only
                                     @click="toggleStatus(rowData.id, rowData.status)" :loading="isSaving"/>
                            <PButton icon="DeleteMinor" destructive icon-only @click="deleteRecord(rowData.id)"
                                     :loading="isSaving">
                            </PButton>
                        </PButtonGroup>
                    </div>
                </VueTable>
            </PCardSection>
            <div slot="footer" class="footer">
                <VueTablePagination ref="pagination" class="pagination-block"
                                     @vuetable-pagination:change-page="onChangePage" />
                <PButtonGroup>
                    <PButton primary :loading="isSaving" @click="$router.push({name: 'bundles.create'})">Create</PButton>
                </PButtonGroup>
            </div>
        </PCard>
    </PLayoutAnnotatedSection>
</template>

<script>
import common from "../../../utils/common"
import table from "../../../utils/table"
import {getApi} from "../../../store/getters"
import MetaDefinition from './MetaDefinition'

export default {
    name: "Bundles",
    mixins: [common, table],
    components: {MetaDefinition},
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
            query: null,
        },
        isSaving: false,
    }),
    methods: {
        btnStatus: function (e) {
            this.isSaving = e
        },
        queryData: function () {
            this.$refs.datatable.refresh()
        },
        toggleStatus: function () {

        },
        editRecord: function () {

        },
        refreshRecord: function () {

        },
        deleteRecord: function () {

        },
        importExcel: function () {

        },
        exportExcel: function () {

        }
    },
    mounted: function () {

    }
}
</script>

<style lang="scss" scoped>
.footer {
    .pagination-block {
        margin-bottom: 15px !important;
    }

    .Polaris-ButtonGroup {
        float: right;
        clear: both;

        &:after {
            content: '';
            clear: both;
            display: block;
        }
    }
}
</style>
