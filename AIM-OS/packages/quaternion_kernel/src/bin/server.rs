//! Main entry point for HTTP server
//!
//! Run with: cargo run --bin quaternion_kernel_server

use quaternion_kernel::http_server::start_server;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let port = std::env::var("PORT")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(8080);
    
    start_server(port).await
}

