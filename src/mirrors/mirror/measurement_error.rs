use std::error::Error;
use std::fmt::Display;

use url::ParseError;

/// Errors that can occur during a mirror measurement.
#[derive(Debug)]
pub enum MeasurementError {
    /// The URL could not be parsed.
    Url(ParseError),
    /// The HTTP request failed.
    Request(reqwest::Error),
}

impl Display for MeasurementError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            MeasurementError::Url(error) => error.fmt(f),
            MeasurementError::Request(error) => error.fmt(f),
        }
    }
}

impl Error for MeasurementError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            MeasurementError::Url(error) => Some(error),
            MeasurementError::Request(error) => Some(error),
        }
    }
}

impl From<ParseError> for MeasurementError {
    fn from(error: ParseError) -> Self {
        Self::Url(error)
    }
}

impl From<reqwest::Error> for MeasurementError {
    fn from(error: reqwest::Error) -> Self {
        Self::Request(error)
    }
}
