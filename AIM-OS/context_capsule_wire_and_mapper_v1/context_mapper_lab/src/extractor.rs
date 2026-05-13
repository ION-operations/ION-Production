//! Strike 1 — First extractor backend: Tree-sitter for Rust.
//! One file in: extract use lines + top-level pub struct/enum/trait/fn/type/const.

use crate::types::{Contract, ContractExtractor, ExtractedFile, ParseConfidence};
use tree_sitter::{Node, Parser};

fn make_parser() -> Parser {
    let mut p = Parser::new();
    p.set_language(&tree_sitter_rust::LANGUAGE.into()).expect("load Rust grammar");
    p
}

/// Tree-sitter–based contract extractor for Rust.
pub struct TreeSitterExtractor;

impl TreeSitterExtractor {
    pub fn new() -> Self {
        Self
    }
}

impl Default for TreeSitterExtractor {
    fn default() -> Self {
        Self::new()
    }
}

impl ContractExtractor for TreeSitterExtractor {
    fn extract(&self, path: &str, contents: &str) -> ExtractedFile {
        let bytes = contents.as_bytes();
        let tree = match make_parser().parse(contents, None) {
            Some(t) => t,
            None => {
                return ExtractedFile {
                    path: path.to_string(),
                    imports: vec![],
                    contracts: vec![],
                    confidence: ParseConfidence::Fallback,
                };
            }
        };

        let root = tree.root_node();
        if root.has_error() {
            return ExtractedFile {
                path: path.to_string(),
                imports: vec![],
                contracts: vec![],
                confidence: ParseConfidence::Degraded,
            };
        }

        let mut imports = Vec::new();
        let mut contracts = Vec::new();

        for i in 0..root.child_count() {
            let node = root.child(i as u32).unwrap();
            match node.kind() {
                "use_declaration" => {
                    let text = node.utf8_text(bytes).unwrap_or_default();
                    if !text.is_empty() {
                        imports.push(text.trim().to_string());
                    }
                }
                "struct_item" | "enum_item" | "trait_item" | "function_item" | "type_item"
                | "const_item" => {
                    if !is_pub(&node, bytes) {
                        continue;
                    }
                    let preceding_attrs = collect_preceding_attributes(&root, i, bytes);
                    if let Some(c) = contract_from_node(&node, bytes, node.kind(), preceding_attrs) {
                        contracts.push(c);
                    }
                }
                _ => {}
            }
        }

        let confidence = if tree.root_node().has_error() {
            ParseConfidence::Degraded
        } else {
            ParseConfidence::High
        };

        ExtractedFile {
            path: path.to_string(),
            imports,
            contracts,
            confidence,
        }
    }
}

/// Collect text of consecutive attribute_item siblings immediately before child at index.
fn collect_preceding_attributes(root: &Node, child_index: usize, bytes: &[u8]) -> Option<String> {
    if child_index == 0 {
        return None;
    }
    let mut parts: Vec<String> = Vec::new();
    for j in (0..child_index).rev() {
        let sibling = root.child(j as u32)?;
        if sibling.kind() != "attribute_item" {
            break;
        }
        let text = sibling.utf8_text(bytes).unwrap_or_default().trim().to_string();
        if !text.is_empty() {
            parts.push(text);
        }
    }
    parts.reverse();
    if parts.is_empty() {
        None
    } else {
        Some(parts.join("\n"))
    }
}

fn is_pub(node: &Node, bytes: &[u8]) -> bool {
    for i in 0..node.child_count() {
        let c = node.child(i as u32).unwrap();
        if c.kind() == "visibility_modifier" {
            let t = c.utf8_text(bytes).unwrap_or_default();
            return t.trim() == "pub";
        }
    }
    false
}

fn contract_from_node(
    node: &Node,
    bytes: &[u8],
    kind: &str,
    preceding_attrs: Option<String>,
) -> Option<Contract> {
    let name = find_identifier_after_visibility(node, bytes)?;
    let mut signature = signature_snippet(node, bytes, kind);
    if let (Some(ref attrs), Some(ref mut sig)) = (preceding_attrs, &mut signature) {
        if !attrs.is_empty() {
            *sig = format!("{}\n{}", attrs.trim(), sig);
        }
    }
    Some(Contract {
        kind: kind.to_string(),
        name,
        signature,
    })
}

fn find_identifier_after_visibility(node: &Node, bytes: &[u8]) -> Option<String> {
    for i in 0..node.child_count() {
        let c = node.child(i as u32).unwrap();
        match c.kind() {
            "visibility_modifier" => continue,
            "identifier" => {
                let t = c.utf8_text(bytes).unwrap_or_default();
                return Some(t.to_string());
            }
            "type_identifier" => {
                let t = c.utf8_text(bytes).unwrap_or_default();
                return Some(t.to_string());
            }
            _ => {}
        }
    }
    None
}

fn signature_snippet(node: &Node, bytes: &[u8], kind: &str) -> Option<String> {
    match kind {
        "function_item" => {
            let end = body_start_byte(node)?;
            let start = node.start_byte();
            let slice = bytes.get(start..end).and_then(|s| std::str::from_utf8(s).ok())?;
            Some(slice.trim().to_string())
        }
        "struct_item" => {
            // Keep full struct (field layout); body_start_byte may be None so we get full node
            let end = body_start_byte(node).unwrap_or(node.end_byte());
            let start = node.start_byte();
            let slice = bytes.get(start..end).and_then(|s| std::str::from_utf8(s).ok())?;
            Some(slice.trim().to_string())
        }
        "enum_item" | "trait_item" => {
            // Include variant list / method signatures for LLM contract usefulness
            let start = node.start_byte();
            let end = node.end_byte();
            let slice = bytes.get(start..end).and_then(|s| std::str::from_utf8(s).ok())?;
            Some(slice.trim().to_string())
        }
        "type_item" | "const_item" => {
            let end = node.end_byte().min(node.start_byte() + 200);
            let start = node.start_byte();
            let slice = bytes.get(start..end).and_then(|s| std::str::from_utf8(s).ok())?;
            Some(slice.trim().to_string())
        }
        _ => None,
    }
}

fn body_start_byte(node: &Node) -> Option<usize> {
    for i in 0..node.child_count() {
        let c = node.child(i as u32).unwrap();
        if c.kind() == "block" || c.kind() == "declaration_list" || c.kind() == "enum_variant_list" {
            return Some(c.start_byte());
        }
    }
    None
}
