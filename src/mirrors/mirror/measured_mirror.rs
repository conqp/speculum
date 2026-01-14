use std::ops::Deref;
use std::time::Duration;

use crate::mirrors::Mirror;

#[derive(Clone, Debug, PartialEq)]
pub struct MeasuredMirror {
    mirror: Mirror,
    download_duration: Option<Duration>,
}

impl MeasuredMirror {
    /// Crate a new measured mirror.
    #[must_use]
    pub(crate) const fn new(mirror: Mirror, download_duration: Option<Duration>) -> Self {
        Self {
            mirror,
            download_duration,
        }
    }

    /// Return the measured duration.
    #[must_use]
    pub const fn download_duration(&self) -> Option<Duration> {
        self.download_duration
    }
}

impl Deref for MeasuredMirror {
    type Target = Mirror;

    fn deref(&self) -> &Self::Target {
        &self.mirror
    }
}
