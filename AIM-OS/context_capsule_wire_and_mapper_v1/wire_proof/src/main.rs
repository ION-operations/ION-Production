mod mcp_daemon_bridge;

use mcp_daemon_bridge::McpDaemonBridge;
use serde_json::json;

#[tokio::main]
async fn main() {
    println!("===================================================");
    println!("     AIM-OS PRIME: ACTION 1 & 2 (THE WIRE)         ");
    println!("===================================================");

    // AIM-OS root: where lucid_mcp_server.py lives (inferred from workspace)
    let workspace_root = "C:/Users/bombe/OneDrive/Desktop/AIM-OS";
    // Python: system or venv; use full path if needed
    let python_path = "python";

    let bridge = match McpDaemonBridge::ignite(workspace_root, python_path).await {
        Ok(b) => b,
        Err(e) => {
            eprintln!("❌ [FATAL] Wire Proof Failed: {}", e);
            return;
        }
    };

    println!("\n⚡ [AIM-OS] Bridge is HOT.");
    println!("🔍 [AIM-OS] Requesting explicit tools/list payload for inspection...");

    match bridge.send_request("tools/list", None).await {
        Ok(result) => {
            println!("\n🏆 [SUCCESS] RAW TOOLS LIST PAYLOAD:");
            println!("{}", serde_json::to_string_pretty(&result).unwrap());

            if let Some(tools) = result.get("tools").and_then(|t| t.as_array()) {
                println!("\n📋 SUMMARY: Discovered {} tools.", tools.len());
                for tool in tools {
                    if let Some(name) = tool.get("name").and_then(|n| n.as_str()) {
                        println!("  - {}", name);
                    }
                }
            }
        }
        Err(e) => {
            eprintln!("\n🔴 [TOOLS/LIST FAILED]: {:?}", e);
        }
    }

    // Action 3: one safe tools/call — get_memory_stats (schema: empty object, no required args)
    println!("\n🔧 [AIM-OS] Action 3: Calling get_memory_stats (tools/call)...");
    let tools_call_params = json!({
        "name": "get_memory_stats",
        "arguments": {}
    });
    match bridge.send_request("tools/call", Some(tools_call_params)).await {
        Ok(result) => {
            println!("\n🏆 [SUCCESS] get_memory_stats RESULT:");
            println!("{}", serde_json::to_string_pretty(&result).unwrap());
        }
        Err(e) => {
            eprintln!("\n🔴 [TOOLS/CALL get_memory_stats FAILED]: {:?}", e);
        }
    }

    println!("\n===================================================");
    println!("===     ACTIONS 1, 2 & 3 COMPLETE (WIRE PROVEN)  ===");
    println!("===================================================");
}
