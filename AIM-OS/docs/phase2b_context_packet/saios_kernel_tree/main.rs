// SAIOS — Sovereign AI Operating System
// The Kernel Entry Point
// Full file: src-tauri/src/main.rs

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    saios_lib::run();
}
