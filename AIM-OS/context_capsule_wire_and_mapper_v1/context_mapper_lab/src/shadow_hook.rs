//! Passive Shadow BCI hook (reference implementation for Lane B).
//!
//! This hook is intentionally:
//! - off by default (`AIMOS_SHADOW_BCI_PASSIVE_EMIT`)
//! - observational only (writes adapter snapshot + emits shadow records)
//! - fail-open (errors are returned to caller for logging, never hard-fail path)

use crate::types::{Contract, ExtractedFile, ParseConfidence};
use serde::Serialize;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{Instant, SystemTime, UNIX_EPOCH};

const FLAG_PASSIVE_EMIT: &str = "AIMOS_SHADOW_BCI_PASSIVE_EMIT";
const ENV_SHADOW_ROOT: &str = "AIMOS_SHADOW_BCI_ROOT";
const ENV_OUT_DIR: &str = "AIMOS_SHADOW_BCI_OUT_DIR";
const ENV_PYTHON_BIN: &str = "AIMOS_SHADOW_BCI_PYTHON";
const ENV_EMITTER_PATH: &str = "AIMOS_SHADOW_BCI_EMITTER";
const ENV_SCHEMA_PATH: &str = "AIMOS_SHADOW_BCI_SCHEMA";

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PassiveEmitOutcome {
    Disabled,
    Emitted {
        snapshot_path: PathBuf,
        elapsed_ms: u128,
    },
    Failed {
        error: String,
    },
}

#[derive(Debug, Serialize)]
struct AdapterFixture<'a> {
    source_path: &'a str,
    source_text: &'a str,
    imports: &'a [String],
    contracts: Vec<AdapterContract<'a>>,
    parse_confidence: &'a str,
    resolved_dependencies: Vec<String>,
}

#[derive(Debug, Serialize)]
struct AdapterContract<'a> {
    kind: &'a str,
    name: &'a str,
    signature: Option<&'a str>,
}

pub fn maybe_emit_passive_shadow(
    source_text: &str,
    extracted: &ExtractedFile,
    resolved_paths: &[PathBuf],
) -> PassiveEmitOutcome {
    if !is_passive_emit_enabled() {
        return PassiveEmitOutcome::Disabled;
    }

    let start = Instant::now();
    eprintln!(
        "[shadow_emit_attempt] source_path={} import_count={} contract_count={}",
        extracted.path,
        extracted.imports.len(),
        extracted.contracts.len()
    );

    match emit_shadow_records(source_text, extracted, resolved_paths) {
        Ok(snapshot_path) => {
            let elapsed_ms = start.elapsed().as_millis();
            eprintln!(
                "[shadow_emit_success] source_path={} snapshot_path={} elapsed_ms={}",
                extracted.path,
                snapshot_path.display(),
                elapsed_ms
            );
            PassiveEmitOutcome::Emitted {
                snapshot_path,
                elapsed_ms,
            }
        }
        Err(error) => {
            eprintln!(
                "[shadow_emit_failure] source_path={} error_class=PassiveShadowHook error_message={}",
                extracted.path, error
            );
            PassiveEmitOutcome::Failed { error }
        }
    }
}

fn emit_shadow_records(
    source_text: &str,
    extracted: &ExtractedFile,
    resolved_paths: &[PathBuf],
) -> Result<PathBuf, String> {
    let root = shadow_root_dir();
    let out_dir = shadow_out_dir(&root);
    fs::create_dir_all(&out_dir).map_err(|e| format!("create out dir failed: {e}"))?;

    let snapshot_path = out_dir.join(format!("live_mapper_snapshot_{}.json", now_unix_ms()?));
    let fixture = build_adapter_fixture(source_text, extracted, resolved_paths);
    let payload = serde_json::to_string_pretty(&fixture)
        .map_err(|e| format!("serialize adapter fixture failed: {e}"))?;
    fs::write(&snapshot_path, payload).map_err(|e| format!("write fixture failed: {e}"))?;

    run_python_emitter(&root, &out_dir, &snapshot_path)?;
    Ok(snapshot_path)
}

fn run_python_emitter(root: &Path, out_dir: &Path, snapshot_path: &Path) -> Result<(), String> {
    let python = env::var(ENV_PYTHON_BIN).unwrap_or_else(|_| "python".to_string());
    let emitter_path =
        env_path_or_default(ENV_EMITTER_PATH, root.join("shadow_bci_v1_emitter.py"));
    let schema_path = env_path_or_default(ENV_SCHEMA_PATH, root.join("shadow_bci_v1_schema.json"));

    let output = Command::new(&python)
        .arg(&emitter_path)
        .arg("--fixture")
        .arg(snapshot_path)
        .arg("--schema")
        .arg(&schema_path)
        .arg("--out-dir")
        .arg(out_dir)
        .output()
        .map_err(|e| format!("spawn emitter failed: {e}"))?;

    if output.status.success() {
        return Ok(());
    }

    let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    Err(format!(
        "emitter exited with status {:?}; stderr='{}'; stdout='{}'",
        output.status.code(),
        stderr,
        stdout
    ))
}

fn shadow_root_dir() -> PathBuf {
    env_path_or_default(ENV_SHADOW_ROOT, PathBuf::from("../shadow_sync"))
}

fn shadow_out_dir(root: &Path) -> PathBuf {
    env::var(ENV_OUT_DIR)
        .map(PathBuf::from)
        .unwrap_or_else(|_| root.join("out"))
}

fn env_path_or_default(name: &str, default: PathBuf) -> PathBuf {
    env::var(name).map(PathBuf::from).unwrap_or(default)
}

fn is_passive_emit_enabled() -> bool {
    match env::var(FLAG_PASSIVE_EMIT) {
        Ok(raw) => is_truthy(&raw),
        Err(_) => false,
    }
}

fn is_truthy(raw: &str) -> bool {
    matches!(raw.trim().to_ascii_lowercase().as_str(), "1" | "true")
}

fn parse_confidence_label(confidence: ParseConfidence) -> &'static str {
    match confidence {
        ParseConfidence::High => "High",
        ParseConfidence::Degraded => "Degraded",
        ParseConfidence::Fallback => "Fallback",
    }
}

fn build_adapter_fixture<'a>(
    source_text: &'a str,
    extracted: &'a ExtractedFile,
    resolved_paths: &[PathBuf],
) -> AdapterFixture<'a> {
    AdapterFixture {
        source_path: &extracted.path,
        source_text,
        imports: &extracted.imports,
        contracts: extracted
            .contracts
            .iter()
            .map(|c: &Contract| AdapterContract {
                kind: &c.kind,
                name: &c.name,
                signature: c.signature.as_deref(),
            })
            .collect(),
        parse_confidence: parse_confidence_label(extracted.confidence),
        resolved_dependencies: resolved_paths
            .iter()
            .map(|p| p.to_string_lossy().to_string())
            .collect(),
    }
}

fn now_unix_ms() -> Result<u128, String> {
    let duration = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| format!("system time error: {e}"))?;
    Ok(duration.as_millis())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::ExtractedFile;
    use std::fs;

    struct EnvGuard {
        key: &'static str,
        original: Option<String>,
    }

    impl EnvGuard {
        fn set(key: &'static str, value: &str) -> Self {
            let original = env::var(key).ok();
            env::set_var(key, value);
            Self { key, original }
        }
    }

    impl Drop for EnvGuard {
        fn drop(&mut self) {
            if let Some(ref value) = self.original {
                env::set_var(self.key, value);
            } else {
                env::remove_var(self.key);
            }
        }
    }

    fn sample_extracted() -> ExtractedFile {
        ExtractedFile {
            path: "src/lib.rs".to_string(),
            imports: vec!["use crate::foo::Bar;".to_string()],
            contracts: vec![Contract {
                kind: "fn".to_string(),
                name: "do_work".to_string(),
                signature: Some("pub fn do_work()".to_string()),
            }],
            confidence: ParseConfidence::High,
        }
    }

    #[test]
    fn truthy_parser_accepts_only_true_or_one() {
        assert!(is_truthy("true"));
        assert!(is_truthy("TRUE"));
        assert!(is_truthy("1"));
        assert!(!is_truthy("false"));
        assert!(!is_truthy("0"));
        assert!(!is_truthy(""));
    }

    #[test]
    fn disabled_flag_short_circuits_hook() {
        let _guard = EnvGuard::set(FLAG_PASSIVE_EMIT, "0");
        let extracted = sample_extracted();
        let outcome = maybe_emit_passive_shadow("fn main(){}", &extracted, &[]);
        assert_eq!(outcome, PassiveEmitOutcome::Disabled);
    }

    #[test]
    fn fixture_maps_parse_confidence_and_dependencies() {
        let extracted = sample_extracted();
        let deps = vec![PathBuf::from("src/foo.rs"), PathBuf::from("src/bar.rs")];
        let fixture = build_adapter_fixture("fn main(){}", &extracted, &deps);
        assert_eq!(fixture.parse_confidence, "High");
        assert_eq!(fixture.resolved_dependencies.len(), 2);
        assert_eq!(fixture.contracts.len(), 1);
    }

    #[test]
    fn enabled_hook_returns_failed_on_missing_python_binary() {
        let _flag_guard = EnvGuard::set(FLAG_PASSIVE_EMIT, "true");
        let _python_guard = EnvGuard::set(ENV_PYTHON_BIN, "python_missing_for_hook_test");

        let temp_root = env::temp_dir().join(format!(
            "shadow_hook_test_{}",
            now_unix_ms().expect("timestamp generation should succeed")
        ));
        fs::create_dir_all(temp_root.join("out")).expect("temp out dir should be creatable");
        let _root_guard = EnvGuard::set(
            ENV_SHADOW_ROOT,
            temp_root
                .to_str()
                .expect("temp path should be representable as UTF-8"),
        );

        let extracted = sample_extracted();
        let outcome = maybe_emit_passive_shadow("fn main(){}", &extracted, &[]);
        match outcome {
            PassiveEmitOutcome::Failed { error } => {
                assert!(error.contains("spawn emitter failed"));
            }
            other => panic!("expected Failed outcome, got: {other:?}"),
        }
    }
}
