use chrono::{DateTime, FixedOffset};
use reqwest::{IntoUrl, get};
use serde::Deserialize;

pub use self::mirror::{Country, Duration, Mirror, Protocol};

mod mirror;

#[derive(Clone, Debug, PartialEq, Deserialize)]
pub struct Mirrors {
    cutoff: u64,
    last_check: DateTime<FixedOffset>,
    num_checks: usize,
    check_frequency: u64,
    urls: Vec<Mirror>,
    version: u8,
}

impl Mirrors {
    /// Return the cutoff value.
    #[must_use]
    pub const fn cutoff(&self) -> u64 {
        self.cutoff
    }

    /// Return the timestamp of the last check.
    #[must_use]
    pub const fn last_check(&self) -> DateTime<FixedOffset> {
        self.last_check
    }

    /// Return the amount of checks.
    #[must_use]
    pub const fn num_checks(&self) -> usize {
        self.num_checks
    }

    /// Return the check frequency.
    #[must_use]
    pub const fn check_frequency(&self) -> u64 {
        self.check_frequency
    }

    /// Return the mirror list.
    #[must_use]
    pub fn urls(&self) -> &[Mirror] {
        &self.urls
    }

    /// Return the API version.
    #[must_use]
    pub const fn version(&self) -> u8 {
        self.version
    }

    /// Get the mirrors from the given URL.
    ///
    /// # Errors
    ///
    /// Returns an [`reqwest::Error`] if the request could not be executed successfully.
    pub async fn get<T>(url: T) -> reqwest::Result<Self>
    where
        T: IntoUrl,
    {
        get(url).await?.error_for_status()?.json().await
    }
}
