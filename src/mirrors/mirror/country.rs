use std::ops::Deref;

use serde::Deserialize;

/// Country information.
#[derive(Clone, Debug, Hash, Deserialize)]
pub struct Country<T> {
    #[serde(rename = "country")]
    name: T,
    #[serde(rename = "country_code")]
    code: T,
}

impl Country<&'static str> {}

impl<T> Country<T>
where
    T: Deref<Target = str>,
{
    /// Create a new `Country`.
    #[must_use]
    pub const fn new(name: T, code: T) -> Self {
        Self { name, code }
    }

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

impl<T, U> PartialEq<Country<U>> for Country<T>
where
    T: Deref<Target = str>,
    U: Deref<Target = str>,
{
    fn eq(&self, other: &Country<U>) -> bool {
        (self.code() == other.code()) || (self.name() == other.name())
    }
}
