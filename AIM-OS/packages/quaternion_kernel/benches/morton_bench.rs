use criterion::{black_box, criterion_group, criterion_main, Criterion};
use quaternion_kernel::*;
use rand::Rng;

fn bench_morton4d_encode(c: &mut Criterion) {
    let mut rng = rand::thread_rng();
    let mut group = c.benchmark_group("morton4d");
    
    group.bench_function("encode", |b| {
        let pos = Vec4 {
            x: rng.gen_range(0.0..1.0),
            y: rng.gen_range(0.0..1.0),
            z: rng.gen_range(0.0..1.0),
            tau: rng.gen_range(0.0..1.0),
        };
        b.iter(|| morton4d_encode(black_box(&pos)))
    });
    
    group.bench_function("decode", |b| {
        let key = MortonKey(rng.gen());
        b.iter(|| morton4d_decode(black_box(key)))
    });
    
    group.bench_function("round_trip", |b| {
        let pos = Vec4 {
            x: rng.gen_range(0.0..1.0),
            y: rng.gen_range(0.0..1.0),
            z: rng.gen_range(0.0..1.0),
            tau: rng.gen_range(0.0..1.0),
        };
        b.iter(|| {
            let key = morton4d_encode(&pos);
            morton4d_decode(key)
        })
    });
    
    group.finish();
}

criterion_group!(benches, bench_morton4d_encode);
criterion_main!(benches);

