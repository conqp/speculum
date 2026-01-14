use std::str::FromStr;

use clap::ValueEnum;
use serde::Deserialize;

/// Supported protocols
#[derive(Clone, Copy, Debug, Eq, PartialEq, Hash, Deserialize, ValueEnum)]
#[serde(rename_all = "lowercase")]
pub enum Protocol {
    /// HTTP
    Http,
    /// HTTPS
    Https,
    /// RSYNC
    Rsync,
}
