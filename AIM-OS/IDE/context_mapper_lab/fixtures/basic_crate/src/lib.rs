// Phase 1H fixture: grouped import, alias, and glob.
use crate::foo::{Foo, make_foo};
use crate::bar::bar_name as bn;
use crate::bar::*;

pub fn run_target() -> i32 {
    let _f = make_foo(42);
    let _x = bn();
    0
}
