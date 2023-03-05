use super::*;
use shopify_function::{run_function_with_input, Result};

#[test]
fn test_with_no_configuration() -> Result<()> {
    let result = run_function_with_input(
        function,
        r#"
            {
                "cart": {
                    "lines": [
                        {
                            "cost": {
                                "totalAmount": {
                                    "amount": "0"
                                }
                            },
                            "merchandise": {
                                "__typename": "ProductVariant",
                                "id": "gid://shopify/ProductVariant/0",
                                "product": { "id": "gid://shopify/Product/10" }
                            },
                            "quantity": 5,
                            "attribute": null,
                            "id": "gid://shopify/CartLine/0"
                        },
                        {
                            "cost": {
                                "totalAmount": {
                                    "amount": "0"
                                }
                            },
                            "merchandise": {
                                "__typename": "ProductVariant",
                                "id": "gid://shopify/ProductVariant/1",
                                "product": { "id": "gid://shopify/Product/11" }
                            },
                            "quantity": 1,
                            "attribute": null,
                            "id": "gid://shopify/CartLine/1"
                        }
                    ]
                },
                "discountNode": {
                    "metafield": null
                }
            }
        "#,
    )?;
    let expected = crate::output::FunctionResult {
        discounts: vec![],
        discount_application_strategy: crate::output::DiscountApplicationStrategy::FIRST,
    };
    assert_eq!(result, expected);
    Ok(())
}

#[test]
fn test_with_correct_properties() -> Result<()> {
    let result = run_function_with_input(
        function,
        r#"
            {
                "cart":
                {
                    "lines":
                    [
                        {
                            "id": "gid://shopify/CartLine/0",
                            "quantity": 1,
                            "attribute":
                            {
                                "key": "_gwp_item",
                                "value": "0x37a16145"
                            },
                            "cost":
                            {
                                "totalAmount":
                                {
                                    "amount": "20.0"
                                }
                            },
                            "merchandise":
                            {
                                "__typename": "ProductVariant",
                                "id": "gid://shopify/ProductVariant/44490537435457",
                                "product":
                                {
                                    "id": "gid://shopify/Product/8121198641473"
                                }
                            }
                        }
                    ]
                },
                "discountNode":
                {
                    "metafield":
                    {
                        "value": "{\"status\":true,\"method\":1,\"value\":4,\"message\":\"Gift with purchase\",\"secret_number\":12,\"pid\":8121198641473,\"attr_key\":\"_gwp_item\"}"
                    }
                }
            }
        "#,
    )?;
    let expected = crate::output::FunctionResult {
        discounts: vec![crate::output::Discount {
            message: Some("Gift with purchase".to_string()),
            targets: vec![crate::output::Target {
                product_variant: Some(crate::output::ProductVariantTarget {
                    id: "gid://shopify/ProductVariant/44490537435457".to_string(),
                    quantity: Some(1),
                }),
            }],
            value: crate::output::Value {
                percentage: Some(crate::output::Percentage {
                    value: "100".to_string(),
                }),
                fixed_amount: None,
            },
        }],
        discount_application_strategy: crate::output::DiscountApplicationStrategy::FIRST,
    };

    assert_eq!(result, expected);
    Ok(())
}

#[test]
fn test_with_incorrect_properties_1() -> Result<()> {
    let result = run_function_with_input(
        function,
        r#"
            {
                "cart":
                {
                    "lines":
                    [
                        {
                            "id": "gid://shopify/CartLine/0",
                            "quantity": 1,
                            "attribute":
                            {
                                "key": "_gwp_item",
                                "value": "0x37a16145"
                            },
                            "cost":
                            {
                                "totalAmount":
                                {
                                    "amount": "30.0"
                                }
                            },
                            "merchandise":
                            {
                                "__typename": "ProductVariant",
                                "id": "gid://shopify/ProductVariant/44490537435477",
                                "product":
                                {
                                    "id": "gid://shopify/Product/8121198641487"
                                }
                            }
                        }
                    ]
                },
                "discountNode":
                {
                    "metafield":
                    {
                        "value": "{\"status\":true,\"method\":1,\"value\":4,\"message\":\"Gift with purchase\",\"secret_number\":12,\"pid\":8121198641473,\"attr_key\":\"_gwp_item\"}"
                    }
                }
            }
        "#,
    )?;
    let expected = crate::output::FunctionResult {
        discounts: vec![],
        discount_application_strategy: crate::output::DiscountApplicationStrategy::FIRST,
    };
    assert_eq!(result, expected);
    Ok(())
}

#[test]
fn test_with_incorrect_properties_2() -> Result<()> {
    let result = run_function_with_input(
        function,
        r#"
            {
                "cart":
                {
                    "lines":
                    [
                        {
                            "id": "gid://shopify/CartLine/0",
                            "quantity": 1,
                            "attribute":
                            {
                                "key": "_gwp_item",
                                "value": "0x37a16145"
                            },
                            "cost":
                            {
                                "totalAmount":
                                {
                                    "amount": "20.0"
                                }
                            },
                            "merchandise":
                            {
                                "__typename": "ProductVariant",
                                "id": "gid://shopify/ProductVariant/44490537435457",
                                "product":
                                {
                                    "id": "gid://shopify/Product/8121198641473"
                                }
                            }
                        }
                    ]
                },
                "discountNode":
                {
                    "metafield":
                    {
                        "value": "{\"status\":true,\"method\":1,\"value\":4,\"message\":\"Gift with purchase\",\"secret_number\":32,\"pid\":8121198641473,\"attr_key\":\"_gwp_item\"}"
                    }
                }
            }
        "#,
    )?;
    let expected = crate::output::FunctionResult {
        discounts: vec![],
        discount_application_strategy: crate::output::DiscountApplicationStrategy::FIRST,
    };
    assert_eq!(result, expected);
    Ok(())
}