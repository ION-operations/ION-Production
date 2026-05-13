# Is `cc` required in the lab build?

Yes. The lab lists `cc = "1.0"` under `[build-dependencies]`. The crate does not define a custom `build.rs`; `tree-sitter-rust` brings its own build script that compiles the Rust grammar C code. That build script uses the `cc` crate to compile the native tree-sitter grammar. So when promoting into SAIOS, `cc` was added to `src-tauri`’s `[build-dependencies]` as well so that `tree-sitter-rust`’s build can succeed. Without it, the kernel build would fail when compiling `tree-sitter-rust`.
