//! Strike 1 — Mini harness: one Rust file or fixture target; resolve local imports only.

use context_mapper_lab::{
    maybe_emit_passive_shadow, resolve_imports, ContractExtractor, ExtractedFile,
    PassiveEmitOutcome, TreeSitterExtractor,
};
use std::env;
use std::fs;
use std::path::Path;

fn main() {
    println!("===================================================");
    println!("  CONTEXT MAPPER LAB — Single-file / fixture mode   ");
    println!("===================================================\n");

    let path = env::args()
        .nth(1)
        .or_else(|| {
            let default = "fixtures/basic_crate/src/lib.rs";
            if Path::new(default).exists() {
                Some(default.to_string())
            } else {
                None
            }
        })
        .or_else(|| {
            let home = env::var("USERPROFILE").unwrap_or_else(|_| ".".into());
            let wp = Path::new(&home)
                .join("Documents")
                .join("Application_Dev")
                .join("IDE")
                .join("wire_proof")
                .join("src")
                .join("main.rs");
            if wp.exists() {
                Some(wp.to_string_lossy().into_owned())
            } else {
                None
            }
        })
        .unwrap_or_else(|| {
            eprintln!("Usage: context_mapper_lab <path-to-rust-file>");
            eprintln!("Example: context_mapper_lab fixtures/basic_crate/src/lib.rs");
            std::process::exit(1);
        });

    let target_path = Path::new(&path);
    let contents = match fs::read_to_string(target_path) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("Failed to read {}: {}", path, e);
            std::process::exit(1);
        }
    };

    let extractor = TreeSitterExtractor::new();
    let extracted = extractor.extract(&path, &contents);

    let crate_root = target_path
        .parent()
        .unwrap_or_else(|| Path::new("."));
    let resolved = resolve_imports(crate_root, &extracted.imports);
    let shadow_outcome = maybe_emit_passive_shadow(&contents, &extracted, &resolved);

    println!("Target file: {}", path);
    println!("Crate root:  {}", crate_root.display());
    println!("\n--- Imports (use) ---");
    if extracted.imports.is_empty() {
        println!("  (none)");
    } else {
        for u in &extracted.imports {
            println!("  {}", u);
        }
    }
    println!("\n--- Contracts (pub) ---");
    print_contracts(&extracted);
    println!("\n--- Resolved Local Files ---");
    if resolved.is_empty() {
        println!("  (none)");
    } else {
        for p in &resolved {
            println!("  {}", p.display());
        }
    }

    println!("\n--- Passive Shadow Emit (feature-flagged) ---");
    match shadow_outcome {
        PassiveEmitOutcome::Disabled => {
            println!(
                "  disabled (set AIMOS_SHADOW_BCI_PASSIVE_EMIT=true to attempt passive shadow emission)"
            );
        }
        PassiveEmitOutcome::Emitted {
            snapshot_path,
            elapsed_ms,
        } => {
            println!("  success");
            println!("  snapshot: {}", snapshot_path.display());
            println!("  elapsed_ms: {}", elapsed_ms);
        }
        PassiveEmitOutcome::Failed { error } => {
            println!("  fail-open (live path preserved)");
            println!("  error: {}", error);
        }
    }

    println!("\n===================================================");
    println!("  One file in, contracts out. Strike 1 Phase 1D.  ");
    println!("===================================================");
}

fn print_contracts(e: &ExtractedFile) {
    println!("  File: {} | confidence: {:?}", e.path, e.confidence);
    if e.contracts.is_empty() {
        println!("  (no pub contracts)");
    } else {
        for c in &e.contracts {
            println!("  [{}] {}", c.kind, c.name);
            if let Some(ref sig) = c.signature {
                println!("      {}", sig);
            }
        }
    }
}
