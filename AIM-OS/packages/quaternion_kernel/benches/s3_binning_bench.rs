use criterion::{black_box, criterion_group, criterion_main, Criterion};
use quaternion_kernel::*;
use rand::Rng;

fn bench_s3_binning(c: &mut Criterion) {
    let mut rng = rand::thread_rng();
    let mut group = c.benchmark_group("s3_binning");
    
    // Generate random unit quaternions
    fn random_unit_quat(rng: &mut impl Rng) -> Quat {
        // Generate random point on S³ using Gaussian method
        let w = rng.gen_range(-1.0..1.0);
        let x = rng.gen_range(-1.0..1.0);
        let y = rng.gen_range(-1.0..1.0);
        let z = rng.gen_range(-1.0..1.0);
        let norm = (w*w + x*x + y*y + z*z).sqrt();
        if norm < 1e-10 {
            Quat { w: 1.0, x: 0.0, y: 0.0, z: 0.0 }
        } else {
            Quat {
                w: w / norm,
                x: x / norm,
                y: y / norm,
                z: z / norm,
            }
        }
    }
    
    group.bench_function("encode", |b| {
        let quat = random_unit_quat(&mut rng);
        b.iter(|| s3_bin_encode(black_box(&quat)))
    });
    
    group.bench_function("neighbors", |b| {
        let bin = S3Bin(rng.gen_range(0..65536u16));
        b.iter(|| get_s3_neighbors(black_box(bin)))
    });
    
    group.finish();
}

criterion_group!(benches, bench_s3_binning);
criterion_main!(benches);

