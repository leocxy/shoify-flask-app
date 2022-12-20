#![allow(dead_code)]

pub type Boolean = bool;
pub type Float = f64;
pub type Int = i64;
pub type ID = String;

pub mod input {
    use super::*;
    use serde::Deserialize;

    #[derive(Clone, Debug, Deserialize)]
    #[serde(rename_all(deserialize = "camelCase"))]
    pub struct Input {
        pub discount_node: DiscountNode,
        pub cart: Cart,
    }

    #[derive(Clone, Debug, Deserialize, Default)]
    pub struct DiscountNode {
        pub metafield: Option<Metafield>,
    }

    #[derive(Clone, Debug, Deserialize, Default)]
    #[serde(rename_all(deserialize = "camelCase"))]
    pub struct Metafield {
        pub value: Option<String>,
    }

    #[derive(Clone, Debug, Serialize, Deserialize)]
    #[serde(rename_all = "camelCase")]
    pub struct Configuration {
        pub method: String,
        pub value: Float,
        pub threshold: Int,
    }

    impl Configuration {
        const DEFAULT_VALUE: Float = 0.0;
        const DEFAULT_THRESHOLD: Int = 0;

        fn from_str(str: &str) -> Self {
            serde_json::from_str(str).unwrap_or_default()
        }
    }

    impl Default for Configuration {
        fn default() -> Self {
            Configuration {
                method: "none".to_string(),
                value: Self::DEFAULT_VALUE,
                threshold: Self::DEFAULT_THRESHOLD,
            }
        }
    }

    impl input::Input {
        pub fn configuration(&self) -> Configuration {
            let value: Option<&str> = self
                .discount_node
                .metafield
                .as_ref()
                .and_then(|metafield| metafield.value.as_deref());
            value.map(Configuration::from_str).unwrap_or_default()
        }
    }

    #[derive(Clone, Debug, Deserialize)]
    #[serde(rename_all = "camelCase")]
    pub struct Cart {
        pub lines: Vec<CartLine>,
        pub cost: Option<Cost>,
        pub buyer_identity: Option<BuyerIdentity>,
        pub attribute: Option<Vec<Attribute>>,
    }

    #[derive(Clone, Debug, Deserialize)]
    pub struct CartLine {
        pub quantity: Int,
        pub merchandise: Merchandise,
        pub cost: CartLineCost
    }

    #[derive(Clone, Debug, Deserialize)]
    #[serde(rename_all = "camelCase")]
    pub struct CartLineCost {
        pub amount_per_quantity: Option<MoneyV2>,
        pub compare_at_amount_per_quantity: Option<MoneyV2>,
        pub subtotal_amount: Option<MoneyV2>,
        pub total_amount: Option<MoneyV2>,
    }

    #[derive(Clone, Debug, Deserialize)]
    pub struct Merchandise {
        pub id: Option<ID>,
        pub sku: Option<String>,
        pub metafield: Option<String>,
    }

    #[derive(Clone, Debug, Deserialize)]
    #[serde(rename_all = "camelCase")]
    pub struct MoneyV2 {
        pub amount: Option<String>,
        // pub currency_code: Option<String>,
    }

    #[derive(Clone, Debug, Deserialize)]
    #[serde(rename_all = "camelCase")]
    pub struct Customer {
        pub amount_spend: Option<MoneyV2>,
        pub email: Option<String>,
        pub number_of_orders: Option<i32>,
        pub metafield: Option<Metafield>,
    }

    #[derive(Clone, Debug, Deserialize)]
    pub struct BuyerIdentity {
        pub email: Option<String>,
        pub customer: Option<Customer>,
    }

    #[derive(Clone, Debug, Deserialize)]
    #[serde(rename_all = "camelCase")]
    pub struct Cost {
        pub subtotal_amount: Option<MoneyV2>,
        pub total_amount: Option<MoneyV2>,
    }

    #[derive(Clone, Debug, Deserialize)]
    pub struct Attribute {
        pub key: String,
        pub value: String,
    }
}

use serde::Serialize;
use serde_with::skip_serializing_none;

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all(serialize = "camelCase"))]
pub struct FunctionResult {
    pub discount_application_strategy: DiscountApplicationStrategy,
    pub discounts: Vec<Discount>,
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all(serialize = "SCREAMING_SNAKE_CASE"))]
pub enum DiscountApplicationStrategy {
    First,
    Maximum,
}

#[skip_serializing_none]
#[derive(Clone, Debug, Serialize)]
pub struct Discount {
    pub value: Value,
    pub targets: Vec<Target>,
    pub message: Option<String>,
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all(serialize = "camelCase"))]
pub enum Value {
    FixedAmount(FixedAmount),
    Percentage(Percentage),
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all(serialize = "camelCase"))]
pub struct FixedAmount {
    pub applies_to_each_item: Option<Boolean>,
    pub value: Float,
}

#[derive(Clone, Debug, Serialize)]
pub struct Percentage {
    pub value: Float,
}

#[skip_serializing_none]
#[derive(Clone, Debug, Serialize)]
#[serde(rename_all(serialize = "camelCase"))]
pub enum Target {
    ProductVariant { id: ID, quantity: Option<Int> },
}