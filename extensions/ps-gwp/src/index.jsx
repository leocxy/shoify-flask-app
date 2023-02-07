import {useState} from "react";
import {
    View,
    Heading,
    Text,
    InlineLayout,
    Image,
    SkeletonImage,
    Button,
    render,
    useTranslate,
    useCartLines,
    useAppMetafields,
    useApplyCartLinesChange,
} from '@shopify/checkout-ui-extensions-react';
import isEmpty from 'lodash/isEmpty'

const emptyResponse = function () {
    return (<View/>)
}

class GWPHelper {
    constructor(values, items, lineItemsChange) {
        this.items = items
        this.enable = values?.enable === undefined ? false : values.enable
        this.method = values?.method === undefined ? 1 : values.method
        this.value = values?.value === undefined ? 999999 : values.value
        this.target = values?.target
        this.pre_requirements = values?.pre_requirements === undefined ? [] : values.pre_requirements
        this.secret_number = values?.secret_number === undefined ? 1 : values.secret_number
        this.key = values?.attr_key === undefined ? '_gwp_hash_str' : values.attr_key
        // dynamic variable
        this.qualified = false
        this.existed = false
        // extension API
        this.lineItemsChange = lineItemsChange
    }

    log = (msg) => {
        console.log('PS-GWP:', msg)
    }

    toCent = (value) => parseInt((parseFloat(value) * 100).toFixed(1))

    toDollar = (value) => parseFloat((parseInt(value) * 0.01).toFixed(2))

    checkQualify() {
        this.method === 1 ? this._checkQuantity() : this._checkThreshold()
    }

    clearExtraFreeGift() {
        if (!this.qualified) return
        let item = this.items.find(item => {
            let pid = parseInt(item.merchandise.product.id.split('/').pop())
            return (pid === this.target.pid && item.attributes.find(attr => attr.key === this.key))
        })
        if (!item) return
        this.log(`Found!`)
        this.log(item)
        this.existed = true
        // Check Quantity
        if (item.quantity !== 1) {
            this.lineItemsChange({
                type: 'updateCartLine',
                id: item.id,
                quantity: 1
            })
        }
    }

    getHashString() {
        let number = parseInt('1' + this.target.pid.toString().slice(-10))
        number += parseInt(this.secret_number.toString() + this.target.vid.toString().slice(-5))
        return '0x' + (Math.floor(number / this.secret_number)).toString(16)
    }

    _checkThreshold() {
        let amount = 0
        this.items.forEach(item => {
            let pid = parseInt(item.merchandise.product.id.split('/').pop())
            if (this.pre_requirements.find(o => o.pid === pid)) {
                amount += this.toCent(item.cost.totalAmount.amount)
            }
        })
        this.qualified = this.toCent(this.value) <= amount
    }

    _checkQuantity() {
        let quantity = 0
        this.items.forEach(item => {
            let pid = parseInt(item.merchandise.product.id.split('/').pop())
            if (this.pre_requirements.find(o => o.pid === pid)) {
                quantity += item.quantity
            }
        })
        this.qualified = this.value <= quantity
    }
}


function App() {
    let [loading, setLoading] = useState(false)
    const items = useCartLines(),
        metaData = useAppMetafields(),
        lineItemsChange = useApplyCartLinesChange(),
        translate = useTranslate();

    // Get Meta Data
    let configs = metaData.find(o => o?.target?.type === 'shop')

    // Check Cart Line items and Meta
    if (isEmpty(items) || !configs) return emptyResponse()

    // Parse JSON String
    try {
        configs = JSON.parse(configs.metafield.value)
    } catch (e) {
        console.error('PS-GWP Error:', e)
        return emptyResponse()
    }

    // Check Status
    if (!configs.enable) return emptyResponse()

    let helper = new GWPHelper(configs, items, lineItemsChange)
    helper.log(configs)

    helper.checkQualify()

    helper.clearExtraFreeGift()

    const addItem = () => {
        setLoading(true)
        lineItemsChange({
            type: 'addCartLine',
            merchandiseId: `gid://shopify/ProductVariant/${helper.target.vid}`,
            quantity: 1,
            attributes: [{
                key: helper.key,
                value: helper.getHashString()
            }]
        }).then(() => setLoading(false))
    }

    if (helper.qualified && !helper.existed) {
        let image = helper.target.image ? <Image source={helper.target.image} loading="lazy"/> :
            <SkeletonImage blockSize='fill'/>

        return (
            <InlineLayout columns={[100, 'fill', '25%']} border="base">
                <View border="none" padding="base">
                    {image}
                </View>
                <View border="none" padding="base">
                    <Heading level="3" inlineAlignment="start">
                        {helper.target.title}
                    </Heading>
                    <Text size="small">Description</Text>
                </View>
                <View border="none" padding="base" blockAlignment="center">
                    <Button kind="primary" onPress={addItem} loading={loading}>
                        {translate('add')}
                    </Button>
                </View>
            </InlineLayout>
        )
    } else {
        return emptyResponse()
    }

}

render('Checkout::CartLines::RenderAfter', () => <App/>);