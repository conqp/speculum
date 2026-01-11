//! Mirror ranking and mirror list updating tool.

use std::error::Error;
use std::process::ExitCode;

use log::{debug, error};

use crate::countries::Countries;
use crate::mirrors::{Country, Mirrors};

mod args;
mod countries;
mod filter;
mod mirrors;

const URL: &str = "https://archlinux.org/mirrors/status/json/";

#[tokio::main]
async fn main() -> ExitCode {
    env_logger::init();

    let Ok(mirrors) = Mirrors::get(URL).await.inspect_err(|error| {
        error!("{error}");

        if let Some(source) = error.source() {
            debug!("{source}");
        }
    }) else {
        return ExitCode::FAILURE;
    };

    for mirror in mirrors
        .urls()
        .iter()
        .filter(|mirror| mirror.country() == &Country::from(Countries::Germany))
    {
        println!("{mirror:?}");
    }

    ExitCode::SUCCESS
}
