use clap::Args;

/// Mirror filter.
#[derive(Clone, Debug, Args)]
pub struct Filter {
    name: String,
}
