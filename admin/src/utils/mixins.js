'use strict';
import { mapGetters} from "vuex";

export default {
    methods: {},
    computed: {
        ...mapGetters(['getApi', 'getRule'])
    }
}
