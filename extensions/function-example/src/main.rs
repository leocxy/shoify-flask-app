use shopify_function::prelude::*;
use shopify_function::Result;

use serde::{Deserialize, Serialize};

generate_types!(
    query_path = "./input.graphql",
    schema_path = "./schema.graphql"
);

#[derive(Serialize, Deserialize, PartialEq, Debug)]
#[serde(untagged)]
enum ConfigValue {
    Float(f64),
    Int(u64),
    None,
}

impl Default for ConfigValue {
    fn default() -> Self {
        ConfigValue::Int(0)
    }
}

// #[serde(rename_all(deserialize = "camelCase"))]
#[derive(Serialize, Deserialize, Default, PartialEq, Debug)]
struct Config {
    pub method: String,
    pub value: ConfigValue,
    pub threshold: i64,
}


#[shopify_function]
fn function(input: input::ResponseData) -> Result<output::FunctionResult> {
    let no_discount = output::FunctionResult {
        discounts: vec![],
        discount_application_strategy: output::DiscountApplicationStrategy::FIRST,
    };

    let config = input
        .discount_node
        .metafield
        .as_ref()
        .map(|meta| serde_json::from_str::<Config>(meta.value.as_str()))
        .transpose()?
        .unwrap_or_default();

    // debug message
    eprintln!("Config: {:#?}", &config);

    let value: String = match config.value {
        ConfigValue::Float(value) => value.to_string(),
        ConfigValue::Int(value) => value.to_string(),
        _ => "0".to_string(),
    };

    // check configs
    let cart_lines = input.cart.lines;
    if cart_lines.is_empty() || value == "0".to_string() {
        return Ok(no_discount);
    }

    // qualify -> item quantity
    let mut quantity = 0;
    for line in &cart_lines {
        quantity += line.quantity
    }

    if quantity < config.threshold {
        return Ok(no_discount);
    }

    // get targets
    let targets = cart_lines
        .iter()
        .filter_map(|line| match &line.merchandise {
            input::InputCartLinesMerchandise::ProductVariant(variant) => Some(variant),
            input::InputCartLinesMerchandise::CustomProduct => None,
        })
        .map(|variant| output::Target {
            product_variant: Some(output::ProductVariantTarget {
                id: variant.id.to_string(),
                quantity: None,
            }),
            order_subtotal: None,
        })
        .collect::<Vec<output::Target>>();

    // apply discount value
    let value = if config.method == "percentage" {
        output::Value {
            percentage: Some(output::Percentage {
                value,
            }),
            fixed_amount: None,
        }
    } else {
        output::Value {
            percentage: None,
            fixed_amount: Some(output::FixedAmount {
                amount: value,
            }),
        }
    };

    eprintln!("Targets: {:#?}\nValue: {:#?}", &targets, &value);

    Ok(output::FunctionResult {
        discount_application_strategy: output::DiscountApplicationStrategy::FIRST,
        discounts: vec![output::Discount {
            conditions: None,
            message: Some("PS Demo".to_string()),
            targets,
            value,
        }],
    })
}

#[cfg(test)]
mod tests;

// fn function_old(input: input::Input) -> Result<FunctionResult, Box<dyn std::error::Error>> {
//     let config: input::Configuration = input.configuration();
//     eprintln!("Config: {:#?}", &config);
//     let cart_lines = input.cart.lines;
//     // Check methods
//     let methods = vec!["fixed".to_string(), "percentage".to_string()];
//     let method = match methods.iter().find(|&s| s == &config.method) {
//         Some(val) => Some(val),
//         None => None
//     };
//     // Check Cart and methods
//     if method == None || cart_lines.is_empty() {
//         return default_result();
//     }
//     // process discount targets
//     let mut targets = vec![];
//     for line in cart_lines {
//         eprintln!("Item: {:#?}", line);
//         if line.quantity >= config.threshold {
//             let item_price: f64 = line.cost.amount_per_quantity.unwrap().amount.unwrap().parse().unwrap();
//             eprintln!("Qty: {:#?}, Price: {:#?}", line.quantity, &item_price);
//             targets.push(Target::ProductVariant {
//                 id: line.merchandise.id.unwrap_or_default(),
//                 quantity: Some(line.quantity - 1),
//             })
//         }
//     }
//
//     if targets.is_empty() {
//         return default_result();
//     }
//
//     let value = match config.method.as_str() {
//         "percentage" => {
//             Value::Percentage(Percentage {
//                 value: config.value
//             })
//         }
//         _ => {
//             Value::FixedAmount(FixedAmount {
//                 amount: config.value
//             })
//         }
//     };
//
//     Ok(FunctionResult {
//         discounts: vec![Discount {
//             message: Some("Hello World".to_string()),
//             targets,
//             value,
//         }],
//         discount_application_strategy: DiscountApplicationStrategy::First,
//     })
// }