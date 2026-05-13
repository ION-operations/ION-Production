"""
Production Deployment Script for CMC Service

This script handles production deployment, including:
- Configuration validation
- Database initialization
- Service startup
- Health checks
- Monitoring setup
"""

import os
import sys
import time
import signal
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

from production_config import load_config, setup_logging, validate_config, get_database_url
from monitoring.health_check import initialize_health_checking, get_health_status


# NL_TAG: VIF-MODEL-001 | CMC Service deployment manager | class CMCDeployment | []
class CMCDeployment:
    """CMC Service deployment manager"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config = load_config()
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        
        # Setup logging
        setup_logging(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize health checking
        self.health_checker = None
    
    def validate_environment(self) -> bool:
        """Validate deployment environment"""
        self.logger.info("Validating deployment environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.logger.error("Python 3.8+ required")
            return False
        
        # Check required packages
        required_packages = [
            "fastapi", "uvicorn", "sqlite3", "pydantic", 
            "psutil", "pathlib", "datetime"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                self.logger.error(f"Required package not found: {package}")
                return False
        
        # Validate configuration
        if not validate_config(self.config):
            self.logger.error("Configuration validation failed")
            return False
        
        self.logger.info("Environment validation passed")
        return True
    
    def initialize_database(self) -> bool:
        """Initialize database"""
        self.logger.info("Initializing database...")
        
        try:
            # Ensure database directory exists
            self.config.database.path.parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize database with proper settings
            from repository import AtomRepository, SQLiteConfig
            
            db_config = SQLiteConfig(
                path=self.config.database.path,
                enable_wal_mode=self.config.database.enable_wal_mode,
                enable_foreign_keys=self.config.database.enable_foreign_keys,
                journal_mode=self.config.database.journal_mode,
                synchronous=self.config.database.synchronous,
                cache_size=self.config.database.cache_size,
                temp_store=self.config.database.temp_store,
                mmap_size=self.config.database.mmap_size
            )
            
            # Create repository and initialize
            repo = AtomRepository(db_config)
            repo.initialize()
            repo.close()
            
            self.logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False
    
    def start_service(self) -> bool:
        """Start the CMC service"""
        self.logger.info("Starting CMC service...")
        
        try:
            # Build uvicorn command
            cmd = [
                "uvicorn",
                "api:app",
                "--host", self.config.host,
                "--port", str(self.config.port),
                "--workers", str(self.config.workers),
                "--log-level", self.config.logging.level.lower()
            ]
            
            # Add production-specific options
            if self.config.environment == Environment.PRODUCTION:
                cmd.extend([
                    "--access-log",
                    "--use-colors", "false"
                ])
            
            # Start process
            self.process = subprocess.Popen(
                cmd,
                cwd=Path(__file__).parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for service to start
            time.sleep(5)
            
            # Check if process is running
            if self.process.poll() is None:
                self.running = True
                self.logger.info(f"CMC service started on {self.config.host}:{self.config.port}")
                return True
            else:
                stdout, stderr = self.process.communicate()
                self.logger.error(f"Service failed to start. stdout: {stdout}, stderr: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            return False
    
    def stop_service(self) -> bool:
        """Stop the CMC service"""
        self.logger.info("Stopping CMC service...")
        
        if self.process and self.process.poll() is None:
            try:
                # Send SIGTERM
                self.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    # Force kill if not responding
                    self.process.kill()
                    self.process.wait()
                
                self.running = False
                self.logger.info("CMC service stopped")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to stop service: {e}")
                return False
        
        return True
    
    def health_check(self) -> bool:
        """Perform health check"""
        if not self.health_checker:
            return False
        
        try:
            health_status = self.health_checker.get_health_summary()
            status = health_status.get("status", "unknown")
            
            if status == "healthy":
                self.logger.info("Health check passed")
                return True
            else:
                self.logger.warning(f"Health check failed: {status}")
                return False
                
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
            return False
    
    def monitor_service(self) -> None:
        """Monitor service health"""
        self.logger.info("Starting service monitoring...")
        
        while self.running:
            try:
                # Check if process is still running
                if self.process and self.process.poll() is not None:
                    self.logger.error("Service process died unexpectedly")
                    self.running = False
                    break
                
                # Perform health check
                if not self.health_check():
                    self.logger.warning("Health check failed, but continuing monitoring")
                
                # Wait for next check
                time.sleep(self.config.monitoring.health_check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(5)
    
    def deploy(self) -> bool:
        """Complete deployment process"""
        self.logger.info("Starting CMC service deployment...")
        
        try:
            # Step 1: Validate environment
            if not self.validate_environment():
                return False
            
            # Step 2: Initialize database
            if not self.initialize_database():
                return False
            
            # Step 3: Start service
            if not self.start_service():
                return False
            
            # Step 4: Initialize health checking
            # Note: This would need the actual server instance
            # self.health_checker = initialize_health_checking(server_instance)
            
            # Step 5: Monitor service
            self.monitor_service()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            return False
        finally:
            # Cleanup
            self.stop_service()
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.stop_service()
        sys.exit(0)


# NL_TAG: VIF-UTIL-001 | Main deployment function | main() | []
def main():
    # NL_TAG: VIF-UTIL-002 |   init   | __init__(self, config_path) | []
    def __init__(self, config_path: Optional[Path] = None):
        self.config = load_config()
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        
        # Setup logging
        setup_logging(self.config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize health checking
        self.health_checker = None
    
    # NL_TAG: VIF-UTIL-003 | Validate deployment environment | validate_environment(self) | []
    # NL_TAG_SPEC: VIF-SPEC-001 | Validates validate_environment specification | validate_environment | [spec_file_TBD]
    def validate_environment(self) -> bool:
        """Validate deployment environment"""
        self.logger.info("Validating deployment environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.logger.error("Python 3.8+ required")
            return False
        
        # Check required packages
        required_packages = [
            "fastapi", "uvicorn", "sqlite3", "pydantic", 
            "psutil", "pathlib", "datetime"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                self.logger.error(f"Required package not found: {package}")
                return False
        
        # Validate configuration
        if not validate_config(self.config):
            self.logger.error("Configuration validation failed")
            return False
        
        self.logger.info("Environment validation passed")
        return True
    
    # NL_TAG: VIF-UTIL-004 | Initialize database | initialize_database(self) | []
    def initialize_database(self) -> bool:
        """Initialize database"""
        self.logger.info("Initializing database...")
        
        try:
            # Ensure database directory exists
            self.config.database.path.parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize database with proper settings
            from repository import AtomRepository, SQLiteConfig
            
            db_config = SQLiteConfig(
                path=self.config.database.path,
                enable_wal_mode=self.config.database.enable_wal_mode,
                enable_foreign_keys=self.config.database.enable_foreign_keys,
                journal_mode=self.config.database.journal_mode,
                synchronous=self.config.database.synchronous,
                cache_size=self.config.database.cache_size,
                temp_store=self.config.database.temp_store,
                mmap_size=self.config.database.mmap_size
            )
            
            # Create repository and initialize
            repo = AtomRepository(db_config)
            repo.initialize()
            repo.close()
            
            self.logger.info("Database initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False
    
    # NL_TAG: VIF-UTIL-005 | Start the CMC service | start_service(self) | []
    def start_service(self) -> bool:
        """Start the CMC service"""
        self.logger.info("Starting CMC service...")
        
        try:
            # Build uvicorn command
            cmd = [
                "uvicorn",
                "api:app",
                "--host", self.config.host,
                "--port", str(self.config.port),
                "--workers", str(self.config.workers),
                "--log-level", self.config.logging.level.lower()
            ]
            
            # Add production-specific options
            if self.config.environment == Environment.PRODUCTION:
                cmd.extend([
                    "--access-log",
                    "--use-colors", "false"
                ])
            
            # Start process
            self.process = subprocess.Popen(
                cmd,
                cwd=Path(__file__).parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for service to start
            time.sleep(5)
            
            # Check if process is running
            if self.process.poll() is None:
                self.running = True
                self.logger.info(f"CMC service started on {self.config.host}:{self.config.port}")
                return True
            else:
                stdout, stderr = self.process.communicate()
                self.logger.error(f"Service failed to start. stdout: {stdout}, stderr: {stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start service: {e}")
            return False
    
    # NL_TAG: VIF-UTIL-006 | Stop the CMC service | stop_service(self) | []
    def stop_service(self) -> bool:
        """Stop the CMC service"""
        self.logger.info("Stopping CMC service...")
        
        if self.process and self.process.poll() is None:
            try:
                # Send SIGTERM
                self.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    # Force kill if not responding
                    self.process.kill()
                    self.process.wait()
                
                self.running = False
                self.logger.info("CMC service stopped")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to stop service: {e}")
                return False
        
        return True
    
    # NL_TAG: VIF-UTIL-007 | Perform health check | health_check(self) | []
    # NL_TAG_SPEC: VIF-SPEC-002 | Validates health_check specification | health_check | [spec_file_TBD]
    def health_check(self) -> bool:
        """Perform health check"""
        if not self.health_checker:
            return False
        
        try:
            health_status = self.health_checker.get_health_summary()
            status = health_status.get("status", "unknown")
            
            if status == "healthy":
                self.logger.info("Health check passed")
                return True
            else:
                self.logger.warning(f"Health check failed: {status}")
                return False
                
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
            return False
    
    # NL_TAG: VIF-UTIL-008 | Monitor service health | monitor_service(self) | []
    def monitor_service(self) -> None:
        """Monitor service health"""
        self.logger.info("Starting service monitoring...")
        
        while self.running:
            try:
                # Check if process is still running
                if self.process and self.process.poll() is not None:
                    self.logger.error("Service process died unexpectedly")
                    self.running = False
                    break
                
                # Perform health check
                if not self.health_check():
                    self.logger.warning("Health check failed, but continuing monitoring")
                
                # Wait for next check
                time.sleep(self.config.monitoring.health_check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(5)
    
    # NL_TAG: VIF-UTIL-009 | Complete deployment process | deploy(self) | []
    def deploy(self) -> bool:
        """Complete deployment process"""
        self.logger.info("Starting CMC service deployment...")
        
        try:
            # Step 1: Validate environment
            if not self.validate_environment():
                return False
            
            # Step 2: Initialize database
            if not self.initialize_database():
                return False
            
            # Step 3: Start service
            if not self.start_service():
                return False
            
            # Step 4: Initialize health checking
            # Note: This would need the actual server instance
            # self.health_checker = initialize_health_checking(server_instance)
            
            # Step 5: Monitor service
            self.monitor_service()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            return False
        finally:
            # Cleanup
            self.stop_service()
    
    # NL_TAG: VIF-UTIL-010 | Handle shutdown signals | signal_handler(self, signum, frame) | []
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.stop_service()
        sys.exit(0)


def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="Deploy CMC Service")
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--validate-only", action="store_true", help="Only validate configuration")
    parser.add_argument("--init-db-only", action="store_true", help="Only initialize database")
    
    args = parser.parse_args()
    
    # Create deployment instance
    deployment = CMCDeployment(args.config)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, deployment.signal_handler)
    signal.signal(signal.SIGTERM, deployment.signal_handler)
    
    try:
        if args.validate_only:
            # Only validate
            if deployment.validate_environment():
                print("Configuration validation passed")
                sys.exit(0)
            else:
                print("Configuration validation failed")
                sys.exit(1)
        
        elif args.init_db_only:
            # Only initialize database
            if deployment.initialize_database():
                print("Database initialization completed")
                sys.exit(0)
            else:
                print("Database initialization failed")
                sys.exit(1)
        
        else:
            # Full deployment
            if deployment.deploy():
                print("Deployment completed successfully")
                sys.exit(0)
            else:
                print("Deployment failed")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Deployment error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
