use criterion::{black_box, criterion_group, criterion_main, Criterion};
use quaternion_kernel::*;
use rand::Rng;

fn bench_kernel_syscalls(c: &mut Criterion) {
    let mut rng = rand::thread_rng();
    let mut group = c.benchmark_group("kernel_syscalls");
    
    fn random_qaddr(rng: &mut impl Rng) -> QAddr {
        QAddr {
            n: PrincipalShell(rng.gen_range(0..4u8)),
            l: OrbitalClass::Memory,
            m: MagneticChannel(S3Bin(rng.gen_range(0..65536u16))),
            s: Spin::Act,
            morton_key: MortonKey(rng.gen()),
        }
    }
    
    fn random_dual_quat(rng: &mut impl Rng) -> DualQuat {
        // Generate random rotation quaternion
        let w = rng.gen_range(-1.0..1.0);
        let x = rng.gen_range(-1.0..1.0);
        let y = rng.gen_range(-1.0..1.0);
        let z = rng.gen_range(-1.0..1.0);
        let rot_norm = (w*w + x*x + y*y + z*z).sqrt();
        let rotation = Quat {
            w: if rot_norm > 1e-10 { w / rot_norm } else { 1.0 },
            x: if rot_norm > 1e-10 { x / rot_norm } else { 0.0 },
            y: if rot_norm > 1e-10 { y / rot_norm } else { 0.0 },
            z: if rot_norm > 1e-10 { z / rot_norm } else { 0.0 },
        };
        
        // Generate random translation (pure quaternion)
        let translation = Quat {
            w: 0.0,
            x: rng.gen_range(-1.0..1.0),
            y: rng.gen_range(-1.0..1.0),
            z: rng.gen_range(-1.0..1.0),
        };
        
        DualQuat { rotation, translation }
    }
    
    group.bench_function("place", |b| {
        let mut kernel = Kernel::new();
        let actor_addr = random_qaddr(&mut rng);
        let mut entity_id = 1u128;
        
        b.iter(|| {
            let entity_state = EntityState {
                addr: random_qaddr(&mut rng),
                pose: random_dual_quat(&mut rng),
            };
            let result = kernel.place(&actor_addr, entity_id, entity_state);
            if result.is_ok() {
                entity_id += 1;
            }
            result
        })
    });
    
    group.bench_function("sense", |b| {
        let mut kernel = Kernel::new();
        let actor_addr = random_qaddr(&mut rng);
        
        // Pre-populate kernel with entities
        for i in 1..100 {
            let entity_state = EntityState {
                addr: random_qaddr(&mut rng),
                pose: random_dual_quat(&mut rng),
            };
            let _ = kernel.place(&actor_addr, i, entity_state);
        }
        
        let region_key = CompositeKey::new(
            MortonKey(rng.gen()),
            S3Bin(rng.gen_range(0..65536u16))
        );
        
        b.iter(|| kernel.sense(black_box(&actor_addr), black_box(region_key), black_box(None)))
    });
    
    group.finish();
}

criterion_group!(benches, bench_kernel_syscalls);
criterion_main!(benches);

