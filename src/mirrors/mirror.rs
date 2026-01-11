use chrono::{DateTime, FixedOffset};
use serde::Deserialize;
use url::Url;

pub use self::duration::Duration;
pub use self::protocol::Protocol;
pub use crate::country::Country;

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
    country: String,
    country_code: String,
    isos: bool,
    ipv4: bool,
    ipv6: bool,
    details: Url,
}

impl Mirror {
    /// Return the mirror's URL.
    #[must_use]
    pub const fn url(&self) -> &Url {
        &self.url
    }

    /// Return the used protocol.
    #[must_use]
    pub const fn protocol(&self) -> Protocol {
        self.protocol
    }

    /// Return the date and time of last sync, if any.
    #[must_use]
    pub const fn last_sync(&self) -> Option<DateTime<FixedOffset>> {
        self.last_sync
    }

    /// Return the completion percentage if any.
    #[must_use]
    pub const fn completion_pct(&self) -> Option<f64> {
        self.completion_pct
    }

    /// Return the delay, if any.
    #[must_use]
    pub const fn delay(&self) -> Option<u64> {
        self.delay
    }

    /// Return the score, if any.
    #[must_use]
    pub const fn score(&self) -> Option<f64> {
        self.score
    }

    /// Return the country.
    pub fn country(&self) -> Result<Country, String> {
        self.country_code.parse()
    }

    #[must_use]
    pub const fn isos(&self) -> bool {
        self.isos
    }

    #[must_use]
    pub const fn ipv4(&self) -> bool {
        self.ipv4
    }

    #[must_use]
    pub const fn ipv6(&self) -> bool {
        self.ipv6
    }

    #[must_use]
    pub const fn details(&self) -> &Url {
        &self.details
    }
}
