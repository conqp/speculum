use serde::Deserialize;

/// Country information.
#[derive(Clone, Debug, Eq, PartialEq, Hash, Deserialize)]
pub struct Country {
    #[serde(rename = "country")]
    name: String,
    #[serde(rename = "country_code")]
    code: String,
}
