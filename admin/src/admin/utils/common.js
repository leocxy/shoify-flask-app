import {errorCB} from "@/store/actions";

export default {
    methods: {
        priceChange: function (e, i) {
            this.groups[i]['unit_price'] = parseFloat(e) * 100
        },
        formatPrice: function (e) {
            return (parseFloat(e) * 0.01).toFixed(2)
        },
        errorHandle: function (err) {
            this.isSaving = false
            let message = err?.data?.message || 'An error occurred!'
            this.$pToast.open({message, error: true, duration: 5000})
            errorCB(err)
        },
    }
}
