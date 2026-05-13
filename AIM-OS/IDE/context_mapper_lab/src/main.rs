//! Strike 1 — Harness: target + normalized imports + deps + envelope (Phase 1H).
//! Phase 1L: gauntlet mode — run pipeline on multiple target files and print summary.

use context_mapper_lab::{
    expand_grouped_submodules, parse_imports, re_export_resolve, resolve_import_refs, slice_contracts,
    ContractExtractor, Contract, ExtractedFile, ImportRef, ParseConfidence, TreeSitterExtractor,
    SystemEnvelope,
};
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

/// Normalize path for console display: forward slashes (matches envelope).
fn display_path(p: &Path) -> String {
    p.to_string_lossy().replace('\\', "/")
}

/// Result of one pipeline run for summary classification.
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum RunStatus {
    Success,
    Partial,
    Failed,
}

/// Category of first concrete failure (mapper-only).
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum IssueCategory {
    None,
    ExtractorLimitation,
    ImportNormalizationLimitation,
    ResolverLimitation,
    ReExportLimitation,
    SlicerLimitation,
    EnvelopeRenderingIssue,
}

/// One gauntlet run: all outputs + status for summary.
pub struct RunResult {
    pub path: String,
    pub crate_root: String,
    pub raw_imports: Vec<String>,
    pub import_refs: Vec<ImportRef>,
    pub resolved: Vec<PathBuf>,
    pub re_exported: Vec<PathBuf>,
    pub target_contracts: Vec<Contract>,
    pub target_confidence: ParseConfidence,
    pub dep_contracts_unpruned: Vec<Contract>,
    pub pruned: Vec<Contract>,
    pub envelope_rendered: Option<String>,
    pub status: RunStatus,
    pub issue: IssueCategory,
    pub note: String,
}

/// Run full pipeline for one target file. Returns Ok(RunResult) or Err on read/early failure.
fn run_one(
    path: &str,
    crate_root: &Path,
    extractor: &TreeSitterExtractor,
) -> Result<RunResult, String> {
    let target_path = Path::new(path);
    let target_contents = fs::read_to_string(target_path).map_err(|e| {
        format!("Failed to read {}: {}", path, e)
    })?;

    let extracted = extractor.extract(path, &target_contents);
    let import_refs = parse_imports(&extracted.imports);
    let mut resolved = resolve_import_refs(crate_root, &import_refs);
    let expanded = expand_grouped_submodules(crate_root, &import_refs);
    for p in expanded {
        if !resolved.iter().any(|q| q == &p) {
            resolved.push(p);
        }
    }
    let re_exported = re_export_resolve(crate_root, &resolved);
    let all_deps: Vec<_> = resolved
        .iter()
        .chain(re_exported.iter())
        .cloned()
        .collect();

    let mut dep_contracts: Vec<Contract> = Vec::new();
    for res_path in &all_deps {
        let contents = match fs::read_to_string(res_path) {
            Ok(c) => c,
            Err(_) => continue,
        };
        let ex = extractor.extract(&res_path.to_string_lossy(), &contents);
        dep_contracts.extend(ex.contracts);
    }

    let pruned = slice_contracts(&target_contents, dep_contracts.clone());

    let envelope = SystemEnvelope::new(
        path,
        &target_contents,
        pruned.clone(),
        extracted.confidence,
        &all_deps,
    );
    let rendered = envelope.render_xml();

    Ok(RunResult {
        path: path.to_string(),
        crate_root: display_path(crate_root),
        raw_imports: extracted.imports.clone(),
        import_refs,
        resolved,
        re_exported,
        target_contracts: extracted.contracts.clone(),
        target_confidence: extracted.confidence,
        dep_contracts_unpruned: dep_contracts,
        pruned,
        envelope_rendered: Some(rendered),
        status: RunStatus::Success,
        issue: IssueCategory::None,
        note: String::new(),
    })
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();

    // Gauntlet mode: 3+ args, first is directory → crate root + list of target files.
    let (gauntlet_mode, crate_root_opt, target_files): (bool, Option<String>, Vec<String>) = {
        if args.len() >= 3 {
            let first = &args[0];
            let p = Path::new(first);
            if p.is_dir() {
                (true, Some(first.clone()), args[1..].to_vec())
            } else {
                (false, None, args.to_vec())
            }
        } else {
            (false, None, args.to_vec())
        }
    };

    if gauntlet_mode {
        run_gauntlet(crate_root_opt.as_deref().unwrap(), &target_files);
        return;
    }

    // Single-file mode: 1 arg = file (crate root = parent), 2 args = file + crate root.
    let path = target_files.first().map(String::as_str);
    let path = match path {
        Some(p) if !p.is_empty() => p.to_string(),
        _ => {
            let default = "fixtures/basic_crate/src/lib.rs";
            if Path::new(default).exists() {
                default.to_string()
            } else {
                let home = env::var("USERPROFILE").unwrap_or_else(|_| ".".into());
                let wp = Path::new(&home)
                    .join("Documents")
                    .join("Application_Dev")
                    .join("IDE")
                    .join("wire_proof")
                    .join("src")
                    .join("main.rs");
                if wp.exists() {
                    wp.to_string_lossy().into_owned()
                } else {
                    eprintln!("Usage: context_mapper_lab <path-to-rust-file> [crate-root-dir]");
                    eprintln!("   or: context_mapper_lab <crate-root-dir> <file1> <file2> ...  (gauntlet)");
                    eprintln!("Example: context_mapper_lab fixtures/basic_crate/src/lib.rs");
                    eprintln!("Example (gauntlet): context_mapper_lab ../src-tauri/src ../src-tauri/src/command/parser.rs ../src-tauri/src/command/executor.rs");
                    std::process::exit(1);
                }
            }
        }
    };

    let crate_root_arg = args.get(1).cloned();

    let target_path = Path::new(&path);
    let crate_root: &Path = match &crate_root_arg {
        Some(cr) => Path::new(cr),
        None => target_path.parent().unwrap_or_else(|| Path::new(".")),
    };

    let extractor = TreeSitterExtractor::new();
    let result = match run_one(&path, crate_root, &extractor) {
        Ok(r) => r,
        Err(e) => {
            eprintln!("{}", e);
            std::process::exit(1);
        }
    };

    println!("===================================================");
    println!("  CONTEXT MAPPER LAB — Phase 1F (deps + slicer)      ");
    println!("===================================================\n");

    println!("Target file: {}", result.path);
    println!("Crate root:  {}", result.crate_root);
    println!("\n--- Raw Imports ---");
    if result.raw_imports.is_empty() {
        println!("  (none)");
    } else {
        for u in &result.raw_imports {
            println!("  {}", u);
        }
    }
    println!("\n--- Normalized Imports ---");
    print_import_refs(&result.import_refs);
    println!("\n--- Resolved Local Files ---");
    if result.resolved.is_empty() {
        println!("  (none)");
    } else {
        for p in &result.resolved {
            println!("  {}", display_path(p));
        }
    }
    println!("\n--- Re-export Resolved Files ---");
    if result.re_exported.is_empty() {
        println!("  (none)");
    } else {
        for p in &result.re_exported {
            println!("  {}", display_path(p));
        }
    }
    println!("\n--- Target Contracts ---");
    println!("  File: {} | confidence: {:?}", result.path, result.target_confidence);
    print_contract_list(&result.target_contracts);
    println!("\n--- Dependency Contracts (Unpruned) ---");
    print_contract_list(&result.dep_contracts_unpruned);
    println!("\n--- Pruned Dependency Contracts ---");
    print_contract_list(&result.pruned);

    if let Some(ref rendered) = result.envelope_rendered {
        println!("\n--- Rendered System Envelope ---");
        println!("{}", rendered);
    }

    println!("===================================================");
    println!("  Strike 1 Phase 1H — import normalization + envelope");
    println!("===================================================");
}

fn run_gauntlet(crate_root: &str, target_files: &[String]) {
    println!("===================================================");
    println!("  CONTEXT MAPPER LAB — Phase 1L Gauntlet             ");
    println!("===================================================\n");
    println!("Crate root: {}", crate_root);
    println!("Files: {}", target_files.len());

    let extractor = TreeSitterExtractor::new();
    let crate_root_path = Path::new(crate_root);
    let mut rows: Vec<(String, RunStatus, IssueCategory, String)> = Vec::new();
    let mut first_success_envelope: Option<String> = None;

    for (i, path) in target_files.iter().enumerate() {
        println!("\n========== File {}: {} ==========", i + 1, path);

        match run_one(path, crate_root_path, &extractor) {
            Ok(r) => {
                println!("  Crate root:  {}", r.crate_root);
                println!("  Raw imports: {}", r.raw_imports.len());
                if !r.raw_imports.is_empty() {
                    for u in &r.raw_imports {
                        println!("    {}", u);
                    }
                }
                println!("  Normalized imports: {}", r.import_refs.len());
                for ref r in &r.import_refs {
                    let local = if r.is_local { "local" } else { "external" };
                    let syms = if r.imported_symbols.is_empty() { "*".to_string() } else { r.imported_symbols.join(", ") };
                    println!("    {} | {} | {}", r.normalized, local, syms);
                }
                println!("  Resolved local files: {}", r.resolved.len());
                for p in &r.resolved {
                    println!("    {}", display_path(p));
                }
                println!("  Re-export resolved: {}", r.re_exported.len());
                for p in &r.re_exported {
                    println!("    {}", display_path(p));
                }
                println!("  Pruned contracts: {}", r.pruned.len());
                for c in &r.pruned {
                    println!("    [{}] {}", c.kind, c.name);
                }
                let ok = r.envelope_rendered.is_some();
                println!("  Envelope rendered: {}", if ok { "yes" } else { "no" });

                if first_success_envelope.is_none() && r.envelope_rendered.is_some() {
                    first_success_envelope = r.envelope_rendered.clone();
                }

                rows.push((
                    path.clone(),
                    r.status,
                    r.issue,
                    r.note.clone(),
                ));
            }
            Err(e) => {
                println!("  FAILED: {}", e);
                rows.push((
                    path.clone(),
                    RunStatus::Failed,
                    IssueCategory::None,
                    e.clone(),
                ));
            }
        }
    }

    println!("\n===================================================");
    println!("  GAUNTLET SUMMARY");
    println!("===================================================");
    println!("{:<55} | {:<10} | {:<28} | note", "file", "status", "issue category");
    println!("{}", "-".repeat(120));
    for (path, status, issue, note) in &rows {
        let status_str = match status {
            RunStatus::Success => "success",
            RunStatus::Partial => "partial",
            RunStatus::Failed => "failed",
        };
        let issue_str = match issue {
            IssueCategory::None => "—",
            IssueCategory::ExtractorLimitation => "extractor limitation",
            IssueCategory::ImportNormalizationLimitation => "import normalization",
            IssueCategory::ResolverLimitation => "resolver limitation",
            IssueCategory::ReExportLimitation => "re-export limitation",
            IssueCategory::SlicerLimitation => "slicer limitation",
            IssueCategory::EnvelopeRenderingIssue => "envelope rendering",
        };
        let short = if note.len() > 40 { format!("{}...", &note[..37]) } else { note.clone() };
        println!("{:<55} | {:<10} | {:<28} | {}", path, status_str, issue_str, short);
    }

    if let Some(env) = first_success_envelope {
        println!("\n===================================================");
        println!("  ONE REPRESENTATIVE ENVELOPE (first success)");
        println!("===================================================\n");
        println!("{}", env);
    }

    println!("===================================================");
    println!("  Strike 1 Phase 1L — real-file gauntlet complete");
    println!("===================================================");
}

fn print_import_refs(refs: &[ImportRef]) {
    if refs.is_empty() {
        println!("  (none)");
        return;
    }
    for r in refs {
        let local = if r.is_local { "local" } else { "external" };
        let symbols = if r.is_glob {
            "*".to_string()
        } else {
            r.imported_symbols.join(", ")
        };
        println!("  {} | {} | {}", r.normalized, local, symbols);
        if let Some(ref a) = r.alias {
            println!("      alias: {}", a);
        }
    }
}

#[allow(dead_code)]
fn print_contracts(e: &ExtractedFile) {
    println!("  File: {} | confidence: {:?}", e.path, e.confidence);
    if e.contracts.is_empty() {
        println!("  (none)");
    } else {
        for c in &e.contracts {
            println!("  [{}] {}", c.kind, c.name);
            if let Some(ref sig) = c.signature {
                println!("      {}", sig);
            }
        }
    }
}

fn print_contract_list(contracts: &[Contract]) {
    if contracts.is_empty() {
        println!("  (none)");
    } else {
        for c in contracts {
            println!("  [{}] {}", c.kind, c.name);
            if let Some(ref sig) = c.signature {
                println!("      {}", sig);
            }
        }
    }
}
