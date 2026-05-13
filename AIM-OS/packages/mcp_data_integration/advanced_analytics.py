# packages/mcp_data_integration/advanced_analytics.py
"""
Advanced Analytics - Deep analysis and insights from consciousness data

This module provides advanced analytics capabilities for consciousness data,
including pattern recognition, trend analysis, and predictive insights.

Features:
- Pattern recognition and analysis
- Trend analysis and forecasting
- Predictive modeling
- Anomaly detection
- Correlation analysis
- Insight generation
"""

import json
import re
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import statistics
from collections import Counter, defaultdict

from .data_indexer import DataIndexer, IndexedFile
from .search_engine import SearchEngine, SearchQuery
from .cross_reference_system import CrossReferenceSystem
from .confidence_system_integration import ConfidenceSystemIntegration, MCPConfidenceRecord

logger = logging.getLogger(__name__)

@dataclass
class Pattern:
    """Represents a discovered pattern."""
    pattern_id: str
    pattern_type: str  # temporal, semantic, behavioral, structural
    description: str
    confidence: float
    frequency: int
    examples: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Trend:
    """Represents a trend analysis result."""
    trend_id: str
    trend_type: str  # increasing, decreasing, cyclical, stable
    metric: str
    start_date: datetime
    end_date: datetime
    slope: float
    r_squared: float
    confidence: float
    forecast: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Anomaly:
    """Represents an detected anomaly."""
    anomaly_id: str
    anomaly_type: str  # outlier, pattern_break, unexpected_value
    description: str
    severity: str  # low, medium, high, critical
    detected_at: datetime
    affected_data: List[str]
    explanation: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Correlation:
    """Represents a correlation between two variables."""
    correlation_id: str
    variable1: str
    variable2: str
    correlation_coefficient: float
    p_value: float
    significance: str  # low, medium, high
    relationship_type: str  # positive, negative, none
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Insight:
    """Represents a generated insight."""
    insight_id: str
    insight_type: str  # pattern, trend, anomaly, correlation, prediction
    title: str
    description: str
    confidence: float
    impact: str  # low, medium, high
    actionable: bool
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class AdvancedAnalytics:
    """
    Advanced analytics for consciousness data.
    
    This class provides comprehensive analytics capabilities for consciousness
    data, including pattern recognition, trend analysis, and predictive insights.
    """
    
    def __init__(self, data_indexer: DataIndexer, search_engine: SearchEngine,
                 cross_reference_system: CrossReferenceSystem,
                 confidence_system: ConfidenceSystemIntegration):
        """
        Initialize the Advanced Analytics.
        
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
        
        self.patterns: Dict[str, Pattern] = {}
        self.trends: Dict[str, Trend] = {}
        self.anomalies: Dict[str, Anomaly] = {}
        self.correlations: Dict[str, Correlation] = {}
        self.insights: Dict[str, Insight] = {}
        
        logger.info("Advanced Analytics initialized")
    
    def discover_patterns(self) -> List[Pattern]:
        """
        Discover patterns in consciousness data.
        
        Returns:
            List of discovered patterns
        """
        logger.info("Discovering patterns in consciousness data")
        
        patterns = []
        
        # Discover temporal patterns
        temporal_patterns = self._discover_temporal_patterns()
        patterns.extend(temporal_patterns)
        
        # Discover semantic patterns
        semantic_patterns = self._discover_semantic_patterns()
        patterns.extend(semantic_patterns)
        
        # Discover behavioral patterns
        behavioral_patterns = self._discover_behavioral_patterns()
        patterns.extend(behavioral_patterns)
        
        # Discover structural patterns
        structural_patterns = self._discover_structural_patterns()
        patterns.extend(structural_patterns)
        
        # Store patterns
        for pattern in patterns:
            self.patterns[pattern.pattern_id] = pattern
        
        logger.info(f"Discovered {len(patterns)} patterns")
        return patterns
    
    def _discover_temporal_patterns(self) -> List[Pattern]:
        """Discover temporal patterns in data."""
        patterns = []
        
        # Analyze file creation patterns
        creation_times = []
        for indexed_file in self.data_indexer.indexed_files.values():
            creation_times.append(datetime.fromtimestamp(indexed_file.last_modified))
        
        if len(creation_times) < 10:
            return patterns
        
        # Sort by time
        creation_times.sort()
        
        # Look for daily patterns
        hour_counts = defaultdict(int)
        for creation_time in creation_times:
            hour_counts[creation_time.hour] += 1
        
        # Find peak hours
        if hour_counts:
            max_hour = max(hour_counts, key=hour_counts.get)
            max_count = hour_counts[max_hour]
            total_count = sum(hour_counts.values())
            
            if max_count / total_count > 0.3:  # More than 30% of activity in one hour
                pattern = Pattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="temporal",
                    description=f"Peak activity at {max_hour}:00",
                    confidence=min(1.0, max_count / total_count),
                    frequency=max_count,
                    examples=[f"Activity at {max_hour}:00: {max_count} files"],
                    metadata={"peak_hour": max_hour, "total_activity": total_count}
                )
                patterns.append(pattern)
        
        # Look for weekly patterns
        weekday_counts = defaultdict(int)
        for creation_time in creation_times:
            weekday_counts[creation_time.weekday()] += 1
        
        if weekday_counts:
            max_weekday = max(weekday_counts, key=weekday_counts.get)
            max_count = weekday_counts[max_weekday]
            total_count = sum(weekday_counts.values())
            
            if max_count / total_count > 0.4:  # More than 40% of activity on one day
                weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                pattern = Pattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="temporal",
                    description=f"Peak activity on {weekday_names[max_weekday]}",
                    confidence=min(1.0, max_count / total_count),
                    frequency=max_count,
                    examples=[f"Activity on {weekday_names[max_weekday]}: {max_count} files"],
                    metadata={"peak_weekday": max_weekday, "total_activity": total_count}
                )
                patterns.append(pattern)
        
        return patterns
    
    def _discover_semantic_patterns(self) -> List[Pattern]:
        """Discover semantic patterns in data."""
        patterns = []
        
        # Analyze confidence patterns
        confidence_scores = [r.confidence_score for r in self.confidence_system.confidence_records.values()]
        
        if len(confidence_scores) < 10:
            return patterns
        
        # Look for confidence clusters
        high_confidence = [score for score in confidence_scores if score >= 0.8]
        medium_confidence = [score for score in confidence_scores if 0.5 <= score < 0.8]
        low_confidence = [score for score in confidence_scores if score < 0.5]
        
        total_scores = len(confidence_scores)
        
        if len(high_confidence) / total_scores > 0.6:
            pattern = Pattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type="semantic",
                description="High confidence bias in decision making",
                confidence=len(high_confidence) / total_scores,
                frequency=len(high_confidence),
                examples=[f"High confidence decisions: {len(high_confidence)}/{total_scores}"],
                metadata={"confidence_distribution": {"high": len(high_confidence), "medium": len(medium_confidence), "low": len(low_confidence)}}
            )
            patterns.append(pattern)
        
        # Analyze tag patterns
        all_tags = []
        for record in self.confidence_system.confidence_records.values():
            all_tags.extend(record.tags)
        
        if all_tags:
            tag_counts = Counter(all_tags)
            most_common_tag = tag_counts.most_common(1)[0]
            
            if most_common_tag[1] / len(all_tags) > 0.3:
                pattern = Pattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="semantic",
                    description=f"Frequent use of tag: {most_common_tag[0]}",
                    confidence=most_common_tag[1] / len(all_tags),
                    frequency=most_common_tag[1],
                    examples=[f"Tag '{most_common_tag[0]}' appears {most_common_tag[1]} times"],
                    metadata={"tag_frequency": dict(tag_counts)}
                )
                patterns.append(pattern)
        
        return patterns
    
    def _discover_behavioral_patterns(self) -> List[Pattern]:
        """Discover behavioral patterns in data."""
        patterns = []
        
        # Analyze file type preferences
        file_type_counts = defaultdict(int)
        for indexed_file in self.data_indexer.indexed_files.values():
            file_type_counts[indexed_file.file_type] += 1
        
        if file_type_counts:
            total_files = sum(file_type_counts.values())
            most_common_type = max(file_type_counts, key=file_type_counts.get)
            most_common_count = file_type_counts[most_common_type]
            
            if most_common_count / total_files > 0.4:
                pattern = Pattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="behavioral",
                    description=f"Preference for {most_common_type} files",
                    confidence=most_common_count / total_files,
                    frequency=most_common_count,
                    examples=[f"Created {most_common_count} {most_common_type} files out of {total_files} total"],
                    metadata={"file_type_distribution": dict(file_type_counts)}
                )
                patterns.append(pattern)
        
        # Analyze confidence vs file type patterns
        confidence_by_type = defaultdict(list)
        for record in self.confidence_system.confidence_records.values():
            if record.file_path:
                file_type = Path(record.file_path).suffix[1:] if Path(record.file_path).suffix else "unknown"
                confidence_by_type[file_type].append(record.confidence_score)
        
        for file_type, scores in confidence_by_type.items():
            if len(scores) >= 5:
                avg_confidence = sum(scores) / len(scores)
                if avg_confidence > 0.8:
                    pattern = Pattern(
                        pattern_id=str(uuid.uuid4()),
                        pattern_type="behavioral",
                        description=f"High confidence when working with {file_type} files",
                        confidence=min(1.0, avg_confidence),
                        frequency=len(scores),
                        examples=[f"Average confidence with {file_type} files: {avg_confidence:.2f}"],
                        metadata={"file_type": file_type, "average_confidence": avg_confidence}
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _discover_structural_patterns(self) -> List[Pattern]:
        """Discover structural patterns in data."""
        patterns = []
        
        # Analyze file size patterns
        file_sizes = [len(indexed_file.content) for indexed_file in self.data_indexer.indexed_files.values()]
        
        if len(file_sizes) >= 10:
            avg_size = sum(file_sizes) / len(file_sizes)
            large_files = [size for size in file_sizes if size > avg_size * 2]
            
            if len(large_files) / len(file_sizes) > 0.2:
                pattern = Pattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="structural",
                    description="Tendency to create large files",
                    confidence=len(large_files) / len(file_sizes),
                    frequency=len(large_files),
                    examples=[f"Large files (> {avg_size * 2:.0f} chars): {len(large_files)}/{len(file_sizes)}"],
                    metadata={"average_size": avg_size, "large_file_threshold": avg_size * 2}
                )
                patterns.append(pattern)
        
        # Analyze content structure patterns
        for indexed_file in self.data_indexer.indexed_files.values():
            content = indexed_file.content
            
            # Look for structured content patterns
            if "## " in content and "### " in content:
                heading_count = content.count("## ") + content.count("### ")
                if heading_count > 5:
                    pattern = Pattern(
                        pattern_id=str(uuid.uuid4()),
                        pattern_type="structural",
                        description="Structured content with multiple headings",
                        confidence=min(1.0, heading_count / 20),  # Normalize by expected max
                        frequency=heading_count,
                        examples=[f"File {indexed_file.file_name} has {heading_count} headings"],
                        metadata={"file_name": indexed_file.file_name, "heading_count": heading_count}
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def analyze_trends(self, days: int = 30) -> List[Trend]:
        """
        Analyze trends in consciousness data.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of trend analysis results
        """
        logger.info(f"Analyzing trends over {days} days")
        
        trends = []
        
        # Analyze confidence trends
        confidence_trends = self._analyze_confidence_trends(days)
        trends.extend(confidence_trends)
        
        # Analyze activity trends
        activity_trends = self._analyze_activity_trends(days)
        trends.extend(activity_trends)
        
        # Analyze learning trends
        learning_trends = self._analyze_learning_trends(days)
        trends.extend(learning_trends)
        
        # Store trends
        for trend in trends:
            self.trends[trend.trend_id] = trend
        
        logger.info(f"Analyzed {len(trends)} trends")
        return trends
    
    def _analyze_confidence_trends(self, days: int) -> List[Trend]:
        """Analyze confidence trends over time."""
        trends = []
        
        # Get confidence records from the specified period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        confidence_records = self.confidence_system.get_confidence_records(
            start_date=start_date,
            end_date=end_date
        )
        
        if len(confidence_records) < 10:
            return trends
        
        # Group by date and calculate daily averages
        daily_confidence = defaultdict(list)
        for record in confidence_records:
            record_date = datetime.fromisoformat(record.timestamp).date()
            daily_confidence[record_date].append(record.confidence_score)
        
        # Calculate daily averages
        daily_averages = []
        for date, scores in sorted(daily_confidence.items()):
            daily_averages.append({
                "date": date,
                "confidence": sum(scores) / len(scores),
                "count": len(scores)
            })
        
        if len(daily_averages) < 5:
            return trends
        
        # Calculate trend slope
        x_values = list(range(len(daily_averages)))
        y_values = [point["confidence"] for point in daily_averages]
        
        slope, r_squared = self._calculate_linear_trend(x_values, y_values)
        
        # Determine trend type
        if abs(slope) < 0.01:
            trend_type = "stable"
        elif slope > 0:
            trend_type = "increasing"
        else:
            trend_type = "decreasing"
        
        # Generate forecast
        forecast = self._generate_forecast(daily_averages, 7)  # 7 days ahead
        
        trend = Trend(
            trend_id=str(uuid.uuid4()),
            trend_type=trend_type,
            metric="confidence",
            start_date=start_date,
            end_date=end_date,
            slope=slope,
            r_squared=r_squared,
            confidence=min(1.0, r_squared),
            forecast=forecast,
            metadata={"data_points": len(daily_averages), "period_days": days}
        )
        
        trends.append(trend)
        return trends
    
    def _analyze_activity_trends(self, days: int) -> List[Trend]:
        """Analyze activity trends over time."""
        trends = []
        
        # Group files by date
        daily_counts = defaultdict(int)
        for indexed_file in self.data_indexer.indexed_files.values():
            file_date = datetime.fromtimestamp(indexed_file.last_modified).date()
            if file_date >= (datetime.now() - timedelta(days=days)).date():
                daily_counts[file_date] += 1
        
        if len(daily_counts) < 5:
            return trends
        
        # Calculate trend
        sorted_dates = sorted(daily_counts.keys())
        x_values = list(range(len(sorted_dates)))
        y_values = [daily_counts[date] for date in sorted_dates]
        
        slope, r_squared = self._calculate_linear_trend(x_values, y_values)
        
        # Determine trend type
        if abs(slope) < 0.5:
            trend_type = "stable"
        elif slope > 0:
            trend_type = "increasing"
        else:
            trend_type = "decreasing"
        
        # Generate forecast
        daily_activity = [{"date": date, "count": daily_counts[date]} for date in sorted_dates]
        forecast = self._generate_forecast(daily_activity, 7)
        
        trend = Trend(
            trend_id=str(uuid.uuid4()),
            trend_type=trend_type,
            metric="activity",
            start_date=sorted_dates[0],
            end_date=sorted_dates[-1],
            slope=slope,
            r_squared=r_squared,
            confidence=min(1.0, r_squared),
            forecast=forecast,
            metadata={"data_points": len(sorted_dates), "period_days": days}
        )
        
        trends.append(trend)
        return trends
    
    def _analyze_learning_trends(self, days: int) -> List[Trend]:
        """Analyze learning trends over time."""
        trends = []
        
        # Analyze learning milestones over time
        milestones = []
        for indexed_file in self.data_indexer.indexed_files.values():
            if indexed_file.file_type in ["thought_journal", "decision_log"]:
                content = indexed_file.content
                file_date = datetime.fromtimestamp(indexed_file.last_modified).date()
                
                # Count learning-related keywords
                learning_keywords = ["learn", "understand", "realize", "discover", "breakthrough", "insight"]
                learning_count = sum(content.lower().count(keyword) for keyword in learning_keywords)
                
                if learning_count > 0:
                    milestones.append({
                        "date": file_date,
                        "learning_score": learning_count
                    })
        
        if len(milestones) < 5:
            return trends
        
        # Group by date and sum learning scores
        daily_learning = defaultdict(int)
        for milestone in milestones:
            daily_learning[milestone["date"]] += milestone["learning_score"]
        
        # Calculate trend
        sorted_dates = sorted(daily_learning.keys())
        x_values = list(range(len(sorted_dates)))
        y_values = [daily_learning[date] for date in sorted_dates]
        
        slope, r_squared = self._calculate_linear_trend(x_values, y_values)
        
        # Determine trend type
        if abs(slope) < 0.1:
            trend_type = "stable"
        elif slope > 0:
            trend_type = "increasing"
        else:
            trend_type = "decreasing"
        
        # Generate forecast
        daily_learning_data = [{"date": date, "score": daily_learning[date]} for date in sorted_dates]
        forecast = self._generate_forecast(daily_learning_data, 7)
        
        trend = Trend(
            trend_id=str(uuid.uuid4()),
            trend_type=trend_type,
            metric="learning",
            start_date=sorted_dates[0],
            end_date=sorted_dates[-1],
            slope=slope,
            r_squared=r_squared,
            confidence=min(1.0, r_squared),
            forecast=forecast,
            metadata={"data_points": len(sorted_dates), "period_days": days}
        )
        
        trends.append(trend)
        return trends
    
    def _calculate_linear_trend(self, x_values: List[float], y_values: List[float]) -> Tuple[float, float]:
        """Calculate linear trend slope and R-squared."""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0, 0.0
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        sum_y2 = sum(y * y for y in y_values)
        
        # Calculate slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Calculate R-squared
        y_mean = sum_y / n
        ss_tot = sum((y - y_mean) ** 2 for y in y_values)
        ss_res = sum((y - (slope * x + (sum_y - slope * sum_x) / n)) ** 2 for x, y in zip(x_values, y_values))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return slope, max(0, r_squared)
    
    def _generate_forecast(self, data: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
        """Generate forecast for the next N days."""
        if len(data) < 2:
            return []
        
        # Simple linear forecast
        x_values = list(range(len(data)))
        y_values = [point["confidence"] if "confidence" in point else point.get("count", point.get("score", 0)) for point in data]
        
        slope, _ = self._calculate_linear_trend(x_values, y_values)
        
        forecast = []
        last_date = data[-1]["date"]
        
        for i in range(1, days + 1):
            forecast_value = y_values[-1] + slope * i
            forecast_date = last_date + timedelta(days=i)
            
            forecast.append({
                "date": forecast_date,
                "value": max(0, forecast_value)  # Ensure non-negative
            })
        
        return forecast
    
    def detect_anomalies(self) -> List[Anomaly]:
        """
        Detect anomalies in consciousness data.
        
        Returns:
            List of detected anomalies
        """
        logger.info("Detecting anomalies in consciousness data")
        
        anomalies = []
        
        # Detect confidence anomalies
        confidence_anomalies = self._detect_confidence_anomalies()
        anomalies.extend(confidence_anomalies)
        
        # Detect activity anomalies
        activity_anomalies = self._detect_activity_anomalies()
        anomalies.extend(activity_anomalies)
        
        # Detect content anomalies
        content_anomalies = self._detect_content_anomalies()
        anomalies.extend(content_anomalies)
        
        # Store anomalies
        for anomaly in anomalies:
            self.anomalies[anomaly.anomaly_id] = anomaly
        
        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies
    
    def _detect_confidence_anomalies(self) -> List[Anomaly]:
        """Detect anomalies in confidence data."""
        anomalies = []
        
        confidence_scores = [r.confidence_score for r in self.confidence_system.confidence_records.values()]
        
        if len(confidence_scores) < 10:
            return anomalies
        
        # Calculate statistics
        mean_confidence = statistics.mean(confidence_scores)
        std_confidence = statistics.stdev(confidence_scores) if len(confidence_scores) > 1 else 0
        
        # Detect outliers (more than 2 standard deviations from mean)
        threshold = 2 * std_confidence
        
        for record in self.confidence_system.confidence_records.values():
            if abs(record.confidence_score - mean_confidence) > threshold:
                severity = "high" if abs(record.confidence_score - mean_confidence) > 3 * std_confidence else "medium"
                
                anomaly = Anomaly(
                    anomaly_id=str(uuid.uuid4()),
                    anomaly_type="outlier",
                    description=f"Confidence score {record.confidence_score:.2f} is {threshold:.2f} standard deviations from mean",
                    severity=severity,
                    detected_at=datetime.fromisoformat(record.timestamp),
                    affected_data=[record.record_id],
                    explanation=f"Expected confidence around {mean_confidence:.2f} ± {std_confidence:.2f}",
                    metadata={"confidence_score": record.confidence_score, "mean": mean_confidence, "std": std_confidence}
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_activity_anomalies(self) -> List[Anomaly]:
        """Detect anomalies in activity data."""
        anomalies = []
        
        # Group files by date
        daily_counts = defaultdict(int)
        for indexed_file in self.data_indexer.indexed_files.values():
            file_date = datetime.fromtimestamp(indexed_file.last_modified).date()
            daily_counts[file_date] += 1
        
        if len(daily_counts) < 7:
            return anomalies
        
        # Calculate statistics
        counts = list(daily_counts.values())
        mean_count = statistics.mean(counts)
        std_count = statistics.stdev(counts) if len(counts) > 1 else 0
        
        # Detect unusual activity days
        threshold = 2 * std_count
        
        for date, count in daily_counts.items():
            if abs(count - mean_count) > threshold:
                severity = "high" if abs(count - mean_count) > 3 * std_count else "medium"
                
                anomaly = Anomaly(
                    anomaly_id=str(uuid.uuid4()),
                    anomaly_type="outlier",
                    description=f"Unusual activity on {date}: {count} files (expected ~{mean_count:.1f})",
                    severity=severity,
                    detected_at=datetime.combine(date, datetime.min.time()),
                    affected_data=[f"daily_activity_{date}"],
                    explanation=f"Expected activity around {mean_count:.1f} ± {std_count:.1f} files per day",
                    metadata={"file_count": count, "mean": mean_count, "std": std_count}
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_content_anomalies(self) -> List[Anomaly]:
        """Detect anomalies in content data."""
        anomalies = []
        
        # Analyze file sizes
        file_sizes = [len(indexed_file.content) for indexed_file in self.data_indexer.indexed_files.values()]
        
        if len(file_sizes) < 10:
            return anomalies
        
        # Calculate statistics
        mean_size = statistics.mean(file_sizes)
        std_size = statistics.stdev(file_sizes) if len(file_sizes) > 1 else 0
        
        # Detect unusually large or small files
        threshold = 2 * std_size
        
        for indexed_file in self.data_indexer.indexed_files.values():
            file_size = len(indexed_file.content)
            if abs(file_size - mean_size) > threshold:
                severity = "high" if abs(file_size - mean_size) > 3 * std_size else "medium"
                
                anomaly = Anomaly(
                    anomaly_id=str(uuid.uuid4()),
                    anomaly_type="outlier",
                    description=f"Unusual file size: {file_size} characters (expected ~{mean_size:.0f})",
                    severity=severity,
                    detected_at=datetime.fromtimestamp(indexed_file.last_modified),
                    affected_data=[indexed_file.file_path],
                    explanation=f"Expected file size around {mean_size:.0f} ± {std_size:.0f} characters",
                    metadata={"file_size": file_size, "mean": mean_size, "std": std_size}
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def analyze_correlations(self) -> List[Correlation]:
        """
        Analyze correlations between different variables.
        
        Returns:
            List of correlation analysis results
        """
        logger.info("Analyzing correlations in consciousness data")
        
        correlations = []
        
        # Analyze confidence vs file type correlations
        file_type_correlations = self._analyze_file_type_correlations()
        correlations.extend(file_type_correlations)
        
        # Analyze confidence vs time correlations
        time_correlations = self._analyze_time_correlations()
        correlations.extend(time_correlations)
        
        # Analyze content vs confidence correlations
        content_correlations = self._analyze_content_correlations()
        correlations.extend(content_correlations)
        
        # Analyze confidence vs time patterns
        confidence_time_correlations = self._analyze_confidence_time_correlations()
        correlations.extend(confidence_time_correlations)
        
        # Store correlations
        for correlation in correlations:
            self.correlations[correlation.correlation_id] = correlation
        
        logger.info(f"Analyzed {len(correlations)} correlations")
        return correlations
    
    def _analyze_file_type_correlations(self) -> List[Correlation]:
        """Analyze correlations between confidence and file types."""
        correlations = []
        
        # Group confidence records by file type
        confidence_by_type = defaultdict(list)
        for record in self.confidence_system.confidence_records.values():
            if record.file_path:
                file_type = Path(record.file_path).suffix[1:] if Path(record.file_path).suffix else "unknown"
                confidence_by_type[file_type].append(record.confidence_score)
        
        # Calculate correlations between different file types
        file_types = list(confidence_by_type.keys())
        
        for i, type1 in enumerate(file_types):
            for type2 in file_types[i+1:]:
                scores1 = confidence_by_type[type1]
                scores2 = confidence_by_type[type2]
                
                if len(scores1) >= 3 and len(scores2) >= 3:  # Lower threshold for more correlations
                    # Calculate correlation coefficient
                    correlation_coef = self._calculate_correlation(scores1, scores2)
                    
                    if abs(correlation_coef) > 0.2:  # Lower threshold for more correlations
                        significance = "high" if abs(correlation_coef) > 0.7 else "medium" if abs(correlation_coef) > 0.5 else "low"
                        relationship_type = "positive" if correlation_coef > 0 else "negative"
                        
                        correlation = Correlation(
                            correlation_id=str(uuid.uuid4()),
                            variable1=f"confidence_{type1}",
                            variable2=f"confidence_{type2}",
                            correlation_coefficient=correlation_coef,
                            p_value=0.05,  # Simplified p-value
                            significance=significance,
                            relationship_type=relationship_type,
                            metadata={"file_type1": type1, "file_type2": type2, "sample_size1": len(scores1), "sample_size2": len(scores2)}
                        )
                        correlations.append(correlation)
        
        return correlations
    
    def _analyze_time_correlations(self) -> List[Correlation]:
        """Analyze correlations between confidence and time."""
        correlations = []
        
        # Get confidence records with timestamps
        confidence_records = list(self.confidence_system.confidence_records.values())
        
        if len(confidence_records) < 10:
            return correlations
        
        # Extract time components
        hours = []
        weekdays = []
        confidence_scores = []
        
        for record in confidence_records:
            record_time = datetime.fromisoformat(record.timestamp)
            hours.append(record_time.hour)
            weekdays.append(record_time.weekday())
            confidence_scores.append(record.confidence_score)
        
        # Analyze hour vs confidence correlation
        hour_correlation = self._calculate_correlation(hours, confidence_scores)
        if abs(hour_correlation) > 0.3:
            significance = "high" if abs(hour_correlation) > 0.7 else "medium" if abs(hour_correlation) > 0.5 else "low"
            relationship_type = "positive" if hour_correlation > 0 else "negative"
            
            correlation = Correlation(
                correlation_id=str(uuid.uuid4()),
                variable1="hour_of_day",
                variable2="confidence",
                correlation_coefficient=hour_correlation,
                p_value=0.05,
                significance=significance,
                relationship_type=relationship_type,
                metadata={"sample_size": len(confidence_scores)}
            )
            correlations.append(correlation)
        
        # Analyze weekday vs confidence correlation
        weekday_correlation = self._calculate_correlation(weekdays, confidence_scores)
        if abs(weekday_correlation) > 0.3:
            significance = "high" if abs(weekday_correlation) > 0.7 else "medium" if abs(weekday_correlation) > 0.5 else "low"
            relationship_type = "positive" if weekday_correlation > 0 else "negative"
            
            correlation = Correlation(
                correlation_id=str(uuid.uuid4()),
                variable1="weekday",
                variable2="confidence",
                correlation_coefficient=weekday_correlation,
                p_value=0.05,
                significance=significance,
                relationship_type=relationship_type,
                metadata={"sample_size": len(confidence_scores)}
            )
            correlations.append(correlation)
        
        return correlations
    
    def _analyze_content_correlations(self) -> List[Correlation]:
        """Analyze correlations between content and confidence."""
        correlations = []
        
        # Analyze file size vs confidence correlation
        file_sizes = []
        confidence_scores = []
        
        for record in self.confidence_system.confidence_records.values():
            if record.file_path and record.file_path in self.data_indexer.indexed_files:
                indexed_file = self.data_indexer.indexed_files[record.file_path]
                file_sizes.append(len(indexed_file.content))
                confidence_scores.append(record.confidence_score)
        
        if len(file_sizes) >= 10:
            size_correlation = self._calculate_correlation(file_sizes, confidence_scores)
            if abs(size_correlation) > 0.3:
                significance = "high" if abs(size_correlation) > 0.7 else "medium" if abs(size_correlation) > 0.5 else "low"
                relationship_type = "positive" if size_correlation > 0 else "negative"
                
                correlation = Correlation(
                    correlation_id=str(uuid.uuid4()),
                    variable1="file_size",
                    variable2="confidence",
                    correlation_coefficient=size_correlation,
                    p_value=0.05,
                    significance=significance,
                    relationship_type=relationship_type,
                    metadata={"sample_size": len(file_sizes)}
                )
                correlations.append(correlation)
        
        return correlations
    
    def _analyze_confidence_time_correlations(self) -> List[Correlation]:
        """Analyze correlations between confidence and time patterns."""
        correlations = []
        
        # Get confidence records with timestamps
        confidence_records = list(self.confidence_system.confidence_records.values())
        
        if len(confidence_records) < 10:
            return correlations
        
        # Extract time components and confidence scores
        timestamps = []
        confidence_scores = []
        
        for record in confidence_records:
            if hasattr(record, 'timestamp') and record.timestamp:
                try:
                    # Convert timestamp to datetime if it's a float
                    if isinstance(record.timestamp, (int, float)):
                        dt = datetime.fromtimestamp(record.timestamp)
                    elif isinstance(record.timestamp, str):
                        # Try to parse string timestamp
                        try:
                            dt = datetime.fromisoformat(record.timestamp.replace('Z', '+00:00'))
                        except ValueError:
                            # Try parsing as timestamp
                            dt = datetime.fromtimestamp(float(record.timestamp))
                    else:
                        dt = record.timestamp
                    
                    # Extract time components
                    hour = dt.hour
                    day_of_week = dt.weekday()
                    day_of_month = dt.day
                    
                    timestamps.append({
                        'hour': hour,
                        'day_of_week': day_of_week,
                        'day_of_month': day_of_month
                    })
                    confidence_scores.append(record.confidence_score)
                except (ValueError, TypeError):
                    continue
        
        if len(timestamps) < 5:
            return correlations
        
        # Analyze hour vs confidence correlation
        hours = [t['hour'] for t in timestamps]
        if len(set(hours)) > 1:  # Need at least 2 different hours
            correlation_coef = self._calculate_correlation(hours, confidence_scores)
            if abs(correlation_coef) > 0.2:
                significance = "high" if abs(correlation_coef) > 0.7 else "medium" if abs(correlation_coef) > 0.5 else "low"
                relationship_type = "positive" if correlation_coef > 0 else "negative"
                
                correlation = Correlation(
                    correlation_id=str(uuid.uuid4()),
                    variable1="hour_of_day",
                    variable2="confidence_score",
                    correlation_coefficient=correlation_coef,
                    p_value=0.05,
                    significance=significance,
                    relationship_type=relationship_type,
                    metadata={"sample_size": len(hours), "analysis_type": "time_pattern"}
                )
                correlations.append(correlation)
        
        # Analyze day of week vs confidence correlation
        days = [t['day_of_week'] for t in timestamps]
        if len(set(days)) > 1:  # Need at least 2 different days
            correlation_coef = self._calculate_correlation(days, confidence_scores)
            if abs(correlation_coef) > 0.2:
                significance = "high" if abs(correlation_coef) > 0.7 else "medium" if abs(correlation_coef) > 0.5 else "low"
                relationship_type = "positive" if correlation_coef > 0 else "negative"
                
                correlation = Correlation(
                    correlation_id=str(uuid.uuid4()),
                    variable1="day_of_week",
                    variable2="confidence_score",
                    correlation_coefficient=correlation_coef,
                    p_value=0.05,
                    significance=significance,
                    relationship_type=relationship_type,
                    metadata={"sample_size": len(days), "analysis_type": "time_pattern"}
                )
                correlations.append(correlation)
        
        return correlations
    
    def _calculate_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        sum_y2 = sum(y * y for y in y_values)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def generate_insights(self) -> List[Insight]:
        """
        Generate insights from all analysis results.
        
        Returns:
            List of generated insights
        """
        logger.info("Generating insights from analysis results")
        
        insights = []
        
        # Generate pattern insights
        pattern_insights = self._generate_pattern_insights()
        insights.extend(pattern_insights)
        
        # Generate trend insights
        trend_insights = self._generate_trend_insights()
        insights.extend(trend_insights)
        
        # Generate anomaly insights
        anomaly_insights = self._generate_anomaly_insights()
        insights.extend(anomaly_insights)
        
        # Generate correlation insights
        correlation_insights = self._generate_correlation_insights()
        insights.extend(correlation_insights)
        
        # Store insights
        for insight in insights:
            self.insights[insight.insight_id] = insight
        
        logger.info(f"Generated {len(insights)} insights")
        return insights
    
    def _generate_pattern_insights(self) -> List[Insight]:
        """Generate insights from discovered patterns."""
        insights = []
        
        for pattern in self.patterns.values():
            if pattern.confidence > 0.7:  # Only high-confidence patterns
                insight = Insight(
                    insight_id=str(uuid.uuid4()),
                    insight_type="pattern",
                    title=f"Pattern: {pattern.description}",
                    description=f"Discovered a {pattern.pattern_type} pattern with {pattern.confidence:.1%} confidence. This pattern appears {pattern.frequency} times.",
                    confidence=pattern.confidence,
                    impact="medium",
                    actionable=True,
                    recommendations=[
                        f"Consider leveraging this {pattern.pattern_type} pattern for optimization",
                        f"Monitor for changes in this pattern over time"
                    ],
                    metadata={"pattern_id": pattern.pattern_id, "pattern_type": pattern.pattern_type}
                )
                insights.append(insight)
        
        return insights
    
    def _generate_trend_insights(self) -> List[Insight]:
        """Generate insights from trend analysis."""
        insights = []
        
        for trend in self.trends.values():
            if trend.confidence > 0.6:  # Only confident trends
                if trend.trend_type == "increasing":
                    title = f"Positive Trend: {trend.metric} is increasing"
                    description = f"The {trend.metric} shows a positive trend with {trend.confidence:.1%} confidence. This suggests continued growth in this area."
                    recommendations = [
                        "Continue current practices that support this positive trend",
                        "Monitor for any changes that might affect this trend"
                    ]
                elif trend.trend_type == "decreasing":
                    title = f"Negative Trend: {trend.metric} is decreasing"
                    description = f"The {trend.metric} shows a negative trend with {trend.confidence:.1%} confidence. This may require attention."
                    recommendations = [
                        "Investigate factors contributing to this decline",
                        "Consider interventions to reverse this trend"
                    ]
                else:
                    title = f"Stable Trend: {trend.metric} is stable"
                    description = f"The {trend.metric} shows a stable trend with {trend.confidence:.1%} confidence. This indicates consistent performance."
                    recommendations = [
                        "Maintain current practices",
                        "Look for opportunities to improve beyond current stability"
                    ]
                
                insight = Insight(
                    insight_id=str(uuid.uuid4()),
                    insight_type="trend",
                    title=title,
                    description=description,
                    confidence=trend.confidence,
                    impact="high" if trend.trend_type in ["increasing", "decreasing"] else "medium",
                    actionable=True,
                    recommendations=recommendations,
                    metadata={"trend_id": trend.trend_id, "trend_type": trend.trend_type, "metric": trend.metric}
                )
                insights.append(insight)
        
        return insights
    
    def _generate_anomaly_insights(self) -> List[Insight]:
        """Generate insights from detected anomalies."""
        insights = []
        
        for anomaly in self.anomalies.values():
            if anomaly.severity in ["high", "critical"]:
                insight = Insight(
                    insight_id=str(uuid.uuid4()),
                    insight_type="anomaly",
                    title=f"Anomaly Detected: {anomaly.description}",
                    description=f"An {anomaly.anomaly_type} anomaly was detected with {anomaly.severity} severity. {anomaly.explanation}",
                    confidence=0.8,  # High confidence for anomalies
                    impact=anomaly.severity,
                    actionable=True,
                    recommendations=[
                        "Investigate the root cause of this anomaly",
                        "Consider if this represents a new pattern or an error",
                        "Monitor for similar anomalies in the future"
                    ],
                    metadata={"anomaly_id": anomaly.anomaly_id, "anomaly_type": anomaly.anomaly_type, "severity": anomaly.severity}
                )
                insights.append(insight)
        
        return insights
    
    def _generate_correlation_insights(self) -> List[Insight]:
        """Generate insights from correlation analysis."""
        insights = []
        
        for correlation in self.correlations.values():
            if correlation.significance in ["high", "medium"]:
                insight = Insight(
                    insight_id=str(uuid.uuid4()),
                    insight_type="correlation",
                    title=f"Correlation: {correlation.variable1} and {correlation.variable2}",
                    description=f"Found a {correlation.relationship_type} correlation ({correlation.correlation_coefficient:.2f}) between {correlation.variable1} and {correlation.variable2} with {correlation.significance} significance.",
                    confidence=correlation.correlation_coefficient,
                    impact="medium",
                    actionable=True,
                    recommendations=[
                        f"Consider how {correlation.variable1} affects {correlation.variable2}",
                        f"Use this relationship to predict or influence outcomes",
                        "Monitor for changes in this correlation over time"
                    ],
                    metadata={"correlation_id": correlation.correlation_id, "variables": [correlation.variable1, correlation.variable2]}
                )
                insights.append(insight)
        
        return insights
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get a summary of all analytics results."""
        return {
            "patterns": {
                "total": len(self.patterns),
                "by_type": Counter(p.pattern_type for p in self.patterns.values()),
                "high_confidence": len([p for p in self.patterns.values() if p.confidence > 0.7])
            },
            "trends": {
                "total": len(self.trends),
                "by_type": Counter(t.trend_type for t in self.trends.values()),
                "high_confidence": len([t for t in self.trends.values() if t.confidence > 0.6])
            },
            "anomalies": {
                "total": len(self.anomalies),
                "by_severity": Counter(a.severity for a in self.anomalies.values()),
                "by_type": Counter(a.anomaly_type for a in self.anomalies.values())
            },
            "correlations": {
                "total": len(self.correlations),
                "by_significance": Counter(c.significance for c in self.correlations.values()),
                "by_relationship": Counter(c.relationship_type for c in self.correlations.values())
            },
            "insights": {
                "total": len(self.insights),
                "by_type": Counter(i.insight_type for i in self.insights.values()),
                "actionable": len([i for i in self.insights.values() if i.actionable]),
                "high_impact": len([i for i in self.insights.values() if i.impact == "high"])
            }
        }
