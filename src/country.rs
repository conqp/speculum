use std::str::FromStr;

/// Available countries.
#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
pub enum Country {
    France,
    Germany,
}

impl FromStr for Country {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        // TODO: Implement all countries.
        match s {
            "France" | "FR" => Ok(Self::France),
            "Germany" | "DE" => Ok(Self::Germany),
            other => Err(other.to_owned()),
        }
    }
}
