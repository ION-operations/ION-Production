"""
CMC Service Monitoring Dashboard

This module provides a web-based monitoring dashboard for the CMC service,
displaying real-time metrics, health status, and system information.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from health_check import HealthCheckSystem, get_health_status, get_detailed_health
from production_config import load_config


class MonitoringDashboard:
    """CMC Service monitoring dashboard"""
    
    def __init__(self):
        self.config = load_config()
        self.logger = logging.getLogger(__name__)
        self.health_checker: Optional[HealthCheckSystem] = None
        self.websocket_connections: List[WebSocket] = []
        
        # Create FastAPI app
        self.app = FastAPI(
            title="CMC Service Monitoring Dashboard",
            version="1.0.0",
            description="Real-time monitoring for CMC Service"
        )
        
        # Setup routes
        self.setup_routes()
    
    def setup_routes(self):
        """Setup dashboard routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Main dashboard page"""
            return self.get_dashboard_html()
        
        @self.app.get("/api/health")
        async def health_api():
            """Health status API"""
            return get_health_status()
        
        @self.app.get("/api/health/detailed")
        async def detailed_health_api():
            """Detailed health information API"""
            return get_detailed_health()
        
        @self.app.get("/api/metrics")
        async def metrics_api():
            """Metrics API"""
            return self.get_metrics()
        
        @self.app.get("/api/system")
        async def system_api():
            """System information API"""
            return self.get_system_info()
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket for real-time updates"""
            await websocket.accept()
            self.websocket_connections.append(websocket)
            
            try:
                while True:
                    # Send periodic updates
                    data = {
                        "timestamp": datetime.now().isoformat(),
                        "health": get_health_status(),
                        "metrics": self.get_metrics(),
                        "system": self.get_system_info()
                    }
                    
                    await websocket.send_text(json.dumps(data))
                    await asyncio.sleep(5)  # Update every 5 seconds
                    
            except WebSocketDisconnect:
                self.websocket_connections.remove(websocket)
    
    def get_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMC Service Monitoring Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease;
        }
        
        .card:hover {
            transform: translateY(-2px);
        }
        
        .card h3 {
            color: #4a5568;
            margin-bottom: 15px;
            font-size: 1.2rem;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-healthy { background-color: #48bb78; }
        .status-degraded { background-color: #ed8936; }
        .status-unhealthy { background-color: #f56565; }
        .status-critical { background-color: #e53e3e; }
        .status-unknown { background-color: #a0aec0; }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            font-weight: 500;
            color: #4a5568;
        }
        
        .metric-value {
            font-weight: 600;
            color: #2d3748;
        }
        
        .chart-container {
            height: 200px;
            background: #f7fafc;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #a0aec0;
            font-style: italic;
        }
        
        .refresh-button {
            background: #4299e1;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            transition: background 0.2s ease;
        }
        
        .refresh-button:hover {
            background: #3182ce;
        }
        
        .footer {
            text-align: center;
            color: white;
            opacity: 0.8;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CMC Service Monitoring</h1>
            <p>Real-time system health and performance metrics</p>
        </div>
        
        <div class="dashboard-grid">
            <div class="card">
                <h3>System Health</h3>
                <div id="health-status">
                    <div class="metric">
                        <span class="metric-label">Overall Status</span>
                        <span class="metric-value">
                            <span class="status-indicator status-unknown"></span>
                            <span id="overall-status">Loading...</span>
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Last Check</span>
                        <span class="metric-value" id="last-check">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Uptime</span>
                        <span class="metric-value" id="uptime">-</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Performance Metrics</h3>
                <div id="performance-metrics">
                    <div class="metric">
                        <span class="metric-label">Response Time</span>
                        <span class="metric-value" id="response-time">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Memory Usage</span>
                        <span class="metric-value" id="memory-usage">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">CPU Usage</span>
                        <span class="metric-value" id="cpu-usage">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Error Rate</span>
                        <span class="metric-value" id="error-rate">-</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Database Status</h3>
                <div id="database-status">
                    <div class="metric">
                        <span class="metric-label">Connection</span>
                        <span class="metric-value" id="db-connection">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Query Time</span>
                        <span class="metric-value" id="query-time">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Cache Hit Rate</span>
                        <span class="metric-value" id="cache-hit-rate">-</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>System Resources</h3>
                <div id="system-resources">
                    <div class="metric">
                        <span class="metric-label">Available Memory</span>
                        <span class="metric-value" id="available-memory">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Disk Usage</span>
                        <span class="metric-value" id="disk-usage">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Active Connections</span>
                        <span class="metric-value" id="active-connections">-</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div style="text-align: center;">
            <button class="refresh-button" onclick="refreshData()">Refresh Data</button>
        </div>
        
        <div class="footer">
            <p>CMC Service Monitoring Dashboard v1.0.0</p>
        </div>
    </div>
    
    <script>
        let ws = null;
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('WebSocket connected');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onclose = function() {
                console.log('WebSocket disconnected, reconnecting...');
                setTimeout(connectWebSocket, 5000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }
        
        function updateDashboard(data) {
            // Update health status
            const health = data.health;
            if (health) {
                document.getElementById('overall-status').textContent = health.status || 'unknown';
                document.getElementById('last-check').textContent = new Date(health.timestamp).toLocaleTimeString();
                
                // Update status indicator
                const indicator = document.querySelector('#overall-status .status-indicator');
                indicator.className = `status-indicator status-${health.status || 'unknown'}`;
            }
            
            // Update metrics
            const metrics = data.metrics;
            if (metrics) {
                document.getElementById('response-time').textContent = 
                    metrics.response_time ? `${metrics.response_time}ms` : '-';
                document.getElementById('memory-usage').textContent = 
                    metrics.memory_usage ? `${metrics.memory_usage}MB` : '-';
                document.getElementById('cpu-usage').textContent = 
                    metrics.cpu_usage ? `${metrics.cpu_usage}%` : '-';
                document.getElementById('error-rate').textContent = 
                    metrics.error_rate ? `${(metrics.error_rate * 100).toFixed(1)}%` : '-';
            }
            
            // Update system info
            const system = data.system;
            if (system) {
                document.getElementById('uptime').textContent = 
                    system.uptime ? formatUptime(system.uptime) : '-';
                document.getElementById('available-memory').textContent = 
                    system.available_memory ? `${system.available_memory}MB` : '-';
                document.getElementById('disk-usage').textContent = 
                    system.disk_usage ? `${system.disk_usage}%` : '-';
                document.getElementById('active-connections').textContent = 
                    system.active_connections || '-';
            }
        }
        
        function formatUptime(seconds) {
            const days = Math.floor(seconds / 86400);
            const hours = Math.floor((seconds % 86400) / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            
            if (days > 0) {
                return `${days}d ${hours}h ${minutes}m`;
            } else if (hours > 0) {
                return `${hours}h ${minutes}m`;
            } else {
                return `${minutes}m`;
            }
        }
        
        function refreshData() {
            fetch('/api/health')
                .then(response => response.json())
                .then(data => updateDashboard({health: data}))
                .catch(error => console.error('Error fetching data:', error));
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            connectWebSocket();
            refreshData();
        });
    </script>
</body>
</html>
        """
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        try:
            import psutil
            
            process = psutil.Process()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "response_time": 0,  # Would be calculated from actual requests
                "memory_usage": process.memory_info().rss / 1024 / 1024,  # MB
                "cpu_usage": process.cpu_percent(),
                "error_rate": 0,  # Would be calculated from actual requests
                "cache_hit_rate": 0.95,  # Would be calculated from cache stats
                "query_time": 0,  # Would be calculated from database queries
            }
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}")
            return {}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            import psutil
            
            return {
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time() - psutil.boot_time(),
                "available_memory": psutil.virtual_memory().available / 1024 / 1024,  # MB
                "disk_usage": psutil.disk_usage('/').percent,
                "active_connections": 0,  # Would be calculated from actual connections
                "cpu_count": psutil.cpu_count(),
                "platform": psutil.platform(),
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}


def create_dashboard_app() -> FastAPI:
    """Create and return the dashboard FastAPI app"""
    dashboard = MonitoringDashboard()
    return dashboard.app


def run_dashboard(host: str = "0.0.0.0", port: int = 8080):
    """Run the monitoring dashboard"""
    app = create_dashboard_app()
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run CMC Monitoring Dashboard")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    
    args = parser.parse_args()
    
    run_dashboard(host=args.host, port=args.port)
