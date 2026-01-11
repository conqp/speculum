use serde::Deserialize;

/// Country information.
#[derive(Clone, Debug, Eq, PartialEq, Hash, Deserialize)]
pub struct Country {
    #[serde(rename = "country")]
    name: String,
    #[serde(rename = "country_code")]
    code: String,
}

impl Country {
    /// Return the country's name.
    #[must_use]
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Return the country's code.
    #[must_use]
    pub fn code(&self) -> &str {
        &self.code
    }
}
