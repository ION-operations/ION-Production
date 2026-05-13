use criterion::{black_box, criterion_group, criterion_main, Criterion};
use quaternion_kernel::*;
use rand::Rng;

fn bench_quantum_operations(c: &mut Criterion) {
    let mut rng = rand::thread_rng();
    let mut group = c.benchmark_group("quantum");
    
    fn random_qaddr(rng: &mut impl Rng) -> QAddr {
        QAddr {
            n: PrincipalShell(rng.gen_range(0..4u8)),
            l: match rng.gen_range(0..7u8) {
                0 => OrbitalClass::Memory,
                1 => OrbitalClass::Io,
                2 => OrbitalClass::Network,
                3 => OrbitalClass::Model,
                4 => OrbitalClass::Crypto,
                5 => OrbitalClass::Ui,
                _ => OrbitalClass::Governance,
            },
            m: MagneticChannel(S3Bin(rng.gen_range(0..65536u16))),
            s: match rng.gen_range(0..4u8) {
                0 => Spin::Read,
                1 => Spin::Write,
                2 => Spin::Plan,
                _ => Spin::Act,
            },
            morton_key: MortonKey(rng.gen()),
        }
    }
    
    group.bench_function("validate_transition", |b| {
        let addr1 = random_qaddr(&mut rng);
        let addr2 = random_qaddr(&mut rng);
        let rules = SelectionRules {
            delta_n: 0,
            delta_l: true,
            delta_m: true,
            delta_s: false,
        };
        b.iter(|| validate_transition(black_box(&addr1), black_box(&addr2), black_box(&rules)))
    });
    
    group.finish();
}

criterion_group!(benches, bench_quantum_operations);
criterion_main!(benches);

