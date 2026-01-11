use crate::mirrors::Country;

/// Available countries.
pub enum Countries {
    France,
    Germany,
}

impl From<Countries> for Country<&'static str> {
    fn from(countries: Countries) -> Self {
        match countries {
            Countries::France => Country::new("France", "FR"),
            Countries::Germany => Country::new("Germany", "DE"),
        }
    }
}
