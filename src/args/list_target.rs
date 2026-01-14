use clap::Subcommand;

/// Possible listing targets.
#[derive(Clone, Copy, Debug, Subcommand)]
pub enum ListTarget {
    /// List countries.
    Countries,
    /// List sorting options.
    SortingOptions,
}
