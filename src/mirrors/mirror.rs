use chrono::{DateTime, FixedOffset};
use serde::Deserialize;
use url::Url;

pub use self::country::Country;
pub use self::duration::Duration;
pub use self::protocol::Protocol;

mod country;
mod duration;
mod protocol;

/// Information about a single mirror.
#[expect(clippy::struct_excessive_bools)]
#[derive(Clone, Debug, PartialEq, Deserialize)]
pub struct Mirror {
    url: Url,
    protocol: Protocol,
    last_sync: Option<DateTime<FixedOffset>>,
    completion_pct: Option<f64>,
    delay: Option<u64>,
    #[serde(flatten)]
    duration: Option<Duration>,
    score: Option<f64>,
    active: bool,
    #[serde(flatten)]
    country: Country,
    isos: bool,
    ipv4: bool,
    ipv6: bool,
    details: Url,
}
