use clap::{Parser, Subcommand};

use crate::filter::Filter;

#[derive(Clone, Debug, Parser)]
pub struct Args {
    #[clap(subcommand)]
    pub(crate) action: Action,
}

#[derive(Clone, Debug, Subcommand)]
pub enum Action {
    List {
        #[clap(subcommand)]
        target: ListTarget,
    },
    Rank(RankArgs),
}

#[derive(Clone, Debug, Subcommand)]
pub enum ListTarget {
    Countries,
    SortingOptions,
}

#[derive(Clone, Debug, clap::Args)]
pub struct RankArgs {
    #[clap(long, short)]
    pub(crate) filter: Filter,
    pub(crate) threshold_milliseconds: u64,
}
