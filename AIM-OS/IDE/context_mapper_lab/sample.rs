//! Sample Rust file for extractor harness testing.

use std::path::Path;

pub struct SampleStruct {
    pub id: u32,
    pub name: String,
}

#[non_exhaustive]
pub enum SampleEnum {
    A,
    B(String),
}

#[repr(C)]
pub trait SampleTrait {
    fn run(&self) -> bool;
}

pub fn public_fn(x: i32) -> i32 {
    x * 2
}

pub type Alias = Vec<String>;

pub const MAX_SIZE: usize = 1024;

fn main() {}
