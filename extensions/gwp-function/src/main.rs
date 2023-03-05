use shopify_function::prelude::*;
use shopify_function::Result;
use serde::{Serialize, Deserialize};

// Something like define the struct/type, you don't need to create the struct manually anymore
generate_types!(
    query_path = "./input.graphql",
    schema_path = "./schema.graphql"
);

#[derive(Serialize, Deserialize, Default, PartialEq, Debug)]
struct Config {
    pub status: bool,
    pub method: i64,
    pub value: i64,
    pub message: String,
    pub secret_number: i64,
    pub pid: i64,
    pub attr_key: String,
}

pub fn calculate_hash_string(secret_number: i64, pid: i64, vid: i64) -> String {
    let pid = pid.to_string();
    let len_check: usize = 10;
    let num1 = "1".to_string() + if pid.len() > len_check {
        &pid[pid.len() - 10..]
    } else {
        &pid[..]
    };
    let num1: i64 = num1.parse::<i64>().unwrap();
    let vid = vid.to_string();
    let len_check: usize = 5;
    let num2 = secret_number.to_string().as_str().to_owned() + if vid.len() > len_check {
        &vid[vid.len() - 5..]
    } else {
        &vid
    };
    let num2: i64 = num2.parse::<i64>().unwrap();
    let hash_str = format!("0x{:x}", (num1 + num2) / secret_number);
    eprintln!("PID: {:?}, VID: {:?}, Hash String: {:#?}", &pid, &vid, &hash_str);
    return hash_str;
}

#[shopify_function]
fn function(input: input::ResponseData) -> Result<output::FunctionResult> {
    let no_discount = output::FunctionResult {
        discounts: vec![],
        discount_application_strategy: output::DiscountApplicationStrategy::FIRST,
    };

    // Read configs from DiscountNode
    let config: Config = input
        .discount_node
        .metafield
        .as_ref()
        .map(|m| serde_json::from_str::<Config>(m.value.as_str()))
        .transpose()?
        .unwrap_or_default();

    // debug message
    eprintln!("Config: {:#?}", &config);

    // check configs
    if config.status == false || config.secret_number <= 0 || config.pid == 0 || config.value == 0 {
        return Ok(no_discount);
    }

    let cart_lines = input.cart.lines;
    if cart_lines.is_empty() {
        return Ok(no_discount);
    }

    // find the gift with purchase item
    let target = cart_lines
        .iter()
        .filter(|line| line.attribute.is_some())
        .filter_map(|line| {
            let hash_str = line.attribute.as_ref().unwrap().value.as_ref().unwrap();
            let variant = match &line.merchandise {
                input::InputCartLinesMerchandise::ProductVariant(variant) => Some(variant),
                input::InputCartLinesMerchandise::CustomProduct => None,
            };
            let mut rs = false;
            if variant.is_some() {
                let vid: &str = &variant.unwrap().id.split("/").collect::<Vec<&str>>().pop().unwrap();
                let pid: &str = &variant.unwrap().product.id.split("/").collect::<Vec<&str>>().pop().unwrap();
                let vid: i64 = vid.to_string().parse().unwrap();
                let pid: i64 = pid.to_string().parse().unwrap();
                rs = calculate_hash_string(config.secret_number, pid, vid) == hash_str.as_ref();
                eprintln!("Props: {:#?}, Match: {:#?}", &hash_str, &rs);
            }
            if rs {
                variant
            } else {
                None
            }
        })
        .map(|variant| output::Target {
            product_variant: Some(output::ProductVariantTarget {
                id: variant.id.to_string(),
                quantity: Some(1),
            })
        })
        .collect::<Vec<output::Target>>();

    if target.is_empty() {
        return Ok(no_discount);
    }

    Ok(output::FunctionResult {
        discount_application_strategy: output::DiscountApplicationStrategy::FIRST,
        discounts: vec![output::Discount {
            message: Some(config.message),
            targets: target,
            value: output::Value {
                percentage: Some(output::Percentage {
                    value: "100".to_string()
                }),
                fixed_amount: None,
            },
        }],
    })
}

#[cfg(test)]
mod tests;