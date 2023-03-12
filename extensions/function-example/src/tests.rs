use super::*;
use shopify_function::{run_function_with_input, Result};

#[test]
fn test_result_with_no_configuration() -> Result<()> {
    let result = run_function_with_input(
        function,
        r#"
            {
                "cart":
                {
                    "lines":
                    [
                        {
                            "quantity": 1,
                            "cost": {
                                "amountPerQuantity": {
                                    "amount": "57.0"
                                },
                                "compareAtAmountPerQuantity": null,
                                "subtotalAmount": {
                                    "amount": "342.0"
                                }
                            },
                            "merchandise": {
                                "__typename": "ProductVariant",
                                "id": "gid://shopify/ProductVariant/44490537894209",
                                "sku": "",
                                "metafield": null
                            }
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
fn test_percentage_1() -> Result<()> {
    let result = run_function_with_input(
        function,
        r#"
            {
                "cart":
                {
                    "lines":
                    [
                        {
                            "quantity": 5,
                            "cost": {
                                "amountPerQuantity": {
                                    "amount": "57.0"
                                },
                                "compareAtAmountPerQuantity": null,
                                "subtotalAmount": {
                                    "amount": "342.0"
                                }
                            },
                            "merchandise": {
                                "__typename": "ProductVariant",
                                "id": "gid://shopify/ProductVariant/44490537894209",
                                "sku": "",
                                "metafield": null
                            }
                        }
                    ]
                },
                "discountNode": {
                    "metafield": {
                        "value": "{\"method\":\"percentage\",\"value\":15.0,\"threshold\":5}"
                    }
                }
            }
        "#,
    )?;

    let expected = crate::output::FunctionResult {
        discounts: vec![crate::output::Discount {
            message: Some("PS Demo".to_string()),
            conditions: None,
            targets: vec![crate::output::Target {
                product_variant: Some(crate::output::ProductVariantTarget {
                    quantity: None,
                    id: "gid://shopify/ProductVariant/44490537894209".to_string(),
                }),
                order_subtotal: None,
            }],
            value: crate::output::Value {
                fixed_amount: None,
                percentage: Some(crate::output::Percentage {
                    value: "15".to_string()
                }),
            },
        }],
        discount_application_strategy: crate::output::DiscountApplicationStrategy::FIRST,
    };

    assert_eq!(result, expected);
    Ok(())
}

#[test]
fn test_percentage_2() -> Result<()> {
    let result = run_function_with_input(
        function,
        r#"
            {
                "cart":
                {
                    "lines":
                    [
                        {
                            "quantity": 3,
                            "cost": {
                                "amountPerQuantity": {
                                    "amount": "57.0"
                                },
                                "compareAtAmountPerQuantity": null,
                                "subtotalAmount": {
                                    "amount": "342.0"
                                }
                            },
                            "merchandise": {
                                "__typename": "ProductVariant",
                                "id": "gid://shopify/ProductVariant/44490537894209",
                                "sku": "",
                                "metafield": null
                            }
                        },
                        {
                            "quantity": 3,
                            "cost": {
                                "amountPerQuantity": {
                                    "amount": "57.0"
                                },
                                "compareAtAmountPerQuantity": null,
                                "subtotalAmount": {
                                    "amount": "342.0"
                                }
                            },
                            "merchandise": {
                                "__typename": "ProductVariant",
                                "id": "gid://shopify/ProductVariant/44490537894210",
                                "sku": "",
                                "metafield": null
                            }
                        }
                    ]
                },
                "discountNode": {
                    "metafield": {
                        "value": "{\"method\":\"percentage\",\"value\":15.0,\"threshold\":5}"
                    }
                }
            }
        "#,
    )?;

    let expected = crate::output::FunctionResult {
        discounts: vec![crate::output::Discount {
            message: Some("PS Demo".to_string()),
            conditions: None,
            targets: vec![crate::output::Target {
                product_variant: Some(crate::output::ProductVariantTarget {
                    quantity: None,
                    id: "gid://shopify/ProductVariant/44490537894209".to_string(),
                }),
                order_subtotal: None,
            }, crate::output::Target {
                product_variant: Some(crate::output::ProductVariantTarget {
                    quantity: None,
                    id: "gid://shopify/ProductVariant/44490537894210".to_string(),
                }),
                order_subtotal: None,
            }],
            value: crate::output::Value {
                fixed_amount: None,
                percentage: Some(crate::output::Percentage {
                    value: "15".to_string()
                }),
            },
        }],
        discount_application_strategy: crate::output::DiscountApplicationStrategy::FIRST,
    };

    assert_eq!(result, expected);
    Ok(())
}

#[test]
fn test_percentage_3() -> Result<()> {
    let result = run_function_with_input(
        function,
        r#"
            {
                "cart":
                {
                    "lines":
                    [
                        {
                            "quantity": 5,
                            "cost": {
                                "amountPerQuantity": {
                                    "amount": "57.0"
                                },
                                "compareAtAmountPerQuantity": null,
                                "subtotalAmount": {
                                    "amount": "342.0"
                                }
                            },
                            "merchandise": {
                                "__typename": "ProductVariant",
                                "id": "gid://shopify/ProductVariant/44490537894209",
                                "sku": "",
                                "metafield": null
                            }
                        }
                    ]
                },
                "discountNode": {
                    "metafield": {
                        "value": "{\"method\":\"percentage\",\"value\":15.55,\"threshold\":5}"
                    }
                }
            }
        "#,
    )?;

    let expected = crate::output::FunctionResult {
        discounts: vec![crate::output::Discount {
            message: Some("PS Demo".to_string()),
            conditions: None,
            targets: vec![crate::output::Target {
                product_variant: Some(crate::output::ProductVariantTarget {
                    quantity: None,
                    id: "gid://shopify/ProductVariant/44490537894209".to_string(),
                }),
                order_subtotal: None,
            }],
            value: crate::output::Value {
                fixed_amount: None,
                percentage: Some(crate::output::Percentage {
                    value: "15.55".to_string()
                }),
            },
        }],
        discount_application_strategy: crate::output::DiscountApplicationStrategy::FIRST,
    };

    assert_eq!(result, expected);
    Ok(())
}

#[test]
fn test_percentage_4() -> Result<()> {
    let result = run_function_with_input(
        function,
        r#"
            {
                "cart":
                {
                    "lines":
                    [
                        {
                            "quantity": 3,
                            "cost": {
                                "amountPerQuantity": {
                                    "amount": "57.0"
                                },
                                "compareAtAmountPerQuantity": null,
                                "subtotalAmount": {
                                    "amount": "342.0"
                                }
                            },
                            "merchandise": {
                                "__typename": "ProductVariant",
                                "id": "gid://shopify/ProductVariant/44490537894209",
                                "sku": "",
                                "metafield": null
                            }
                        },
                        {
                            "quantity": 3,
                            "cost": {
                                "amountPerQuantity": {
                                    "amount": "57.0"
                                },
                                "compareAtAmountPerQuantity": null,
                                "subtotalAmount": {
                                    "amount": "342.0"
                                }
                            },
                            "merchandise": {
                                "__typename": "ProductVariant",
                                "id": "gid://shopify/ProductVariant/44490537894210",
                                "sku": "",
                                "metafield": null
                            }
                        }
                    ]
                },
                "discountNode": {
                    "metafield": {
                        "value": "{\"method\":\"percentage\",\"value\":13.34,\"threshold\":5}"
                    }
                }
            }
        "#,
    )?;

    let expected = crate::output::FunctionResult {
        discounts: vec![crate::output::Discount {
            message: Some("PS Demo".to_string()),
            conditions: None,
            targets: vec![crate::output::Target {
                product_variant: Some(crate::output::ProductVariantTarget {
                    quantity: None,
                    id: "gid://shopify/ProductVariant/44490537894209".to_string(),
                }),
                order_subtotal: None,
            }, crate::output::Target {
                product_variant: Some(crate::output::ProductVariantTarget {
                    quantity: None,
                    id: "gid://shopify/ProductVariant/44490537894210".to_string(),
                }),
                order_subtotal: None,
            }],
            value: crate::output::Value {
                fixed_amount: None,
                percentage: Some(crate::output::Percentage {
                    value: "13.34".to_string()
                }),
            },
        }],
        discount_application_strategy: crate::output::DiscountApplicationStrategy::FIRST,
    };

    assert_eq!(result, expected);
    Ok(())
}

// Fixed Amount

// #[test]
// fn test_leo() -> Result<()> {
//     let json_str = "{\"method\":\"percentage\",\"value\":15,\"threshold\":5}";
//     let json_str = serde_json::from_str::<crate::Config>(json_str);
//     eprintln!("{:#?}", json_str);
//     Ok(())
// }
//
// #[test]
// fn test_leo_2() -> Result<()> {
//     let json_str = "null";
//     let json_str = serde_json::from_str::<crate::Config>(json_str);
//     eprintln!("{:#?}", json_str.unwrap_or_default());
//     Ok(())
// }