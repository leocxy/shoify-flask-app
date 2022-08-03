import {getApi} from "@/store/getters";
import VueTable from "vuetable-2/src/components/Vuetable"
import VuetablePagination from "vuetable-2/src/components/VuetablePagination"

export default {
    components: {VueTable, VuetablePagination},
    computed: {
        tableHeaders: function () {
            return {headers: {'Authorization': this.$http.defaults.headers?.common?.Authorization || ''}}
        },
        tableCss: function () {
            return {
                tableClass: 'ui selectable celled stackable attached table',
                loadingClass: 'loading',
                ascendingIcon: 'blue chevron up icon',
                descendingIcon: 'blue chevron down icon',
                ascendingClass: 'sorted-asc',
                descendingClass: 'sorted-desc',
                sortableIcon: '',
                detailRowClass: 'vuetable-detail-row',
                handleIcon: 'grey sidebar icon',
                tableBodyClass: 'vuetable-semantic-no-top vuetable-fixed-layout',
                tableHeaderClass: 'vuetable-fixed-layout'
            }
        }
    },
    methods: {
        getApi: getApi,
        onChangePage: function (page) {
            this.$refs.datatable.changePage(page)
        },
        onPaginationData: function (data) {
            this.$refs.pagination.setPaginationData(data)
        },
    }
}
