#!/usr/bin/env python3
"""
Advanced MCP Data Integration Demo

This script demonstrates the advanced features of the MCP Data Integration system,
including confidence tracking, data visualization, and advanced analytics.

Usage:
    python packages/mcp_data_integration/demo_advanced.py
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add the parent directory to the sys.path to allow importing from 'packages'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from mcp_data_integration import (
    DataIndexer, FileSystemMonitor, MCPDataBridge, SearchEngine, SearchQuery,
    CrossReferenceSystem, ConfidenceSystemIntegration, MCPConfidenceRecord,
    DataVisualizationDashboard, DashboardConfig, DashboardWidget, ChartData,
    AdvancedAnalytics, Pattern, Trend, Anomaly, Correlation, Insight
)

def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")

def main():
    """Main demo function."""
    print("Advanced MCP Data Integration Demo")
    print("This demo showcases the advanced features of the MCP Data Integration system.")
    
    # Initialize components
    print_section("Initializing Components")
    
    # Data Indexer
    print("Initializing Data Indexer...")
    data_indexer = DataIndexer("knowledge_architecture/AETHER_MEMORY")
    indexed_count = data_indexer.index_all_files()
    print(f"Indexed {indexed_count} files")
    
    # File System Monitor
    print("Initializing File System Monitor...")
    file_monitor = FileSystemMonitor("knowledge_architecture/AETHER_MEMORY")
    print("File System Monitor ready")
    
    # Search Engine
    print("Initializing Search Engine...")
    search_engine = SearchEngine(data_indexer)
    print("Search Engine ready")
    
    # Cross Reference System
    print("Initializing Cross Reference System...")
    cross_ref_system = CrossReferenceSystem(data_indexer)
    print("Cross Reference System ready")
    
    # Confidence System Integration
    print("Initializing Confidence System Integration...")
    confidence_system = ConfidenceSystemIntegration(data_indexer)
    print("Confidence System Integration ready")
    
    # Data Visualization Dashboard
    print("Initializing Data Visualization Dashboard...")
    dashboard = DataVisualizationDashboard(
        data_indexer, search_engine, cross_ref_system, confidence_system
    )
    print("Data Visualization Dashboard ready")
    
    # Advanced Analytics
    print("Initializing Advanced Analytics...")
    analytics = AdvancedAnalytics(
        data_indexer, search_engine, cross_ref_system, confidence_system
    )
    print("Advanced Analytics ready")
    
    # MCP Data Bridge
    print("Initializing MCP Data Bridge...")
    mcp_bridge = MCPDataBridge("knowledge_architecture/AETHER_MEMORY")
    print("MCP Data Bridge ready")
    
    # Phase 3: Advanced Features Demo
    print_section("Phase 3: Advanced Features Demo")
    
    # Confidence System Integration Demo
    print_subsection("Confidence System Integration")
    
    print("Extracting confidence data from files...")
    confidence_records = confidence_system.extract_confidence_from_files()
    print(f"Extracted {len(confidence_records)} confidence records")
    
    if confidence_records:
        print("\nSample confidence records:")
        for i, record in enumerate(confidence_records[:3]):
            print(f"  {i+1}. Confidence: {record.confidence_score:.2f}")
            # Sanitize context for display
            context_safe = record.context[:100].encode('ascii', 'replace').decode('ascii')
            print(f"     Context: {context_safe}...")
            print(f"     Tags: {', '.join(record.tags)}")
            print()
    
    # Get confidence analytics
    print("Getting confidence analytics...")
    confidence_analytics = confidence_system.get_confidence_analytics()
    print(f"Confidence Analytics:")
    print(f"   Total Records: {confidence_analytics['total_records']}")
    print(f"   Average Confidence: {confidence_analytics['average_confidence']:.3f}")
    print(f"   Confidence Levels: {confidence_analytics['confidence_level_distribution']}")
    print(f"   Tag Distribution: {dict(list(confidence_analytics['tag_distribution'].items())[:5])}")
    
    # Analyze confidence trends
    print("\nAnalyzing confidence trends...")
    confidence_trends = confidence_system.analyze_confidence_trends(days=30)
    print(f"Found {len(confidence_trends)} confidence trends")
    
    for trend in confidence_trends[:2]:
        print(f"   Trend: {trend.trend_type} (average: {trend.average_confidence:.2f})")
        print(f"   Variance: {trend.confidence_variance:.3f}, Data Points: {trend.data_points}")
    
    # Data Visualization Dashboard Demo
    print_subsection("Data Visualization Dashboard")
    
    print("Getting dashboard information...")
    dashboards = dashboard.get_all_dashboards()
    print(f"Available dashboards: {len(dashboards)}")
    
    for db in dashboards:
        print(f"   - {db.name}: {len(db.widgets)} widgets")
    
    # Get dashboard analytics
    print("\nGetting dashboard analytics...")
    dashboard_analytics = dashboard.get_dashboard_analytics()
    print(f"Dashboard Analytics:")
    print(f"   Total Dashboards: {dashboard_analytics['total_dashboards']}")
    print(f"   Total Widgets: {dashboard_analytics['total_widgets']}")
    print(f"   Widget Types: {dashboard_analytics['widget_type_distribution']}")
    
    # Advanced Analytics Demo
    print_subsection("Advanced Analytics")
    
    print("Discovering patterns...")
    patterns = analytics.discover_patterns()
    print(f"Discovered {len(patterns)} patterns")
    
    for pattern in patterns[:3]:
        print(f"   - {pattern.pattern_type}: {pattern.description}")
        print(f"     Confidence: {pattern.confidence:.2f}, Frequency: {pattern.frequency}")
    
    print("\nAnalyzing trends...")
    trends = analytics.analyze_trends(days=30)
    print(f"Analyzed {len(trends)} trends")
    
    for trend in trends[:2]:
        print(f"   - {trend.trend_type} {trend.metric}: slope={trend.slope:.3f}, R²={trend.r_squared:.3f}")
    
    print("\nDetecting anomalies...")
    anomalies = analytics.detect_anomalies()
    print(f"Detected {len(anomalies)} anomalies")
    
    for anomaly in anomalies[:2]:
        print(f"   - {anomaly.anomaly_type}: {anomaly.description}")
        print(f"     Severity: {anomaly.severity}")
    
    print("\nAnalyzing correlations...")
    correlations = analytics.analyze_correlations()
    print(f"Analyzed {len(correlations)} correlations")
    
    for correlation in correlations[:2]:
        print(f"   - {correlation.variable1} <-> {correlation.variable2}")
        print(f"     Correlation: {correlation.correlation_coefficient:.3f} ({correlation.relationship_type})")
    
    print("\nGenerating insights...")
    insights = analytics.generate_insights()
    print(f"Generated {len(insights)} insights")
    
    for insight in insights[:3]:
        print(f"   - {insight.insight_type}: {insight.title}")
        print(f"     Confidence: {insight.confidence:.2f}, Impact: {insight.impact}")
        if insight.recommendations:
            print(f"     Recommendations: {insight.recommendations[0]}")
    
    # Get analytics summary
    print("\nGetting analytics summary...")
    analytics_summary = analytics.get_analytics_summary()
    print(f"Analytics Summary:")
    print(f"   Patterns: {analytics_summary['patterns']['total']} total, {analytics_summary['patterns']['high_confidence']} high confidence")
    print(f"   Trends: {analytics_summary['trends']['total']} total, {analytics_summary['trends']['high_confidence']} high confidence")
    print(f"   Anomalies: {analytics_summary['anomalies']['total']} total")
    print(f"   Correlations: {analytics_summary['correlations']['total']} total")
    print(f"   Insights: {analytics_summary['insights']['total']} total, {analytics_summary['insights']['actionable']} actionable")
    
    # MCP Data Bridge Demo
    print_subsection("MCP Data Bridge")
    
    print("Testing MCP Data Bridge...")
    
    # Test memory retrieval
    print("   Testing memory retrieval...")
    memory_atoms = mcp_bridge.get_memory_atoms(limit=5)
    print(f"   Retrieved {len(memory_atoms)} memory atoms")
    
    for memory in memory_atoms[:2]:
        print(f"     - {memory.content[:100]}...")
        print(f"       Tags: {memory.tags}")
    
    # Test timeline retrieval
    print("   Testing timeline retrieval...")
    timeline_entries = mcp_bridge.get_timeline_entries(limit=5)
    print(f"   Retrieved {len(timeline_entries)} timeline entries")
    
    for entry in timeline_entries[:2]:
        print(f"     - {entry.description[:100]}...")
        print(f"       Type: {entry.event_type}")
    
    # Test confidence retrieval
    print("   Testing confidence retrieval...")
    confidence_records = mcp_bridge.get_confidence_records(limit=5)
    print(f"   Retrieved {len(confidence_records)} confidence records")
    
    for record in confidence_records[:2]:
        print(f"     - Confidence: {record.confidence_score:.2f}")
        print(f"       Context: {record.context[:50]}...")
    
    # Test memory search
    print("   Testing memory search...")
    search_results = mcp_bridge.search_memory("MCP Data Integration", limit=3)
    print(f"   Found {len(search_results)} search results")
    
    for result in search_results[:2]:
        print(f"     - {result.file_name}: {result.content_snippet[:50]}...")
        print(f"       Score: {result.relevance_score:.2f}")
    
    # Test data synchronization
    print("   Testing data synchronization...")
    sync_result = mcp_bridge.sync_all_data()
    print(f"   Sync completed: {sync_result}")
    
    # Test memory stats
    print("   Testing memory stats...")
    memory_stats = mcp_bridge.get_memory_stats()
    print(f"   Memory stats: {memory_stats}")
    
    # Performance Metrics
    print_section("Performance Metrics")
    
    print("System Performance:")
    print(f"   Total Files Indexed: {len(data_indexer.indexed_files)}")
    print(f"   Confidence Records: {len(confidence_system.confidence_records)}")
    print(f"   Patterns Discovered: {len(analytics.patterns)}")
    print(f"   Trends Analyzed: {len(analytics.trends)}")
    print(f"   Anomalies Detected: {len(analytics.anomalies)}")
    print(f"   Correlations Found: {len(analytics.correlations)}")
    print(f"   Insights Generated: {len(analytics.insights)}")
    print(f"   Dashboards Available: {len(dashboard.dashboards)}")
    
    # Cleanup
    print_section("Cleanup")
    
    print("Cleaning up resources...")
    data_indexer.close()
    file_monitor.stop_monitoring()
    confidence_system.close()
    mcp_bridge.close()
    print("Cleanup completed")
    
    print_section("Demo Complete")
    print("Advanced MCP Data Integration Demo completed successfully!")
    print("\nKey Achievements:")
    print("Confidence System Integration - Extracted and analyzed confidence data")
    print("Data Visualization Dashboard - Created comprehensive dashboards")
    print("Advanced Analytics - Discovered patterns, trends, and insights")
    print("MCP Data Bridge - Integrated all systems with MCP tools")
    print("Performance Monitoring - Tracked system performance and metrics")
    
    print("\nNext Steps:")
    print("1. Explore the generated dashboards and visualizations")
    print("2. Review the discovered patterns and insights")
    print("3. Use the confidence tracking for decision making")
    print("4. Leverage the analytics for continuous improvement")
    print("5. Integrate with your existing MCP tools and workflows")

if __name__ == "__main__":
    main()
