import {ValidationObserver, ValidationProvider} from "vee-validate"

export default {
    props: ['id'],
    components: {ValidationObserver, ValidationProvider},
    data: () => ({
        record_id: null,
    }),
}
