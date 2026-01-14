use std::str::FromStr;

use clap::ValueEnum;

use crate::country::Country;
use crate::mirrors::Protocol;

/// Filtering options.
#[derive(Clone, Debug)]
pub enum FilterOption {
    /// Filter by country.
    Country(Country),
    /// Filter by protocol.
    Protocol(Protocol),
}

impl FromStr for FilterOption {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let Some((key, value)) = s.split_once('=') else {
            return Err("No value specified.".into());
        };

        match key {
            "country" => Country::from_str(value, true).map(Self::Country),
            "protocol" => Protocol::from_str(value, true).map(Self::Protocol),
            other => Err(format!("Unknown filter option: {other}")),
        }
    }
}
