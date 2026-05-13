// Phase 1I fixture: target imports through façade (api) which re-exports from inner.
use crate::api::Thing;

pub fn run() -> i32 {
    let t = Thing { x: 42 };
    t.x
}
