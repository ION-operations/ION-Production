use dashmap::DashMap;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::process::Stdio;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::process::{ChildStdin, Command};
use tokio::sync::{oneshot, Mutex};
use std::time::Duration;

#[derive(Serialize)]
pub struct JsonRpcRequest {
    pub jsonrpc: String,
    pub method: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub params: Option<Value>,
    pub id: u64,
}

#[derive(Serialize)]
pub struct JsonRpcNotification {
    pub jsonrpc: String,
    pub method: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub params: Option<Value>,
}

#[derive(Deserialize, Debug)]
pub struct JsonRpcResponse {
    pub jsonrpc: Option<String>,
    pub id: Option<u64>,
    pub result: Option<Value>,
    pub error: Option<Value>,
}

#[derive(Debug, Clone)]
pub enum McpError {
    Timeout(String),
    DaemonDied,
    ToolError(String),
    ParseError(String),
    IoError(String),
}

pub struct McpDaemonBridge {
    stdin: Mutex<ChildStdin>,
    request_id_counter: AtomicU64,
    pending_requests: Arc<DashMap<u64, oneshot::Sender<Result<Value, McpError>>>>,
}

impl McpDaemonBridge {
    pub async fn ignite(workspace_root: &str, python_path: &str) -> Result<Arc<Self>, String> {
        println!("🧠 [AIM-OS] Igniting Python MCP Brain Stem using '{}'...", python_path);

        let mut child = Command::new(python_path)
            .arg("-u")
            .arg("lucid_mcp_server.py")
            .current_dir(workspace_root)
            .env("PYTHONPATH", workspace_root)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit())
            .spawn()
            .map_err(|e| format!("Fatal: Failed to boot MCP Daemon: {}", e))?;

        let stdin = child.stdin.take().unwrap();
        let stdout = child.stdout.take().unwrap();

        let pending_requests: Arc<DashMap<u64, oneshot::Sender<Result<Value, McpError>>>> =
            Arc::new(DashMap::new());
        let listener_pending = pending_requests.clone();
        let watcher_pending = pending_requests.clone();

        tokio::spawn(async move {
            let mut reader = BufReader::new(stdout);
            let mut line = String::new();
            while reader.read_line(&mut line).await.unwrap_or(0) > 0 {
                let trimmed = line.trim();
                if !trimmed.is_empty() {
                    if let Ok(response) = serde_json::from_str::<JsonRpcResponse>(trimmed) {
                        if let Some(id) = response.id {
                            if let Some((_, tx)) = listener_pending.remove(&id) {
                                if let Some(err) = response.error {
                                    let _ = tx.send(Err(McpError::ToolError(err.to_string())));
                                } else if let Some(res) = response.result {
                                    let _ = tx.send(Ok(res));
                                } else {
                                    let _ = tx.send(Err(McpError::ParseError(
                                        "Missing result and error".into(),
                                    )));
                                }
                            }
                        }
                    } else {
                        eprintln!("⚠️ [MCP WARN] Unparseable JSON on stdout: {}", trimmed);
                    }
                }
                line.clear();
            }
            eprintln!("⚠️ [MCP WARN] Stdout pipe closed.");
        });

        tokio::spawn(async move {
            let status = child.wait().await;
            eprintln!("💀 [AIM-OS FATAL] Python MCP Daemon exited: {:?}", status);
            let keys: Vec<u64> = watcher_pending.iter().map(|kv| *kv.key()).collect();
            for k in keys {
                if let Some((_, tx)) = watcher_pending.remove(&k) {
                    let _ = tx.send(Err(McpError::DaemonDied));
                }
            }
        });

        let bridge = Arc::new(Self {
            stdin: Mutex::new(stdin),
            request_id_counter: AtomicU64::new(1),
            pending_requests,
        });

        bridge.initialize().await?;
        bridge.sanity_probe().await?;

        Ok(bridge)
    }

    pub async fn send_request(&self, method: &str, params: Option<Value>) -> Result<Value, McpError> {
        let id = self.request_id_counter.fetch_add(1, Ordering::SeqCst);
        let request = JsonRpcRequest {
            jsonrpc: "2.0".to_string(),
            method: method.to_string(),
            params,
            id,
        };

        let (tx, rx) = oneshot::channel();
        self.pending_requests.insert(id, tx);

        let payload = format!("{}\n", serde_json::to_string(&request).unwrap());
        {
            let mut stdin_lock = self.stdin.lock().await;
            if let Err(e) = stdin_lock.write_all(payload.as_bytes()).await {
                self.pending_requests.remove(&id);
                return Err(McpError::IoError(e.to_string()));
            }
            if let Err(e) = stdin_lock.flush().await {
                self.pending_requests.remove(&id);
                return Err(McpError::IoError(e.to_string()));
            }
        }

        match tokio::time::timeout(Duration::from_secs(90), rx).await {
            Ok(Ok(Ok(res))) => Ok(res),
            Ok(Ok(Err(e))) => Err(e),
            Ok(Err(_)) => Err(McpError::DaemonDied),
            Err(_) => {
                self.pending_requests.remove(&id);
                Err(McpError::Timeout(format!(
                    "Timeout waiting for MCP method: {}",
                    method
                )))
            }
        }
    }

    async fn initialize(&self) -> Result<(), String> {
        println!("🔄 [AIM-OS] Sending MCP Initialize Handshake...");
        let params = json!({
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": { "name": "SAIOS-Tauri-Kernel", "version": "1.0.0" }
        });

        self.send_request("initialize", Some(params))
            .await
            .map_err(|e| format!("Initialize failed: {:?}", e))?;

        let notif = JsonRpcNotification {
            jsonrpc: "2.0".to_string(),
            method: "notifications/initialized".to_string(),
            params: None,
        };
        let payload = format!("{}\n", serde_json::to_string(&notif).unwrap());
        let mut stdin_lock = self.stdin.lock().await;
        let _ = stdin_lock.write_all(payload.as_bytes()).await.unwrap();
        let _ = stdin_lock.flush().await.unwrap();

        println!("✅ [AIM-OS] MCP Handshake Complete.");
        Ok(())
    }

    async fn sanity_probe(&self) -> Result<(), String> {
        println!("🔍 [AIM-OS] Probing MCP Brain Stem for Tool Surface (tools/list)...");
        let tools_response = self
            .send_request("tools/list", None)
            .await
            .map_err(|e| format!("Sanity Probe failed: {:?}", e))?;

        if let Some(tool_list) = tools_response.get("tools").and_then(|t| t.as_array()) {
            println!(
                "🎯 [AIM-OS] Brain Stem Online. Discovered {} cognitive tools.",
                tool_list.len()
            );
            Ok(())
        } else {
            Err("Sanity Probe failed: Did not receive valid tools list".into())
        }
    }
}
