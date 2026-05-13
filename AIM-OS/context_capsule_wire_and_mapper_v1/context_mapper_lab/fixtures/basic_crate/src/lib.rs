//! Fixture target: lib.rs with std + crate imports.

use std::collections::HashMap;
use crate::dummy_models::SampleModel;
use crate::dummy_utils::HelperConfig;

pub fn run() -> Option<SampleModel> {
    let _: HashMap<(), ()> = HashMap::new();
    let _ = HelperConfig;
    None
}
