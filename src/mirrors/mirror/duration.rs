use serde::Deserialize;

/// Duration information.
#[derive(Clone, Debug, PartialEq, Deserialize)]
pub struct Duration {
    #[serde(rename = "duration_avg")]
    average: f64,
    #[serde(rename = "duration_stddev")]
    standard_deviation: f64,
}
