<template>
    <PCard sectioned title="Meta Definition">
        <VueTable
            :data="table_data"
            :fields="table_fields"
            data-path="data.data"
            pagination-path="data"
            :per-page="10"
            :http-options="tableHeaders"
            ref="datatable"
            :css="tableCss">
            <template slot="status" slot-scope="{rowData}">
                <PIcon v-if="rowData.status === 1" color="success" source="CircleTickOutlineMinor"/>
                <PIcon v-else color="critical" source="CircleCancelMinor"/>
            </template>
        </VueTable>
        <PButtonGroup slot="footer">
            <PButton v-if="!status" primary @click="createDefinition" :loading="isSaving">Create Definition</PButton>
            <PButton v-else destructive @click="deleteDefinition" :loading="isSaving">Delete Definition</PButton>
        </PButtonGroup>
    </PCard>
</template>

<script>
import common from "../../../utils/common"
import table from "../../../utils/table"
import {getApi} from "../../../store/getters"
import {errorCB} from "../../../store/actions"

export default {
    name: "MetaDefinition",
    mixins: [common, table],
    props: ['isSaving'],
    data: () => ({
        table_fields: [{
            name: 'namespace',
            title: 'Namespace',
            titleClass: 'center aligned',
            dataClass: 'center aligned'
        }, {
            name: 'key',
            title: 'Key',
            titleClass: 'center aligned',
            dataClass: 'center aligned'
        }, {
            name: 'owner_type',
            title: 'Owner',
            titleClass: 'center aligned',
            dataClass: 'center aligned'
        }, {
            name: '__slot:status',
            title: 'Status',
            titleClass: 'center aligned',
            dataClass: 'center aligned'
        }],
        table_data: [],
        status: false,
        url_suffix: 'meta_definitions'
    }),
    methods: {
        processData: function (data) {
            this.table_data = data.data
            this.status = this.table_data.find(v => v.status === 0) === undefined
        },
        getMetaDefinitionData: function () {
            this.$http.get(getApi('bundles', this.url_suffix)).then(({data}) => {
                this.processData(data)
            }).catch((err) => {
                let message = err?.data?.message || 'An error occurred!'
                this.$pToast.open({message, error: true, duration: 5000})
                errorCB(err)
            })
        },
        createDefinition: function () {
            this.$emit('change', true)
            this.$http.post(getApi('bundles', this.url_suffix)).then(({data}) => {
                this.processData(data)
                this.$pToast.open({message: 'Meta Definitions have been created!'})
                this.$emit('change', false)
            }).catch((err) => {
                this.$emit('change', false)
                let message = err?.data?.message || 'An error occurred!'
                this.$pToast.open({message, error: true, duration: 5000})
                errorCB(err)
            })
        },
        deleteDefinition: function () {
            this.$emit('change', true)
            this.$confirm('Delete the MetaDefinitions will delete all associated metafields!').then(() => {
                this.$http.delete(getApi('bundles', this.url_suffix)).then(({data}) => {
                    this.$emit('change', false)
                    this.processData(data)
                    this.$pToast.open({message: 'Meta Definitions have been created!'})
                }).catch((err) => {
                    this.$emit('change', false)
                    let message = err?.data?.message || 'An error occurred!'
                    this.$pToast.open({message, error: true, duration: 5000})
                    errorCB(err)
                })
            }).catch(() => {
                this.$emit('change', false)
                this.$pToast.open({message: "Action cancelled!"})
            })
        }
    },
    mounted: function () {
        this.getMetaDefinitionData()
    }
}
</script>
