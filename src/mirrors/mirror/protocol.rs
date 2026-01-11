use serde::Deserialize;

/// Supported protocols
#[derive(Clone, Copy, Debug, Eq, PartialEq, Hash, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Protocol {
    /// HTTP
    Http,
    /// HTTPS
    Https,
    /// RSYNC
    Rsync,
}
