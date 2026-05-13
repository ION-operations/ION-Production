//! Sample Rust file for extractor harness testing.
//! Realistic attributes: #[repr(C)] on struct, #[non_exhaustive] on enum, plain trait.

use std::path::Path;

#[repr(C)]
pub struct SampleStruct {
    pub id: u32,
    pub name: String,
}

#[non_exhaustive]
pub enum SampleEnum {
    A,
    B(String),
}

pub trait SampleTrait {
    fn run(&self) -> bool;
}

pub fn public_fn(x: i32) -> i32 {
    x * 2
}

pub type Alias = Vec<String>;

pub const MAX_SIZE: usize = 1024;

fn main() {}
