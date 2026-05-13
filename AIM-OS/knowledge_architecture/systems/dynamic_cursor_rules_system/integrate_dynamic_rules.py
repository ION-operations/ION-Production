#!/usr/bin/env python3
"""
Dynamic Cursor Rules Integration Script
Integrates the dynamic rule system with Cursor IDE and AIM-OS protocols.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dynamic_rule_loader import DynamicRuleLoader, ContextProfile

class DynamicRulesIntegrator:
    """Integrates dynamic rules with AIM-OS and Cursor IDE"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.rules_system_path = self.project_root / "knowledge_architecture" / "systems" / "dynamic_cursor_rules_system"
        self.cursor_rules_path = self.project_root / ".cursorrules"
        self.loader = DynamicRuleLoader(str(self.rules_system_path / "rule_partitions"))
        
    def detect_aim_os_context(self) -> ContextProfile:
        """Detect if we're in an AIM-OS project context"""
        # Check for AIM-OS indicators
        aim_os_indicators = [
            "goals/GOAL_TREE.yaml",
            "knowledge_architecture/",
            "packages/",
            "AETHER_MEMORY/"
        ]
        
        is_aim_os = any((self.project_root / indicator).exists() for indicator in aim_os_indicators)
        
        if is_aim_os:
            return ContextProfile(
                project_type="aim_os",
                task_type="development",
                protocol_required=["l0_l4", "mcp_tools", "lucid"],
                session_state="active",
                user_preference="comprehensive",
                confidence_level=0.8,
                complexity_level="medium"
            )
        else:
            return ContextProfile(
                project_type="general",
                task_type="development",
                protocol_required=[],
                session_state="active",
                user_preference="standard",
                confidence_level=0.8,
                complexity_level="medium"
            )
    
    def generate_aim_os_rules(self) -> str:
        """Generate rules specifically for AIM-OS development"""
        context = self.detect_aim_os_context()
        return self.loader.generate_cursor_rules(context)
    
    def generate_contextual_rules(self, user_input: str = "", environment_data: dict = None) -> str:
        """Generate rules based on specific context"""
        context = self.loader.analyze_context(user_input, environment_data)
        return self.loader.generate_cursor_rules(context)
    
    def install_dynamic_rules(self, backup_existing: bool = True) -> bool:
        """Install the dynamic rules system"""
        try:
            # Backup existing .cursorrules if it exists
            if backup_existing and self.cursor_rules_path.exists():
                backup_path = self.cursor_rules_path.with_suffix('.cursorrules.backup')
                self.cursor_rules_path.rename(backup_path)
                print(f"Backed up existing .cursorrules to {backup_path}")
            
            # Generate AIM-OS specific rules
            rules_content = self.generate_aim_os_rules()
            
            # Save to .cursorrules
            with open(self.cursor_rules_path, 'w', encoding='utf-8') as f:
                f.write(rules_content)
            
            print(f"Dynamic rules installed to {self.cursor_rules_path}")
            print(f"Loaded partitions: {self.loader.get_loaded_partitions()}")
            print(f"Memory usage: {self.loader.get_memory_usage()}KB")
            
            return True
            
        except Exception as e:
            print(f"Error installing dynamic rules: {e}")
            return False
    
    def update_rules_for_context(self, user_input: str, environment_data: dict = None) -> bool:
        """Update rules based on new context"""
        try:
            rules_content = self.generate_contextual_rules(user_input, environment_data)
            
            with open(self.cursor_rules_path, 'w', encoding='utf-8') as f:
                f.write(rules_content)
            
            print(f"Rules updated for context: {user_input[:50]}...")
            print(f"Loaded partitions: {self.loader.get_loaded_partitions()}")
            
            return True
            
        except Exception as e:
            print(f"Error updating rules: {e}")
            return False
    
    def create_rule_management_script(self) -> str:
        """Create a script for managing dynamic rules"""
        script_content = '''#!/usr/bin/env python3
"""
Dynamic Rules Management Script
Use this script to manage Cursor IDE rules dynamically.
"""

import sys
import os
from pathlib import Path

# Add the dynamic rules system to path
sys.path.append(str(Path(__file__).parent))

from dynamic_rule_loader import DynamicRuleLoader

def main():
    """Main function for rule management"""
    if len(sys.argv) < 2:
        print("Usage: python manage_rules.py <command> [args]")
        print("Commands:")
        print("  generate <context> - Generate rules for specific context")
        print("  install - Install dynamic rules system")
        print("  update <context> - Update rules for new context")
        print("  status - Show current rule status")
        return
    
    command = sys.argv[1]
    loader = DynamicRuleLoader()
    
    if command == "generate":
        if len(sys.argv) < 3:
            print("Usage: python manage_rules.py generate <context>")
            return
        
        context_input = sys.argv[2]
        context = loader.analyze_context(context_input)
        rules = loader.generate_cursor_rules(context)
        
        with open(".cursorrules", 'w') as f:
            f.write(rules)
        
        print(f"Generated rules for: {context_input}")
        print(f"Loaded partitions: {loader.get_loaded_partitions()}")
    
    elif command == "install":
        # Install with AIM-OS context
        context = loader.analyze_context("AIM-OS development with full protocols")
        rules = loader.generate_cursor_rules(context)
        
        with open(".cursorrules", 'w') as f:
            f.write(rules)
        
        print("Dynamic rules system installed")
        print(f"Loaded partitions: {loader.get_loaded_partitions()}")
    
    elif command == "update":
        if len(sys.argv) < 3:
            print("Usage: python manage_rules.py update <context>")
            return
        
        context_input = sys.argv[2]
        context = loader.analyze_context(context_input)
        rules = loader.generate_cursor_rules(context)
        
        with open(".cursorrules", 'w') as f:
            f.write(rules)
        
        print(f"Updated rules for: {context_input}")
        print(f"Loaded partitions: {loader.get_loaded_partitions()}")
    
    elif command == "status":
        print("Dynamic Rules System Status:")
        print(f"Available partitions: {len(loader.rule_metadata)}")
        print(f"Currently loaded: {loader.get_loaded_partitions()}")
        print(f"Memory usage: {loader.get_memory_usage()}KB")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
'''
        
        script_path = self.project_root / "manage_dynamic_rules.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make it executable
        os.chmod(script_path, 0o755)
        
        return str(script_path)
    
    def create_cursor_integration(self) -> str:
        """Create Cursor IDE integration files"""
        # Create .cursor directory if it doesn't exist
        cursor_dir = self.project_root / ".cursor"
        cursor_dir.mkdir(exist_ok=True)
        
        # Create dynamic rules configuration
        config = {
            "dynamic_rules": {
                "enabled": True,
                "auto_update": True,
                "context_aware": True,
                "rule_partitions_path": str(self.rules_system_path / "rule_partitions"),
                "config_path": str(self.rules_system_path / "rule_config.json")
            },
            "protocols": {
                "l0_l4": True,
                "ah_protocol": True,
                "mcp_tools": True,
                "lucid": True
            },
            "performance": {
                "max_memory_kb": 500,
                "max_load_time_ms": 200,
                "cache_enabled": True
            }
        }
        
        config_path = cursor_dir / "dynamic_rules_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return str(config_path)

def main():
    """Main function for integration"""
    print("Dynamic Cursor Rules System Integration")
    print("=" * 50)
    
    # Initialize integrator
    integrator = DynamicRulesIntegrator()
    
    # Install dynamic rules
    print("Installing dynamic rules system...")
    if integrator.install_dynamic_rules():
        print("SUCCESS: Dynamic rules installed successfully")
    else:
        print("ERROR: Failed to install dynamic rules")
        return
    
    # Create management script
    print("Creating rule management script...")
    script_path = integrator.create_rule_management_script()
    print(f"SUCCESS: Management script created: {script_path}")
    
    # Create Cursor integration
    print("Creating Cursor IDE integration...")
    config_path = integrator.create_cursor_integration()
    print(f"SUCCESS: Cursor integration created: {config_path}")
    
    print("\nDynamic Cursor Rules System is ready!")
    print("\nUsage:")
    print(f"  python {script_path} status - Show current status")
    print(f"  python {script_path} update 'context description' - Update rules")
    print(f"  python {script_path} generate 'specific task' - Generate rules for task")

if __name__ == "__main__":
    main()
