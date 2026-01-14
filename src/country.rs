use clap::ValueEnum;
use clap::builder::PossibleValue;

/// Available countries.
#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
pub enum Country {
    France,
    Germany,
}

impl ValueEnum for Country {
    fn value_variants<'a>() -> &'a [Self] {
        &[Self::France, Self::Germany]
    }

    fn to_possible_value(&self) -> Option<PossibleValue> {
        match self {
            Self::France => Some(PossibleValue::new("France").alias("FR")),
            Self::Germany => Some(PossibleValue::new("Germany").alias("DE")),
        }
    }
}
