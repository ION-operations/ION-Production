# packages/mcp_data_integration/data_visualization_dashboard.py
"""
Data Visualization Dashboard - Visual representation of consciousness data

This module provides a comprehensive dashboard for visualizing consciousness data
from various sources, including MCP tools and file system data.

Features:
- Interactive data visualization
- Real-time data updates
- Multiple chart types
- Data filtering and exploration
- Export capabilities
"""

import json
import re
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

from .data_indexer import DataIndexer, IndexedFile
from .search_engine import SearchEngine, SearchQuery
from .cross_reference_system import CrossReferenceSystem
from .confidence_system_integration import ConfidenceSystemIntegration, MCPConfidenceRecord

logger = logging.getLogger(__name__)

@dataclass
class ChartData:
    """Represents data for a chart."""
    chart_id: str
    chart_type: str  # line, bar, pie, scatter, heatmap, timeline
    title: str
    data: List[Dict[str, Any]]
    x_axis: str
    y_axis: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DashboardWidget:
    """Represents a dashboard widget."""
    widget_id: str
    widget_type: str  # chart, metric, table, text
    title: str
    position: Tuple[int, int]  # (row, col)
    size: Tuple[int, int]  # (width, height)
    data: Any
    config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DashboardConfig:
    """Configuration for the dashboard."""
    dashboard_id: str
    name: str
    description: str
    widgets: List[DashboardWidget]
    layout: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: int = 30  # seconds
    auto_refresh: bool = True

class DataVisualizationDashboard:
    """
    Data visualization dashboard for consciousness data.
    
    This class provides comprehensive visualization capabilities for consciousness
    data from various sources, including MCP tools and file system data.
    """
    
    def __init__(self, data_indexer: DataIndexer, search_engine: SearchEngine,
                 cross_reference_system: CrossReferenceSystem,
                 confidence_system: ConfidenceSystemIntegration):
        """
        Initialize the Data Visualization Dashboard.
        
        Args:
            data_indexer: DataIndexer instance for accessing indexed data
            search_engine: SearchEngine instance for data search
            cross_reference_system: CrossReferenceSystem instance for relationships
            confidence_system: ConfidenceSystemIntegration instance for confidence data
        """
        self.data_indexer = data_indexer
        self.search_engine = search_engine
        self.cross_reference_system = cross_reference_system
        self.confidence_system = confidence_system
        
        self.dashboards: Dict[str, DashboardConfig] = {}
        self.charts: Dict[str, ChartData] = {}
        self.widgets: Dict[str, DashboardWidget] = {}
        
        # Initialize default dashboards
        self._create_default_dashboards()
        
        logger.info("Data Visualization Dashboard initialized")
    
    def _create_default_dashboards(self):
        """Create default dashboards."""
        # Consciousness Overview Dashboard
        consciousness_dashboard = self._create_consciousness_overview_dashboard()
        self.dashboards[consciousness_dashboard.dashboard_id] = consciousness_dashboard
        
        # Learning Progress Dashboard
        learning_dashboard = self._create_learning_progress_dashboard()
        self.dashboards[learning_dashboard.dashboard_id] = learning_dashboard
        
        # System Health Dashboard
        health_dashboard = self._create_system_health_dashboard()
        self.dashboards[health_dashboard.dashboard_id] = health_dashboard
        
        logger.info("Created 3 default dashboards")
    
    def _create_consciousness_overview_dashboard(self) -> DashboardConfig:
        """Create the consciousness overview dashboard."""
        dashboard_id = str(uuid.uuid4())
        widgets = []
        
        # File type distribution pie chart
        file_type_chart = self._create_file_type_distribution_chart()
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            widget_type="chart",
            title="File Type Distribution",
            position=(0, 0),
            size=(4, 3),
            data=file_type_chart,
            config={"chart_type": "pie"}
        ))
        
        # Timeline activity chart
        timeline_chart = self._create_timeline_activity_chart()
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            widget_type="chart",
            title="Timeline Activity",
            position=(0, 4),
            size=(8, 3),
            data=timeline_chart,
            config={"chart_type": "line"}
        ))
        
        # Confidence trend chart
        confidence_chart = self._create_confidence_trend_chart()
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            widget_type="chart",
            title="Confidence Trends",
            position=(3, 0),
            size=(6, 3),
            data=confidence_chart,
            config={"chart_type": "line"}
        ))
        
        # Key metrics widget
        metrics_widget = self._create_key_metrics_widget()
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            widget_type="metric",
            title="Key Metrics",
            position=(3, 6),
            size=(6, 3),
            data=metrics_widget,
            config={"metric_type": "summary"}
        ))
        
        return DashboardConfig(
            dashboard_id=dashboard_id,
            name="Consciousness Overview",
            description="Overview of consciousness data and activity",
            widgets=widgets,
            layout={"grid_size": (6, 12), "auto_layout": True},
            refresh_interval=30,
            auto_refresh=True
        )
    
    def _create_learning_progress_dashboard(self) -> DashboardConfig:
        """Create the learning progress dashboard."""
        dashboard_id = str(uuid.uuid4())
        widgets = []
        
        # Learning milestones timeline
        milestones_chart = self._create_learning_milestones_chart()
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            widget_type="chart",
            title="Learning Milestones",
            position=(0, 0),
            size=(12, 4),
            data=milestones_chart,
            config={"chart_type": "timeline"}
        ))
        
        # Knowledge growth chart
        knowledge_chart = self._create_knowledge_growth_chart()
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            widget_type="chart",
            title="Knowledge Growth",
            position=(4, 0),
            size=(6, 4),
            data=knowledge_chart,
            config={"chart_type": "bar"}
        ))
        
        # Learning efficiency chart
        efficiency_chart = self._create_learning_efficiency_chart()
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            widget_type="chart",
            title="Learning Efficiency",
            position=(4, 6),
            size=(6, 4),
            data=efficiency_chart,
            config={"chart_type": "scatter"}
        ))
        
        return DashboardConfig(
            dashboard_id=dashboard_id,
            name="Learning Progress",
            description="Track learning progress and knowledge growth",
            widgets=widgets,
            layout={"grid_size": (8, 12), "auto_layout": True},
            refresh_interval=60,
            auto_refresh=True
        )
    
    def _create_system_health_dashboard(self) -> DashboardConfig:
        """Create the system health dashboard."""
        dashboard_id = str(uuid.uuid4())
        widgets = []
        
        # System status metrics
        status_metrics = self._create_system_status_metrics()
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            widget_type="metric",
            title="System Status",
            position=(0, 0),
            size=(4, 3),
            data=status_metrics,
            config={"metric_type": "status"}
        ))
        
        # Performance metrics
        performance_chart = self._create_performance_metrics_chart()
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            widget_type="chart",
            title="Performance Metrics",
            position=(0, 4),
            size=(8, 3),
            data=performance_chart,
            config={"chart_type": "line"}
        ))
        
        # Error tracking chart
        error_chart = self._create_error_tracking_chart()
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            widget_type="chart",
            title="Error Tracking",
            position=(3, 0),
            size=(6, 3),
            data=error_chart,
            config={"chart_type": "bar"}
        ))
        
        # Health alerts
        alerts_widget = self._create_health_alerts_widget()
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            widget_type="table",
            title="Health Alerts",
            position=(3, 6),
            size=(6, 3),
            data=alerts_widget,
            config={"table_type": "alerts"}
        ))
        
        return DashboardConfig(
            dashboard_id=dashboard_id,
            name="System Health",
            description="Monitor system health and performance",
            widgets=widgets,
            layout={"grid_size": (6, 12), "auto_layout": True},
            refresh_interval=15,
            auto_refresh=True
        )
    
    def _create_file_type_distribution_chart(self) -> ChartData:
        """Create file type distribution chart data."""
        file_types = {}
        for indexed_file in self.data_indexer.indexed_files.values():
            file_type = indexed_file.file_type
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        data = [{"label": file_type, "value": count} for file_type, count in file_types.items()]
        
        return ChartData(
            chart_id=str(uuid.uuid4()),
            chart_type="pie",
            title="File Type Distribution",
            data=data,
            x_axis="file_type",
            y_axis="count",
            metadata={"total_files": sum(file_types.values())}
        )
    
    def _create_timeline_activity_chart(self) -> ChartData:
        """Create timeline activity chart data."""
        # Get timeline data from the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Group files by date
        daily_counts = {}
        for indexed_file in self.data_indexer.indexed_files.values():
            file_date = datetime.fromtimestamp(indexed_file.last_modified)
            if start_date <= file_date <= end_date:
                date_str = file_date.strftime("%Y-%m-%d")
                daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
        
        # Sort by date
        sorted_dates = sorted(daily_counts.keys())
        data = [{"date": date, "count": daily_counts[date]} for date in sorted_dates]
        
        return ChartData(
            chart_id=str(uuid.uuid4()),
            chart_type="line",
            title="Timeline Activity",
            data=data,
            x_axis="date",
            y_axis="count",
            metadata={"period_days": 30, "total_activity": sum(daily_counts.values())}
        )
    
    def _create_confidence_trend_chart(self) -> ChartData:
        """Create confidence trend chart data."""
        # Get confidence records from the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        confidence_records = self.confidence_system.get_confidence_records(
            start_date=start_date,
            end_date=end_date
        )
        
        # Group by date and calculate average confidence
        daily_confidence = {}
        for record in confidence_records:
            record_date = datetime.fromisoformat(record.timestamp).strftime("%Y-%m-%d")
            if record_date not in daily_confidence:
                daily_confidence[record_date] = []
            daily_confidence[record_date].append(record.confidence_score)
        
        # Calculate average confidence per day
        data = []
        for date, scores in daily_confidence.items():
            avg_confidence = sum(scores) / len(scores)
            data.append({"date": date, "confidence": avg_confidence, "count": len(scores)})
        
        # Sort by date
        data.sort(key=lambda x: x["date"])
        
        return ChartData(
            chart_id=str(uuid.uuid4()),
            chart_type="line",
            title="Confidence Trends",
            data=data,
            x_axis="date",
            y_axis="confidence",
            metadata={"period_days": 30, "total_records": len(confidence_records)}
        )
    
    def _create_key_metrics_widget(self) -> Dict[str, Any]:
        """Create key metrics widget data."""
        total_files = len(self.data_indexer.indexed_files)
        total_confidence_records = len(self.confidence_system.confidence_records)
        
        # Calculate average confidence
        confidence_scores = [r.confidence_score for r in self.confidence_system.confidence_records.values()]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Calculate file type distribution
        file_types = {}
        for indexed_file in self.data_indexer.indexed_files.values():
            file_type = indexed_file.file_type
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return {
            "total_files": total_files,
            "total_confidence_records": total_confidence_records,
            "average_confidence": round(avg_confidence, 3),
            "file_types": file_types,
            "last_updated": datetime.now().isoformat()
        }
    
    def _create_learning_milestones_chart(self) -> ChartData:
        """Create learning milestones chart data."""
        # Extract milestones from thought journals and decision logs
        milestones = []
        
        for indexed_file in self.data_indexer.indexed_files.values():
            if indexed_file.file_type in ["thought_journal", "decision_log"]:
                content = indexed_file.content
                
                # Look for milestone patterns
                milestone_patterns = [
                    r"milestone[:\s]+(.+)",
                    r"breakthrough[:\s]+(.+)",
                    r"achievement[:\s]+(.+)",
                    r"completed[:\s]+(.+)",
                    r"success[:\s]+(.+)"
                ]
                
                for pattern in milestone_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        milestone_text = match.group(1).strip()
                        milestones.append({
                            "date": datetime.fromtimestamp(indexed_file.last_modified).strftime("%Y-%m-%d"),
                            "milestone": milestone_text,
                            "file": indexed_file.file_name,
                            "type": indexed_file.file_type
                        })
        
        # Sort by date
        milestones.sort(key=lambda x: x["date"])
        
        return ChartData(
            chart_id=str(uuid.uuid4()),
            chart_type="timeline",
            title="Learning Milestones",
            data=milestones,
            x_axis="date",
            y_axis="milestone",
            metadata={"total_milestones": len(milestones)}
        )
    
    def _create_knowledge_growth_chart(self) -> ChartData:
        """Create knowledge growth chart data."""
        # Calculate knowledge growth over time
        # This is a simplified version - in reality, you'd analyze content complexity, concepts, etc.
        
        # Group files by month
        monthly_counts = {}
        for indexed_file in self.data_indexer.indexed_files.values():
            file_date = datetime.fromtimestamp(indexed_file.last_modified)
            month_str = file_date.strftime("%Y-%m")
            monthly_counts[month_str] = monthly_counts.get(month_str, 0) + 1
        
        # Sort by month
        sorted_months = sorted(monthly_counts.keys())
        data = [{"month": month, "files": monthly_counts[month]} for month in sorted_months]
        
        return ChartData(
            chart_id=str(uuid.uuid4()),
            chart_type="bar",
            title="Knowledge Growth",
            data=data,
            x_axis="month",
            y_axis="files",
            metadata={"total_months": len(sorted_months)}
        )
    
    def _create_learning_efficiency_chart(self) -> ChartData:
        """Create learning efficiency chart data."""
        # Calculate learning efficiency based on confidence vs time
        # This is a simplified version
        
        efficiency_data = []
        for record in self.confidence_system.confidence_records.values():
            record_date = datetime.fromisoformat(record.timestamp)
            efficiency_data.append({
                "date": record_date.strftime("%Y-%m-%d"),
                "confidence": record.confidence_score,
                "efficiency": record.confidence_score * 100  # Simplified efficiency metric
            })
        
        # Sort by date
        efficiency_data.sort(key=lambda x: x["date"])
        
        return ChartData(
            chart_id=str(uuid.uuid4()),
            chart_type="scatter",
            title="Learning Efficiency",
            data=efficiency_data,
            x_axis="date",
            y_axis="efficiency",
            metadata={"total_points": len(efficiency_data)}
        )
    
    def _create_system_status_metrics(self) -> Dict[str, Any]:
        """Create system status metrics."""
        total_files = len(self.data_indexer.indexed_files)
        total_confidence_records = len(self.confidence_system.confidence_records)
        
        # Calculate system health score
        health_score = min(100, (total_files * 0.1) + (total_confidence_records * 0.5))
        
        return {
            "health_score": round(health_score, 1),
            "total_files": total_files,
            "confidence_records": total_confidence_records,
            "status": "healthy" if health_score > 80 else "warning" if health_score > 60 else "critical",
            "last_updated": datetime.now().isoformat()
        }
    
    def _create_performance_metrics_chart(self) -> ChartData:
        """Create performance metrics chart data."""
        # This is a simplified version - in reality, you'd track actual performance metrics
        
        # Simulate performance data
        data = []
        for i in range(30):
            date = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
            data.append({
                "date": date,
                "response_time": 100 + (i * 2) + (i % 3) * 10,  # Simulated response time
                "throughput": 50 + (i * 1.5),  # Simulated throughput
                "error_rate": max(0, 0.1 - (i * 0.001))  # Simulated error rate
            })
        
        return ChartData(
            chart_id=str(uuid.uuid4()),
            chart_type="line",
            title="Performance Metrics",
            data=data,
            x_axis="date",
            y_axis="value",
            metadata={"metrics": ["response_time", "throughput", "error_rate"]}
        )
    
    def _create_error_tracking_chart(self) -> ChartData:
        """Create error tracking chart data."""
        # This is a simplified version - in reality, you'd track actual errors
        
        # Simulate error data
        data = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
            data.append({
                "date": date,
                "errors": max(0, 5 - i + (i % 2)),  # Simulated error count
                "warnings": 10 + (i * 2)  # Simulated warning count
            })
        
        return ChartData(
            chart_id=str(uuid.uuid4()),
            chart_type="bar",
            title="Error Tracking",
            data=data,
            x_axis="date",
            y_axis="count",
            metadata={"error_types": ["errors", "warnings"]}
        )
    
    def _create_health_alerts_widget(self) -> List[Dict[str, Any]]:
        """Create health alerts widget data."""
        alerts = []
        
        # Check for potential issues
        total_files = len(self.data_indexer.indexed_files)
        if total_files < 100:
            alerts.append({
                "level": "warning",
                "message": "Low file count - may indicate incomplete indexing",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check confidence records
        confidence_records = len(self.confidence_system.confidence_records)
        if confidence_records < 10:
            alerts.append({
                "level": "info",
                "message": "Few confidence records - consider enabling more confidence tracking",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check for recent activity
        recent_files = 0
        cutoff_time = time.time() - (24 * 60 * 60)  # 24 hours ago
        for indexed_file in self.data_indexer.indexed_files.values():
            if indexed_file.last_modified > cutoff_time:
                recent_files += 1
        
        if recent_files == 0:
            alerts.append({
                "level": "warning",
                "message": "No recent file activity - system may be inactive",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def get_dashboard(self, dashboard_id: str) -> Optional[DashboardConfig]:
        """Get a dashboard by ID."""
        return self.dashboards.get(dashboard_id)
    
    def get_all_dashboards(self) -> List[DashboardConfig]:
        """Get all dashboards."""
        return list(self.dashboards.values())
    
    def create_custom_dashboard(self, name: str, description: str,
                              widgets: List[DashboardWidget]) -> DashboardConfig:
        """Create a custom dashboard."""
        dashboard_id = str(uuid.uuid4())
        
        dashboard = DashboardConfig(
            dashboard_id=dashboard_id,
            name=name,
            description=description,
            widgets=widgets,
            layout={"grid_size": (6, 12), "auto_layout": True},
            refresh_interval=30,
            auto_refresh=True
        )
        
        self.dashboards[dashboard_id] = dashboard
        logger.info(f"Created custom dashboard: {name}")
        
        return dashboard
    
    def update_dashboard(self, dashboard_id: str, updates: Dict[str, Any]) -> bool:
        """Update a dashboard."""
        if dashboard_id not in self.dashboards:
            return False
        
        dashboard = self.dashboards[dashboard_id]
        
        # Update dashboard properties
        for key, value in updates.items():
            if hasattr(dashboard, key):
                setattr(dashboard, key, value)
        
        logger.info(f"Updated dashboard: {dashboard_id}")
        return True
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        if dashboard_id not in self.dashboards:
            return False
        
        del self.dashboards[dashboard_id]
        logger.info(f"Deleted dashboard: {dashboard_id}")
        return True
    
    def export_dashboard_data(self, dashboard_id: str, format: str = "json") -> str:
        """Export dashboard data in specified format."""
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return ""
        
        if format == "json":
            return json.dumps({
                "dashboard_id": dashboard.dashboard_id,
                "name": dashboard.name,
                "description": dashboard.description,
                "widgets": [
                    {
                        "widget_id": widget.widget_id,
                        "widget_type": widget.widget_type,
                        "title": widget.title,
                        "position": widget.position,
                        "size": widget.size,
                        "data": widget.data,
                        "config": widget.config
                    }
                    for widget in dashboard.widgets
                ],
                "layout": dashboard.layout,
                "filters": dashboard.filters,
                "refresh_interval": dashboard.refresh_interval,
                "auto_refresh": dashboard.auto_refresh
            }, indent=2)
        else:
            return "Unsupported format"
    
    def refresh_dashboard(self, dashboard_id: str) -> bool:
        """Refresh a dashboard with updated data."""
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return False
        
        # Refresh all widgets in the dashboard
        for widget in dashboard.widgets:
            if widget.widget_type == "chart":
                # Refresh chart data
                if "file_type" in widget.title.lower():
                    widget.data = self._create_file_type_distribution_chart()
                elif "timeline" in widget.title.lower():
                    widget.data = self._create_timeline_activity_chart()
                elif "confidence" in widget.title.lower():
                    widget.data = self._create_confidence_trend_chart()
                # Add more chart refresh logic as needed
            elif widget.widget_type == "metric":
                # Refresh metric data
                if "key" in widget.title.lower():
                    widget.data = self._create_key_metrics_widget()
                elif "status" in widget.title.lower():
                    widget.data = self._create_system_status_metrics()
                # Add more metric refresh logic as needed
        
        logger.info(f"Refreshed dashboard: {dashboard_id}")
        return True
    
    def get_dashboard_analytics(self) -> Dict[str, Any]:
        """Get analytics about all dashboards."""
        total_dashboards = len(self.dashboards)
        total_widgets = sum(len(dashboard.widgets) for dashboard in self.dashboards.values())
        
        widget_types = {}
        for dashboard in self.dashboards.values():
            for widget in dashboard.widgets:
                widget_type = widget.widget_type
                widget_types[widget_type] = widget_types.get(widget_type, 0) + 1
        
        return {
            "total_dashboards": total_dashboards,
            "total_widgets": total_widgets,
            "widget_type_distribution": widget_types,
            "average_widgets_per_dashboard": total_widgets / total_dashboards if total_dashboards > 0 else 0,
            "last_updated": datetime.now().isoformat()
        }
