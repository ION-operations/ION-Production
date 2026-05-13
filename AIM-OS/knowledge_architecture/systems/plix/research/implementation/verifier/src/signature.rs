//! Signature verification
//!
//! This module implements signature verification for evidence nodes:
//! - Ed25519 signature verification
//! - Quorum signature verification
//! - Public key management

use crate::types::EvidenceNode;
use ed25519_dalek::{PublicKey, Signature, Verifier};
use std::collections::HashMap;

/// Signature error
#[derive(Debug, thiserror::Error)]
pub enum SignatureError {
    #[error("Invalid signature for node: {node}")]
    InvalidSignature { node: String },
    
    #[error("Public key not found for signer: {signer}")]
    PublicKeyNotFound { signer: String },
    
    #[error("Invalid public key format: {0}")]
    InvalidPublicKey(String),
    
    #[error("Invalid signature format: {0}")]
    InvalidSignatureFormat(String),
    
    #[error("Quorum not met: required={required}, actual={actual}")]
    QuorumNotMet { required: usize, actual: usize },
    
    #[error("Ed25519 verification failed: {0}")]
    Ed25519Error(String),
}

/// Verify signature
///
/// Verifies the cryptographic signature on an evidence node
pub fn verify_signature(
    node: &EvidenceNode,
    public_key: &PublicKey,
) -> Result<(), SignatureError> {
    // Construct message to verify (same as what was signed)
    let message = construct_message(node);
    
    // Parse signature
    let signature = parse_signature(&node.sig)?;
    
    // Verify signature
    public_key
        .verify(message.as_bytes(), &signature)
        .map_err(|e| SignatureError::Ed25519Error(e.to_string()))?;
    
    Ok(())
}

/// Verify signature with trusted keys map
pub fn verify_signature_with_keys(
    node: &EvidenceNode,
    trusted_keys: &HashMap<String, PublicKey>,
) -> Result<(), SignatureError> {
    let public_key = trusted_keys
        .get(&node.signer)
        .ok_or_else(|| SignatureError::PublicKeyNotFound {
            signer: node.signer.clone(),
        })?;
    
    verify_signature(node, public_key)
}

/// Quorum signature configuration
#[derive(Debug, Clone)]
pub struct QuorumSignature {
    /// Required number of signatures
    pub threshold: usize,
    /// Signer IDs
    pub signers: Vec<String>,
    /// Signatures (parallel to signers)
    pub signatures: Vec<String>,
}

/// Verify quorum signature
pub fn verify_quorum_signature(
    node: &EvidenceNode,
    quorum: &QuorumSignature,
    trusted_keys: &HashMap<String, PublicKey>,
) -> Result<(), SignatureError> {
    let message = construct_message(node);
    let mut valid_signatures = 0;
    
    for (signer_id, sig_str) in quorum.signers.iter().zip(&quorum.signatures) {
        if let Some(public_key) = trusted_keys.get(signer_id) {
            if let Ok(signature) = parse_signature(sig_str) {
                if public_key.verify(message.as_bytes(), &signature).is_ok() {
                    valid_signatures += 1;
                }
            }
        }
    }
    
    if valid_signatures >= quorum.threshold {
        Ok(())
    } else {
        Err(SignatureError::QuorumNotMet {
            required: quorum.threshold,
            actual: valid_signatures,
        })
    }
}

/// Construct message for signature verification
fn construct_message(node: &EvidenceNode) -> String {
    format!(
        "{}:{}:{}:{}:{}",
        node.id,
        node.time.to_rfc3339(),
        node.tool,
        node.input_hash,
        node.output_hash
    )
}

/// Parse signature from hex string
fn parse_signature(sig_str: &str) -> Result<Signature, SignatureError> {
    // Simple hex parsing (in production, use proper encoding)
    if sig_str.len() != 128 {
        return Err(SignatureError::InvalidSignatureFormat(
            "Signature must be 128 hex characters (64 bytes)".to_string(),
        ));
    }
    
    let bytes = hex::decode(sig_str)
        .map_err(|e| SignatureError::InvalidSignatureFormat(e.to_string()))?;
    
    Signature::from_bytes(&bytes.try_into().map_err(|_| {
        SignatureError::InvalidSignatureFormat("Invalid signature length".to_string())
    })?)
    .map_err(|e| SignatureError::Ed25519Error(e.to_string()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use ed25519_dalek::{Keypair, Signer};
    use rand::rngs::OsRng;

    #[test]
    fn test_construct_message() {
        let node = EvidenceNode::new(
            "source".to_string(),
            None,
            None,
            "tool1".to_string(),
            "input_hash".to_string(),
            "output_hash".to_string(),
            None,
            Vec::new(),
            "signer1".to_string(),
            "sig1".to_string(),
        );
        
        let message = construct_message(&node);
        assert!(message.contains(&node.id));
        assert!(message.contains("tool1"));
    }

    #[test]
    fn test_verify_signature_valid() {
        let mut csprng = OsRng{};
        let keypair: Keypair = Keypair::generate(&mut csprng);
        
        let mut node = EvidenceNode::new(
            "source".to_string(),
            None,
            None,
            "tool1".to_string(),
            "input_hash".to_string(),
            "output_hash".to_string(),
            None,
            Vec::new(),
            "signer1".to_string(),
            "sig1".to_string(),
        );
        
        // Sign the message
        let message = construct_message(&node);
        let signature = keypair.sign(message.as_bytes());
        node.sig = hex::encode(signature.to_bytes());
        
        // Verify
        let result = verify_signature(&node, &keypair.public);
        assert!(result.is_ok());
    }

    #[test]
    fn test_verify_signature_invalid() {
        let mut csprng = OsRng{};
        let keypair1: Keypair = Keypair::generate(&mut csprng);
        let keypair2: Keypair = Keypair::generate(&mut csprng);
        
        let mut node = EvidenceNode::new(
            "source".to_string(),
            None,
            None,
            "tool1".to_string(),
            "input_hash".to_string(),
            "output_hash".to_string(),
            None,
            Vec::new(),
            "signer1".to_string(),
            "sig1".to_string(),
        );
        
        // Sign with keypair1
        let message = construct_message(&node);
        let signature = keypair1.sign(message.as_bytes());
        node.sig = hex::encode(signature.to_bytes());
        
        // Verify with keypair2 (should fail)
        let result = verify_signature(&node, &keypair2.public);
        assert!(result.is_err());
    }

    #[test]
    fn test_verify_quorum_signature() {
        let mut csprng = OsRng{};
        let keypair1: Keypair = Keypair::generate(&mut csprng);
        let keypair2: Keypair = Keypair::generate(&mut csprng);
        let keypair3: Keypair = Keypair::generate(&mut csprng);
        
        let node = EvidenceNode::new(
            "source".to_string(),
            None,
            None,
            "tool1".to_string(),
            "input_hash".to_string(),
            "output_hash".to_string(),
            None,
            Vec::new(),
            "signer1".to_string(),
            "sig1".to_string(),
        );
        
        let message = construct_message(&node);
        
        // Create quorum with 3 signers, threshold 2
        let quorum = QuorumSignature {
            threshold: 2,
            signers: vec![
                "signer1".to_string(),
                "signer2".to_string(),
                "signer3".to_string(),
            ],
            signatures: vec![
                hex::encode(keypair1.sign(message.as_bytes()).to_bytes()),
                hex::encode(keypair2.sign(message.as_bytes()).to_bytes()),
                hex::encode(keypair3.sign(message.as_bytes()).to_bytes()),
            ],
        };
        
        let mut trusted_keys = HashMap::new();
        trusted_keys.insert("signer1".to_string(), keypair1.public);
        trusted_keys.insert("signer2".to_string(), keypair2.public);
        trusted_keys.insert("signer3".to_string(), keypair3.public);
        
        let result = verify_quorum_signature(&node, &quorum, &trusted_keys);
        assert!(result.is_ok());
    }
}


