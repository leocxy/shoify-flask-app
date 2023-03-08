import {useEffect, useState} from "react";
import {
    View,
    Heading,
    Text,
    BlockStack,
    Divider,
    InlineLayout,
    Image,
    SkeletonImage,
    Button,
    Banner,
    render,
    useTranslate,
    useCartLines,
    useAppMetafields,
    useDiscountCodes,
    useApplyCartLinesChange,
    useApplyDiscountCodeChange,
} from '@shopify/checkout-ui-extensions-react';
import isEmpty from 'lodash/isEmpty'

render('Checkout::Dynamic::Render', () => <App/>);

function App() {

    const items = useCartLines(),
        metaData = useAppMetafields(),
        applyCartLinesChange = useApplyCartLinesChange(),
        applyDiscountCodeChange = useApplyDiscountCodeChange(),
        translate = useTranslate(),
        discountCodes = useDiscountCodes();

    const [exist, setExist] = useState(false)
    const [qualify, setQualify] = useState(false)
    const [conf, setConfig] = useState({})
    const [error, setError] = useState(false)
    const [adding, setAdding] = useState(false)
    const [loading, setLoading] = useState(false)

    class GWPHelper {
        constructor() {
        }

        log = (m, k = 'Debug') => {
            console.log(`PS-GWP[${k}]:`, m)
        }

        toCent = (value) => parseInt((parseFloat(value) * 100).toFixed(1))

        toDollar = (value) => parseFloat((parseInt(value) * 0.01).toFixed(2))

        checkQualify = (method, items, pre_requirements, value) => {
            let fn = method === 1 ? 'checkQuantity' : 'checkThreshold'
            this[fn](items, pre_requirements, value)
        }

        getHashString = (pid, vid, secret_number) => {
            let number = parseInt('1' + pid.toString().slice(-10))
            number += parseInt(secret_number.toString() + vid.toString().slice(-5))
            return '0x' + (Math.floor(number / secret_number)).toString(16)
        }

        logStatus = () => {
            this.log(`Qualify: ${qualify}`)
            this.log(`Exist: ${exist}`)
        }

        showLoading = () => {
            this.log('Loading')
            return (<View/>)
        }

        showEmpty = () => {
            this.logStatus()
            return (<View/>)
        }

        checkThreshold = (items, pre_requirements, value) => {
            let amount = 0
            items.forEach(item => {
                let pid = parseInt(item.merchandise.product.id.split('/').pop())
                if (pre_requirements.find(o => o === pid)) {
                    amount += this.toCent(item.cost.totalAmount.amount)
                }
            })
            setQualify(value <= amount)
        }

        checkQuantity = (items, pre_requirements, value) => {
            let quantity = 0
            items.forEach(item => {
                let pid = parseInt(item.merchandise.product.id.split('/').pop())
                if (pre_requirements.find(o => o === pid)) {
                    quantity += item.quantity
                }
            })
            setQualify(value <= quantity)
        }

        addItem = async () => {
            setAdding(true)
            // Add Item
            const result = await applyCartLinesChange({
                type: 'addCartLine',
                merchandiseId: `gid://shopify/ProductVariant/${conf.target.vid}`,
                quantity: 1,
                attributes: [{
                    key: conf.attr_key,
                    value: helper.getHashString(conf.target.pid, conf.target.vid, conf.secret_number)
                }]
            })
            // Add Discount Code
            const code_result = await applyDiscountCodeChange({
                type: 'addDiscountCode',
                code: conf.code
            })
            if (result.type === 'error') {
                setError(true)
                this.log(result, 'AddItemError')
            }
            if (!error && code_result.type === 'error') {
                setError(true)
                this.log(code_result, 'AddDiscountCodeError')
            }
            setExist(true)
            setAdding(false)
        }
    }

    let helper = new GWPHelper()

    // Loading Effect
    useEffect(() => {
        setLoading(true)
        new Promise((resolve, reject) => {
            let configs = metaData.find(o => o?.target?.type === 'shop')
            if (!configs) return reject('Shop Meta is empty!')
            configs = JSON.parse(configs.metafield.value)
            resolve(configs)
        }).then((result) => {
            helper.log(result, 'Config')
            setConfig(result)
        }).catch((err) => {
            helper.log(err, 'Error')
        }).finally(() => setLoading(false))
    }, [metaData])

    // CartItem
    useEffect(() => {
        setLoading(true)
        if (isEmpty(conf) || isEmpty(items)) return
        if (conf?.status === true) {
            helper.checkQualify(conf.method, items, conf.pre_requirements, conf.value)
            // Qualify -> Check GWP, Check Discount Code
            if (!qualify) {
                const clearData = async (items, target, attr_key, code) => {
                    let item = items.find(item => {
                        let pid = parseInt(item.merchandise.product.id.split('/').pop())
                        if (pid !== target.pid) return false
                        if (item.cost.totalAmount === 0) return true
                        let attr = item.attributes.find(attr => attr.key === attr_key)
                        if (!attr) return false
                        return true
                    })
                    let found_code = discountCodes.find(o => o.code === code)
                    setLoading(true)
                    let result;
                    if (found_code) {
                        result = await applyDiscountCodeChange({
                            type: 'removeDiscountCode',
                            code: conf.code
                        })
                        if (!error && result.type === 'error') {
                            setError(true)
                            this.log(result, 'RemoveCodeError')
                        }
                    }
                    if (item && (conf.force_remove || item.cost.totalAmount === 0)) {
                        result = await applyCartLinesChange({
                            type: "removeCartLine",
                            id: item.id,
                            quantity: item.quantity
                        })
                        if (!error && result.type === 'error') {
                            setError(true)
                            this.log(result, 'RemoveItemError')
                        }
                    }
                    setLoading(false)
                }
                clearData(items, conf.target, conf.attr_key, conf.code).catch((err) => helper.log(err))
            }
        }
        setLoading(false)
    }, [items, conf, discountCodes])

    // Loading
    if (loading) return helper.showLoading()

    if (qualify && !exist) {
        helper.logStatus()
        return (
            <BlockStack spacing="loose">
                <Divider/>
                <Heading level={3}>{translate('sub-title')}</Heading>
                <BlockStack spacing="loose">
                    <InlineLayout
                        spacing="base"
                        columns={[64, 'fill', 'auto']}
                        blockAlignment="center">
                        <BlockStack spacing="none">
                            {conf.target.image ? <Image source={conf.target.image} loading="lazy"/> :
                                <SkeletonImage aspectRatio={1}/>}
                        </BlockStack>
                        <BlockStack spacing="none">
                            <Text>{conf.target.title}</Text>
                        </BlockStack>
                        <BlockStack spacing="none">
                            <Button kind="primary" loading={adding} onPress={helper.addItem}>
                                {translate('add')}
                            </Button>
                        </BlockStack>
                    </InlineLayout>
                </BlockStack>
                {error && (
                    <Banner status='critical'>
                        There was an issue adding this product. Please try again.
                    </Banner>
                )}
            </BlockStack>
        )
    }

    return helper.showEmpty()
}

