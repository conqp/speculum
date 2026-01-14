use std::num::NonZero;

use clap::{Parser, Subcommand};

use self::filter_option::FilterOption;
use self::list_target::ListTarget;
use self::sorting_option::SortingOption;

mod filter_option;
mod list_target;
mod sorting_option;

#[derive(Clone, Debug, Parser)]
pub struct Args {
    #[clap(subcommand)]
    pub(crate) action: Action,
}

#[derive(Clone, Debug, Subcommand)]
pub enum Action {
    /// List available options.
    List {
        #[clap(subcommand)]
        target: ListTarget,
    },
    /// Generate a mirror list.
    Generate {
        #[clap(long, short, help = "Filter mirrors by the given options.")]
        filter: Vec<FilterOption>,
        #[clap(long, short, help = "Sort mirrors by the given property.")]
        sort_by: Option<SortingOption>,
        #[clap(long, short, help = "Limit amount of mirrors to the given number.")]
        limit: Option<NonZero<usize>>,
    },
}
