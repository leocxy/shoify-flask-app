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
    pub method: String,
    pub value: i64,
    pub message: String,
    pub secret_number: i64,
    pub pid: i64,
}

pub fn calculate_hash_string(secret_number: i64, pid: i64, vid: i64) -> String {
    let pid = pid.to_string();
    let len_check: usize = 10;
    let mut hash_str = if pid.len() > len_check {
        "1".to_string() + &pid[pid.len() - 10..] + secret_number.to_string().as_str()
    } else {
        "1".to_string() + &pid[..] + secret_number.to_string().as_str()
    };
    let vid = vid.to_string();
    let len_check: usize = 5;
    if vid.len() > len_check {
        hash_str += &vid[vid.len() - 5..]
    } else {
        hash_str += &vid
    }
    hash_str = format!("0x{:x}", hash_str.parse::<i64>().unwrap_or_default() / secret_number);
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
        return Ok(no_discount)
    }

    let cart_lines = input.cart.lines;
    if cart_lines.is_empty() {
        return Ok(no_discount)
    }

    // find the gift with purchase item
    // let target = vec![];
    // for item in cart_lines {
    //     // check the hash string
    //     // if item
    //
    //     // apply the discount
    // }

    eprintln!("{:#?}", calculate_hash_string(config.secret_number, 1234567890123, 1234567));

    Ok(no_discount)
}

#[cfg(test)]
mod tests;