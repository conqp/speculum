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
    country: Country<String>,
    isos: bool,
    ipv4: bool,
    ipv6: bool,
    details: Url,
}

impl Mirror {
    pub fn url(&self) -> &Url {
        &self.url
    }

    pub fn protocol(&self) -> Protocol {
        self.protocol
    }

    pub fn last_sync(&self) -> Option<DateTime<FixedOffset>> {
        self.last_sync
    }

    pub fn completion_pct(&self) -> Option<f64> {
        self.completion_pct
    }

    pub fn delay(&self) -> Option<u64> {
        self.delay
    }

    pub fn score(&self) -> Option<f64> {
        self.score
    }

    pub fn country(&self) -> &Country<String> {
        &self.country
    }

    pub fn isos(&self) -> bool {
        self.isos
    }

    pub fn ipv4(&self) -> bool {
        self.ipv4
    }

    pub fn ipv6(&self) -> bool {
        self.ipv6
    }

    pub fn details(&self) -> &Url {
        &self.details
    }
}
