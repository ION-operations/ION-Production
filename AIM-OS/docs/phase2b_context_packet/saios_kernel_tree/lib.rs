// SAIOS — Library Root (excerpt: module declarations only)
// Full file: src-tauri/src/lib.rs

pub mod webview_manager;
pub mod injection;
pub mod extraction;
pub mod actuator;
pub mod command;
pub mod state_machine;
pub mod workspace;
pub mod evasion;
pub mod context_mapper;   // <-- Phase 2B: promoted mapper core

use tauri::Manager;
// ... ipc module, run(), etc.
