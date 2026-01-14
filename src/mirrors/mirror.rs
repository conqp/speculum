use std::time::Duration;

use chrono::{DateTime, FixedOffset};
use clap::ValueEnum;
use log::error;
use reqwest::get;
use serde::Deserialize;
use tokio::time::Instant;
use url::Url;

use self::measured_mirror::MeasuredMirror;
pub use self::measurement_error::MeasurementError;
pub use self::protocol::Protocol;
pub use crate::country::Country;

mod measured_mirror;
mod measurement_error;
mod protocol;

const EXTRA_DB_PATH: &str = "extra/os/x86_64/extra.db";

/// Information about a single mirror.
#[expect(clippy::struct_excessive_bools)]
#[derive(Clone, Debug, PartialEq, Deserialize)]
pub struct Mirror {
    url: Url,
    protocol: Protocol,
    last_sync: Option<DateTime<FixedOffset>>,
    completion_pct: Option<f64>,
    delay: Option<u64>,
    duration_avg: Option<f64>,
    duration_stddev: Option<f64>,
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

    /// Return the average duration, if any.
    #[must_use]
    pub const fn duration_avg(&self) -> Option<f64> {
        self.duration_avg
    }

    /// Return the standard deviation of the duration, if any.
    #[must_use]
    pub const fn duration_stddev(&self) -> Option<f64> {
        self.duration_stddev
    }

    /// Return the score, if any.
    #[must_use]
    pub const fn score(&self) -> Option<f64> {
        self.score
    }

    /// Return the country.
    pub fn country(&self) -> Result<Country, String> {
        ValueEnum::from_str(&self.country_code, true)
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

    /// Measure the mirror speed.
    ///
    /// TODO: Support `rsync`.
    ///
    /// # Errors
    ///
    /// Returns a [`MeasurementError`] if a URL parsing or request error occurs.
    pub async fn measure(&self) -> Result<Duration, MeasurementError> {
        let start = Instant::now();
        let _extra_db = get(self.url.join(EXTRA_DB_PATH)?)
            .await?
            .error_for_status()?
            .bytes()
            .await?;
        Ok(start.elapsed())
    }

    /// Measure the mirror and return a measured mirror.
    pub async fn measured(self) -> MeasuredMirror {
        let duration = self
            .measure()
            .await
            .inspect_err(|error| error!("{error}"))
            .ok();
        MeasuredMirror::new(self, duration)
    }
}
