"""
Production Configuration for CMC Service

This module provides production-ready configuration for the CMC service,
including environment variables, logging, monitoring, and deployment settings.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    path: Path
    max_connections: int = 10
    connection_timeout: int = 30
    query_timeout: int = 60
    enable_wal_mode: bool = True
    enable_foreign_keys: bool = True
    journal_mode: str = "WAL"
    synchronous: str = "NORMAL"
    cache_size: int = -2000  # 2GB cache
    temp_store: str = "MEMORY"
    mmap_size: int = 268435456  # 256MB


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[Path] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enable_health_checks: bool = True
    health_check_interval: int = 30  # seconds
    enable_metrics: bool = True
    metrics_retention_days: int = 30
    enable_alerts: bool = True
    alert_thresholds: Dict[str, float] = None
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                "memory_usage_percent": 80.0,
                "cpu_usage_percent": 70.0,
                "response_time_ms": 1000.0,
                "error_rate_percent": 5.0
            }


@dataclass
class PerformanceConfig:
    """Performance configuration"""
    enable_connection_pooling: bool = True
    enable_query_caching: bool = True
    cache_size: int = 1000
    cache_ttl: int = 300  # 5 minutes
    enable_batch_processing: bool = True
    batch_size: int = 100
    enable_parallel_processing: bool = True
    max_workers: int = 4


@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_encryption: bool = True
    encryption_key: Optional[str] = None
    enable_audit_logging: bool = True
    enable_access_control: bool = True
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600  # 1 hour


@dataclass
class ProductionConfig:
    """Complete production configuration"""
    environment: Environment
    database: DatabaseConfig
    logging: LoggingConfig
    monitoring: MonitoringConfig
    performance: PerformanceConfig
    security: SecurityConfig
    
    # Service configuration
    service_name: str = "cmc-service"
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Data paths
    data_dir: Path = Path("data")
    backup_dir: Path = Path("backups")
    log_dir: Path = Path("logs")
    
    def __post_init__(self):
        """Ensure directories exist"""
        self.data_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)


def load_config() -> ProductionConfig:
    """Load configuration from environment variables"""
    
    # Determine environment
    env_str = os.getenv("CMC_ENVIRONMENT", "development").lower()
    environment = Environment(env_str) if env_str in [e.value for e in Environment] else Environment.DEVELOPMENT
    
    # Database configuration
    db_path = Path(os.getenv("CMC_DB_PATH", "data/cmc.db"))
    database = DatabaseConfig(
        path=db_path,
        max_connections=int(os.getenv("CMC_MAX_CONNECTIONS", "10")),
        connection_timeout=int(os.getenv("CMC_CONNECTION_TIMEOUT", "30")),
        query_timeout=int(os.getenv("CMC_QUERY_TIMEOUT", "60")),
        enable_wal_mode=os.getenv("CMC_ENABLE_WAL", "true").lower() == "true",
        enable_foreign_keys=os.getenv("CMC_ENABLE_FOREIGN_KEYS", "true").lower() == "true",
        journal_mode=os.getenv("CMC_JOURNAL_MODE", "WAL"),
        synchronous=os.getenv("CMC_SYNCHRONOUS", "NORMAL"),
        cache_size=int(os.getenv("CMC_CACHE_SIZE", "-2000")),
        temp_store=os.getenv("CMC_TEMP_STORE", "MEMORY"),
        mmap_size=int(os.getenv("CMC_MMAP_SIZE", "268435456"))
    )
    
    # Logging configuration
    log_file = Path(os.getenv("CMC_LOG_FILE", "logs/cmc.log"))
    logging_config = LoggingConfig(
        level=os.getenv("CMC_LOG_LEVEL", "INFO"),
        format=os.getenv("CMC_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        file_path=log_file if os.getenv("CMC_LOG_TO_FILE", "true").lower() == "true" else None,
        max_file_size=int(os.getenv("CMC_LOG_MAX_SIZE", str(10 * 1024 * 1024))),
        backup_count=int(os.getenv("CMC_LOG_BACKUP_COUNT", "5")),
        enable_console=os.getenv("CMC_LOG_CONSOLE", "true").lower() == "true",
        enable_file=os.getenv("CMC_LOG_TO_FILE", "true").lower() == "true"
    )
    
    # Monitoring configuration
    monitoring = MonitoringConfig(
        enable_health_checks=os.getenv("CMC_ENABLE_HEALTH_CHECKS", "true").lower() == "true",
        health_check_interval=int(os.getenv("CMC_HEALTH_CHECK_INTERVAL", "30")),
        enable_metrics=os.getenv("CMC_ENABLE_METRICS", "true").lower() == "true",
        metrics_retention_days=int(os.getenv("CMC_METRICS_RETENTION_DAYS", "30")),
        enable_alerts=os.getenv("CMC_ENABLE_ALERTS", "true").lower() == "true"
    )
    
    # Performance configuration
    performance = PerformanceConfig(
        enable_connection_pooling=os.getenv("CMC_ENABLE_CONNECTION_POOLING", "true").lower() == "true",
        enable_query_caching=os.getenv("CMC_ENABLE_QUERY_CACHING", "true").lower() == "true",
        cache_size=int(os.getenv("CMC_CACHE_SIZE", "1000")),
        cache_ttl=int(os.getenv("CMC_CACHE_TTL", "300")),
        enable_batch_processing=os.getenv("CMC_ENABLE_BATCH_PROCESSING", "true").lower() == "true",
        batch_size=int(os.getenv("CMC_BATCH_SIZE", "100")),
        enable_parallel_processing=os.getenv("CMC_ENABLE_PARALLEL_PROCESSING", "true").lower() == "true",
        max_workers=int(os.getenv("CMC_MAX_WORKERS", "4"))
    )
    
    # Security configuration
    security = SecurityConfig(
        enable_encryption=os.getenv("CMC_ENABLE_ENCRYPTION", "true").lower() == "true",
        encryption_key=os.getenv("CMC_ENCRYPTION_KEY"),
        enable_audit_logging=os.getenv("CMC_ENABLE_AUDIT_LOGGING", "true").lower() == "true",
        enable_access_control=os.getenv("CMC_ENABLE_ACCESS_CONTROL", "true").lower() == "true",
        max_request_size=int(os.getenv("CMC_MAX_REQUEST_SIZE", str(10 * 1024 * 1024))),
        rate_limit_requests=int(os.getenv("CMC_RATE_LIMIT_REQUESTS", "1000")),
        rate_limit_window=int(os.getenv("CMC_RATE_LIMIT_WINDOW", "3600"))
    )
    
    return ProductionConfig(
        environment=environment,
        database=database,
        logging=logging_config,
        monitoring=monitoring,
        performance=performance,
        security=security,
        service_name=os.getenv("CMC_SERVICE_NAME", "cmc-service"),
        version=os.getenv("CMC_VERSION", "1.0.0"),
        host=os.getenv("CMC_HOST", "0.0.0.0"),
        port=int(os.getenv("CMC_PORT", "8000")),
        workers=int(os.getenv("CMC_WORKERS", "1")),
        data_dir=Path(os.getenv("CMC_DATA_DIR", "data")),
        backup_dir=Path(os.getenv("CMC_BACKUP_DIR", "backups")),
        log_dir=Path(os.getenv("CMC_LOG_DIR", "logs"))
    )


def setup_logging(config: ProductionConfig) -> None:
    """Setup logging based on configuration"""
    
    # Create formatter
    formatter = logging.Formatter(config.logging.format)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.logging.level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if config.logging.enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if config.logging.enable_file and config.logging.file_path:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            config.logging.file_path,
            maxBytes=config.logging.max_file_size,
            backupCount=config.logging.backup_count
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_database_url(config: ProductionConfig) -> str:
    """Get database URL for the configuration"""
    return f"sqlite:///{config.database.path}"


def validate_config(config: ProductionConfig) -> bool:
    """Validate configuration"""
    errors = []
    
    # Check database path
    if not config.database.path.parent.exists():
        errors.append(f"Database directory does not exist: {config.database.path.parent}")
    
    # Check log directory
    if not config.log_dir.exists():
        errors.append(f"Log directory does not exist: {config.log_dir}")
    
    # Check security
    if config.security.enable_encryption and not config.security.encryption_key:
        errors.append("Encryption enabled but no encryption key provided")
    
    # Check performance
    if config.performance.max_workers < 1:
        errors.append("Max workers must be at least 1")
    
    if errors:
        for error in errors:
            logging.error(f"Configuration error: {error}")
        return False
    
    return True


# Default configuration for development
DEFAULT_CONFIG = ProductionConfig(
    environment=Environment.DEVELOPMENT,
    database=DatabaseConfig(path=Path("data/cmc.db")),
    logging=LoggingConfig(),
    monitoring=MonitoringConfig(),
    performance=PerformanceConfig(),
    security=SecurityConfig()
)
