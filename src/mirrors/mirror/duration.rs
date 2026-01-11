use serde::Deserialize;

/// Duration information.
#[derive(Clone, Copy, Debug, PartialEq, Deserialize)]
pub struct Duration {
    #[serde(rename = "duration_avg")]
    average: f64,
    #[serde(rename = "duration_stddev")]
    standard_deviation: f64,
}

impl Duration {
    /// Return the average duration.
    #[must_use]
    pub const fn average(self) -> f64 {
        self.average
    }

    /// Return the standard deviation of the duration.
    #[must_use]
    pub const fn standard_deviation(self) -> f64 {
        self.standard_deviation
    }
}
