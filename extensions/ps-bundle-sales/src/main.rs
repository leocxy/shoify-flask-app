use serde::Serialize;

mod api;

use api::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let input: input::Input = serde_json::from_reader(std::io::BufReader::new(std::io::stdin()))?;
    let mut out = std::io::stdout();
    let mut serializer = serde_json::Serializer::new(&mut out);
    function(input)?.serialize(&mut serializer)?;
    Ok(())
}

fn default_result() -> Result<FunctionResult, Box<dyn std::error::Error>> {
    return Ok(FunctionResult {
        discounts: vec![],
        discount_application_strategy: DiscountApplicationStrategy::First,
    });
}

fn function(input: input::Input) -> Result<FunctionResult, Box<dyn std::error::Error>> {
    let config: input::Configuration = input.configuration();
    eprintln!("Config: {:#?}", &config);
    let cart_lines = input.cart.lines;
    // Check methods
    let methods = vec!["fixed".to_string(), "percentage".to_string()];
    let method = match methods.iter().find(|&s| s == &config.method) {
        Some(val) => Some(val),
        None => None
    };
    // Check Cart and methods
    if method == None || cart_lines.is_empty() {
        return default_result();
    }
    // process discount targets
    let mut targets = vec![];
    for line in cart_lines {
        eprintln!("Item: {:#?}", line);
        if line.quantity >= config.threshold {
            let item_price: f64 = line.cost.amount_per_quantity.unwrap().amount.unwrap().parse().unwrap();
            eprintln!("Qty: {:#?}, Price: {:#?}", line.quantity, &item_price);
            targets.push(Target::ProductVariant {
                id: line.merchandise.id.unwrap_or_default(),
                quantity: Some(line.quantity - 1),
            })
        }
    }

    if targets.is_empty() {
        return default_result();
    }

    Ok(FunctionResult {
        discounts: vec![Discount {
            message: Some("Hello World".to_string()),
            targets,
            value: Value::FixedAmount(FixedAmount {
                applies_to_each_item: Some(true),
                value: config.value,
            })
        }],
        discount_application_strategy: DiscountApplicationStrategy::First,
    })

}

#[cfg(test)]
mod tests {
    use super::*;

    fn input(configuration: Option<input::Configuration>) -> input::Input {
        let input = r#"
        {
          "cart": {
            "attribute": [{"key": "test", "value": "test-value"}],
            "cost": {
              "subtotalAmount": {
                "amount": "200.0"
              },
              "totalAmount": {
                "amount": "200.0"
              }
            },
            "buyerIdentity": null,
            "lines": [
              {
                "quantity": 5,
                "cost": {
                  "amountPerQuantity": {
                    "amount": "40.0"
                  },
                  "subtotalAmount": {
                    "amount": "200.0"
                  },
                  "totalAmount": {
                    "amount": "200.0"
                  }
                },
                "merchandise": {
                  "id": "gid://shopify/ProductVariant/31441228824630",
                  "sku": "31347",
                  "metafield": null
                }
              }
            ]
          },
          "discountNode": {
            "metafield": {
              "value": "{\"method\":\"fixed\",\"value\":20,\"threshold\":3}"
            }
          }
        }
        "#;
        let default_input: input::Input = serde_json::from_str(input).unwrap();
        // read meta value from raw text
        let value = match configuration.map(|x| serde_json::to_string(&x).unwrap()) {
            Some(val) => Some(val),
            None => default_input.discount_node.metafield.unwrap().value,
        };

        let discount_node = input::DiscountNode {
            metafield: Some(input::Metafield { value }),
        };

        input::Input {
            discount_node,
            ..default_input
        }
    }

    #[test]
    fn test_basic() {
        let input = input(None);
        let result = serde_json::json!(function(input).unwrap());
        let expected_json = r#"
            {
                "discounts": [{
                    "message": "Hello World",
                    "targets": [
                        {
                            "productVariant": {
                                "id": "gid://shopify/ProductVariant/31441228824630",
                                "quantity": 4
                            }
                        }
                    ],
                    "value": {"fixedAmount": {
                        "appliesToEachItem": true,
                        "value": 20.0
                    }}
                }],
                "discountApplicationStrategy": "FIRST"
            }
        "#;

        let expected_handle_result: serde_json::Value =
            serde_json::from_str(expected_json).unwrap();
        assert_eq!(
            result.to_string(),
            expected_handle_result.to_string()
        );
    }

    #[test]
    fn test_discount_with_none_method() {
        let input = input(Some(input::Configuration {
            method: "none".to_string(),
            value: 0.0,
            threshold: 0,
        }));
        let handle_result = serde_json::json!(function(input).unwrap());

        let expected_json = r#"
            {
                "discounts": [],
                "discountApplicationStrategy": "FIRST"
            }
        "#;

        let expected_handle_result: serde_json::Value =
            serde_json::from_str(expected_json).unwrap();
        assert_eq!(
            handle_result.to_string(),
            expected_handle_result.to_string()
        );
    }

    #[test]
    fn test_discount_with_not_meet_the_threshold() {
        let input = input(Some(input::Configuration {
            method: "fixed".to_string(),
            value: 15.0,
            threshold: 10,
        }));
        let handle_result = serde_json::json!(function(input).unwrap());

        let expected_json = r#"
            {
                "discounts": [],
                "discountApplicationStrategy": "FIRST"
            }
        "#;

        let expected_handle_result: serde_json::Value =
            serde_json::from_str(expected_json).unwrap();
        assert_eq!(
            handle_result.to_string(),
            expected_handle_result.to_string()
        );
    }

    #[test]
    fn test_discount_with_meet_the_threshold() {
        let input = input(Some(input::Configuration {
            method: "fixed".to_string(),
            value: 18.0,
            threshold: 5,
        }));
        let handle_result = serde_json::json!(function(input).unwrap());

        let expected_json = r#"
            {
                "discounts": [{
                    "message": "Hello World",
                    "targets": [
                        {
                            "productVariant": {
                                "id": "gid://shopify/ProductVariant/31441228824630",
                                "quantity": 4
                            }
                        }
                    ],
                    "value": {"fixedAmount": {
                        "appliesToEachItem": true,
                        "value": 18.0
                    }}
                }],
                "discountApplicationStrategy": "FIRST"
            }
        "#;

        let expected_handle_result: serde_json::Value =
            serde_json::from_str(expected_json).unwrap();
        assert_eq!(
            handle_result.to_string(),
            expected_handle_result.to_string()
        );
    }
}