use chrono::{DateTime, FixedOffset};
use reqwest::{IntoUrl, get};
use serde::Deserialize;

pub use self::mirror::Mirror;
use crate::URL;

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
    /// Get the mirrors from the given URL.
    ///
    /// # Errors
    ///
    /// Returns an [`reqwest::Error`] if the request could not be executed successfully.
    pub async fn get<T>(url: T) -> reqwest::Result<Mirrors>
    where
        T: IntoUrl,
    {
        get(URL).await?.error_for_status()?.json().await
    }
}
