use clap::ValueEnum;

/// Options to sort the mirrors by.
#[derive(Clone, Copy, Debug, ValueEnum)]
pub enum SortingOption {
    /// Sort by last sync,
    LastSync,
    /// Sort by completion.
    CompletionPct,
    /// Sort by delay.
    Delay,
    /// Sort by duration.
    Duration,
    /// Sort by score.
    Score,
    /// Sort by measurement.
    Measurement,
}
