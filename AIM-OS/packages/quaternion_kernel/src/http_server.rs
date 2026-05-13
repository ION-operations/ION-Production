//! HTTP Server for Quaternion Kernel
//!
//! Provides REST API for kernel syscalls (place, move, sense, emit)
//! Phase 1: Real System Integration

use axum::{
    extract::State,
    http::StatusCode,
    response::Json,
    routing::post,
    Router,
};
use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};

use crate::kernel::{Kernel, EntityId, EntityState};
use crate::{QAddr, DualQuat, Quat, Vec4, CompositeKey, MortonKey, S3Bin, PrincipalShell, OrbitalClass, Spin};
use std::str::FromStr;

/// Shared kernel state
type KernelState = Arc<Mutex<Kernel>>;

/// Request/Response types for HTTP API

#[derive(Debug, Deserialize)]
pub struct QAddrRequest {
    pub n: u8,
    pub l: String,
    pub m: u16,
    pub s: String,
    pub morton_key: u64,
    pub s3_bin: u16,
}

impl From<QAddrRequest> for QAddr {
    fn from(req: QAddrRequest) -> Self {
        QAddr {
            n: PrincipalShell(req.n),
            l: match req.l.as_str() {
                "memory" => OrbitalClass::Memory,
                "io" => OrbitalClass::Io,
                "network" => OrbitalClass::Network,
                "compute" => OrbitalClass::Compute,
                "governance" => OrbitalClass::Governance,
                _ => OrbitalClass::Memory,
            },
            m: S3Bin(req.m),
            s: match req.s.as_str() {
                "plan" => Spin::Plan,
                "act" => Spin::Act,
                "read" => Spin::Read,
                "write" => Spin::Write,
                _ => Spin::Plan,
            },
            morton_key: MortonKey(req.morton_key),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct QAddrResponse {
    pub n: u8,
    pub l: String,
    pub m: u16,
    pub s: String,
    pub morton_key: u64,
    pub s3_bin: u16,
}

impl From<QAddr> for QAddrResponse {
    fn from(addr: QAddr) -> Self {
        QAddrResponse {
            n: addr.n.0,
            l: match addr.l {
                OrbitalClass::Memory => "memory".to_string(),
                OrbitalClass::Io => "io".to_string(),
                OrbitalClass::Network => "network".to_string(),
                OrbitalClass::Compute => "compute".to_string(),
                OrbitalClass::Governance => "governance".to_string(),
            },
            m: addr.m.0,
            s: match addr.s {
                Spin::Plan => "plan".to_string(),
                Spin::Act => "act".to_string(),
                Spin::Read => "read".to_string(),
                Spin::Write => "write".to_string(),
            },
            morton_key: addr.morton_key.0,
            s3_bin: addr.m.0,
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct QuatRequest {
    pub w: f32,
    pub x: f32,
    pub y: f32,
    pub z: f32,
}

impl From<QuatRequest> for Quat {
    fn from(req: QuatRequest) -> Self {
        Quat {
            w: req.w,
            x: req.x,
            y: req.y,
            z: req.z,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct QuatResponse {
    pub w: f32,
    pub x: f32,
    pub y: f32,
    pub z: f32,
}

impl From<Quat> for QuatResponse {
    fn from(q: Quat) -> Self {
        QuatResponse {
            w: q.w,
            x: q.x,
            y: q.y,
            z: q.z,
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct DualQuatRequest {
    pub rotation: QuatRequest,
    pub translation: QuatRequest,
}

impl From<DualQuatRequest> for DualQuat {
    fn from(req: DualQuatRequest) -> Self {
        DualQuat {
            rotation: req.rotation.into(),
            translation: req.translation.into(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct DualQuatResponse {
    pub rotation: QuatResponse,
    pub translation: QuatResponse,
}

impl From<DualQuat> for DualQuatResponse {
    fn from(dq: DualQuat) -> Self {
        DualQuatResponse {
            rotation: dq.rotation.into(),
            translation: dq.translation.into(),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct EntityStateRequest {
    pub qaddr: QAddrRequest,
    pub pose: DualQuatRequest,
}

impl From<EntityStateRequest> for EntityState {
    fn from(req: EntityStateRequest) -> Self {
        EntityState {
            addr: req.qaddr.into(),
            pose: req.pose.into(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct EntityStateResponse {
    pub qaddr: QAddrResponse,
    pub pose: DualQuatResponse,
}

impl From<EntityState> for EntityStateResponse {
    fn from(state: EntityState) -> Self {
        EntityStateResponse {
            qaddr: state.addr.into(),
            pose: state.pose.into(),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct PlaceRequest {
    pub actor_qaddr: QAddrRequest,
    pub entity_id: String, // UUID as string
    pub entity_state: EntityStateRequest,
}

#[derive(Debug, Serialize)]
pub struct SelectionRulesResponse {
    pub delta_n: i8,
    pub delta_l: bool,
    pub delta_m: bool,
    pub delta_s: bool,
    pub ok: bool,
}

#[derive(Debug, Serialize)]
pub struct PlaceResponse {
    pub success: bool,
    pub entity_id: String,
    pub qaddr: QAddrResponse,
    pub selection_rules: SelectionRulesResponse,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct MoveRequest {
    pub actor_qaddr: QAddrRequest,
    pub entity_id: String,
    pub delta_pose: DualQuatRequest,
    pub current_time: f32,
}

#[derive(Debug, Serialize)]
pub struct MoveResponse {
    pub success: bool,
    pub entity_id: String,
    pub new_qaddr: QAddrResponse,
    pub new_pose: DualQuatResponse,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct RegionRequest {
    pub center: Vec4Request,
    pub radius: f32,
}

#[derive(Debug, Deserialize)]
pub struct Vec4Request {
    pub x: f32,
    pub y: f32,
    pub z: f32,
    pub tau: f32,
}

#[derive(Debug, Deserialize)]
pub struct SenseRequest {
    pub actor_qaddr: QAddrRequest,
    pub region: RegionRequest,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub filters: Option<SenseFilters>,
}

#[derive(Debug, Deserialize)]
pub struct SenseFilters {
    pub orbital_class: Option<String>,
    pub min_n: Option<u8>,
    pub max_n: Option<u8>,
}

#[derive(Debug, Serialize)]
pub struct EntityResult {
    pub entity_id: String,
    pub qaddr: QAddrResponse,
    pub pose: DualQuatResponse,
    pub distance: f32,
}

#[derive(Debug, Serialize)]
pub struct SenseResponse {
    pub success: bool,
    pub entities: Vec<EntityResult>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct EmitRequest {
    pub actor_qaddr: QAddrRequest,
    pub event: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub field_deltas: Option<FieldDeltas>,
}

#[derive(Debug, Deserialize)]
pub struct FieldDeltas {
    pub kappa: f32,
    pub lambda: f32,
    pub rho: f32,
}

#[derive(Debug, Serialize)]
pub struct EmitResponse {
    pub success: bool,
    pub event: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

/// Handler functions

async fn handle_place(
    State(kernel): State<KernelState>,
    Json(request): Json<PlaceRequest>,
) -> Result<Json<PlaceResponse>, StatusCode> {
    let mut kernel = kernel.lock().unwrap();
    
    // Parse entity_id (UUID string to u128)
    let entity_id = parse_entity_id(&request.entity_id)
        .map_err(|_| StatusCode::BAD_REQUEST)?;
    
    let actor_qaddr: QAddr = request.actor_qaddr.into();
    let entity_state: EntityState = request.entity_state.into();
    
    match kernel.place(&actor_qaddr, entity_id, entity_state) {
        Ok(()) => {
            Ok(Json(PlaceResponse {
                success: true,
                entity_id: request.entity_id,
                qaddr: entity_state.addr.into(),
                selection_rules: SelectionRulesResponse {
                    delta_n: 0,
                    delta_l: true,
                    delta_m: true,
                    delta_s: true,
                    ok: true,
                },
                error: None,
            }))
        }
        Err(e) => {
            Ok(Json(PlaceResponse {
                success: false,
                entity_id: request.entity_id,
                qaddr: entity_state.addr.into(),
                selection_rules: SelectionRulesResponse {
                    delta_n: 0,
                    delta_l: false,
                    delta_m: false,
                    delta_s: false,
                    ok: false,
                },
                error: Some(e.to_string()),
            }))
        }
    }
}

async fn handle_move(
    State(kernel): State<KernelState>,
    Json(request): Json<MoveRequest>,
) -> Result<Json<MoveResponse>, StatusCode> {
    let mut kernel = kernel.lock().unwrap();
    
    let entity_id = parse_entity_id(&request.entity_id)
        .map_err(|_| StatusCode::BAD_REQUEST)?;
    
    let actor_qaddr: QAddr = request.actor_qaddr.into();
    let delta_pose: DualQuat = request.delta_pose.into();
    
    match kernel.move_entity(&actor_qaddr, entity_id, delta_pose, request.current_time) {
        Ok(()) => {
            // Retrieve updated entity state
            let entity_state = kernel.entities.get(&entity_id)
                .ok_or(StatusCode::INTERNAL_SERVER_ERROR)?;
            
            Ok(Json(MoveResponse {
                success: true,
                entity_id: request.entity_id,
                new_qaddr: entity_state.addr.into(),
                new_pose: entity_state.pose.into(),
                error: None,
            }))
        }
        Err(e) => {
            Ok(Json(MoveResponse {
                success: false,
                entity_id: request.entity_id,
                new_qaddr: QAddrResponse {
                    n: 0,
                    l: "memory".to_string(),
                    m: 0,
                    s: "plan".to_string(),
                    morton_key: 0,
                    s3_bin: 0,
                },
                new_pose: DualQuatResponse {
                    rotation: QuatResponse { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
                    translation: QuatResponse { w: 0.0, x: 0.0, y: 0.0, z: 0.0 },
                },
                error: Some(e.to_string()),
            }))
        }
    }
}

async fn handle_sense(
    State(kernel): State<KernelState>,
    Json(request): Json<SenseRequest>,
) -> Result<Json<SenseResponse>, StatusCode> {
    let kernel = kernel.lock().unwrap();
    
    let actor_qaddr: QAddr = request.actor_qaddr.into();
    
    // Convert region to kernel types
    let center = Vec4 {
        x: request.region.center.x,
        y: request.region.center.y,
        z: request.region.center.z,
        tau: request.region.center.tau,
    };
    
    // Calculate region key from center (simplified - use center as key)
    let morton_key = crate::morton4d_encode(
        (center.x * 1000.0) as i32,
        (center.y * 1000.0) as i32,
        (center.z * 1000.0) as i32,
        (center.tau * 1000.0) as i32,
    );
    let region_key = CompositeKey::new(morton_key, S3Bin(0)); // Simplified: use identity orientation
    
    let filter_l = request.filters.as_ref()
        .and_then(|f| f.orbital_class.as_ref())
        .and_then(|s| match s.as_str() {
            "memory" => Some(OrbitalClass::Memory),
            "io" => Some(OrbitalClass::Io),
            "network" => Some(OrbitalClass::Network),
            "compute" => Some(OrbitalClass::Compute),
            "governance" => Some(OrbitalClass::Governance),
            _ => None,
        });
    
    match kernel.sense(&actor_qaddr, region_key, filter_l) {
        Ok(entity_ids) => {
            let mut entities = Vec::new();
            
            for entity_id in entity_ids {
                if let Some(entity_state) = kernel.entities.get(&entity_id) {
                    // Calculate distance (simplified)
                    let distance = calculate_distance(&center, &entity_state.pose);
                    
                    entities.push(EntityResult {
                        entity_id: format_entity_id(entity_id),
                        qaddr: entity_state.addr.into(),
                        pose: entity_state.pose.into(),
                        distance,
                    });
                }
            }
            
            Ok(Json(SenseResponse {
                success: true,
                entities,
                error: None,
            }))
        }
        Err(e) => {
            Ok(Json(SenseResponse {
                success: false,
                entities: Vec::new(),
                error: Some(e.to_string()),
            }))
        }
    }
}

async fn handle_emit(
    State(kernel): State<KernelState>,
    Json(request): Json<EmitRequest>,
) -> Result<Json<EmitResponse>, StatusCode> {
    let mut kernel = kernel.lock().unwrap();
    
    let actor_qaddr: QAddr = request.actor_qaddr.into();
    
    match kernel.emit(&actor_qaddr) {
        Ok(()) => {
            Ok(Json(EmitResponse {
                success: true,
                event: request.event,
                error: None,
            }))
        }
        Err(e) => {
            Ok(Json(EmitResponse {
                success: false,
                event: request.event,
                error: Some(e.to_string()),
            }))
        }
    }
}

/// Helper functions

fn parse_entity_id(id_str: &str) -> Result<EntityId, ()> {
    // Simple UUID parsing (first 16 hex chars as u128)
    // In production, use proper UUID parsing
    if id_str.len() >= 32 {
        let hex_str = &id_str[..32];
        u128::from_str_radix(hex_str, 16).map_err(|_| ())
    } else {
        // Fallback: hash the string
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        let mut hasher = DefaultHasher::new();
        id_str.hash(&mut hasher);
        Ok(hasher.finish())
    }
}

impl From<Vec4Request> for Vec4 {
    fn from(req: Vec4Request) -> Self {
        Vec4 {
            x: req.x,
            y: req.y,
            z: req.z,
            tau: req.tau,
        }
    }
}

fn format_entity_id(id: EntityId) -> String {
    format!("{:032x}", id)
}

fn calculate_distance(center: &Vec4, pose: &DualQuat) -> f32 {
    // Extract position from dual quaternion
    // Simplified: use translation quaternion as position
    let dx = pose.translation.x - center.x;
    let dy = pose.translation.y - center.y;
    let dz = pose.translation.z - center.z;
    (dx * dx + dy * dy + dz * dz).sqrt()
}

/// Create router with all endpoints

pub fn create_router(kernel: KernelState) -> Router {
    Router::new()
        .route("/syscall/place", post(handle_place))
        .route("/syscall/move", post(handle_move))
        .route("/syscall/sense", post(handle_sense))
        .route("/syscall/emit", post(handle_emit))
        .with_state(kernel)
        .layer(tower_http::cors::CorsLayer::permissive())
}

/// Start HTTP server

pub async fn start_server(port: u16) -> Result<(), Box<dyn std::error::Error>> {
    let kernel = Arc::new(Mutex::new(Kernel::new()));
    let app = create_router(kernel);
    
    let listener = tokio::net::TcpListener::bind(format!("0.0.0.0:{}", port)).await?;
    
    println!("Quaternion Kernel HTTP Server listening on port {}", port);
    
    axum::serve(listener, app).await?;
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_qaddr_conversion() {
        let req = QAddrRequest {
            n: 1,
            l: "io".to_string(),
            m: 1234,
            s: "act".to_string(),
            morton_key: 1234567890,
            s3_bin: 5678,
        };
        
        let qaddr: QAddr = req.into();
        assert_eq!(qaddr.n.0, 1);
        assert_eq!(qaddr.m.0, 1234);
    }
    
    #[test]
    fn test_parse_entity_id() {
        let id = parse_entity_id("1234567890abcdef1234567890abcdef").unwrap();
        assert!(id > 0);
    }
}

