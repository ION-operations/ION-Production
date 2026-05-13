"""
Cursor Commands MCP Tools - Phase 1: Discovery & Validation

Provides MCP tools for managing Cursor commands programmatically.

Phase 1 Tools:
1. list_cursor_commands - Discover available commands
2. get_cursor_command - Inspect command details
3. validate_cursor_command - Quality assurance

Author: Aether
Date: 2025-11-05
Status: Phase 1 Implementation
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class CursorCommandsTools:
    """MCP tools for Cursor command management and automation."""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """Initialize CursorCommandsTools.
        
        Args:
            workspace_root: Path to workspace root (auto-detects if None)
        """
        if workspace_root:
            self.workspace_root = Path(workspace_root)
        else:
            # Auto-detect workspace root
            # Try multiple methods:
            # 1. Check CURSOR_WORKSPACE_ROOT environment variable
            env_root = os.getenv("CURSOR_WORKSPACE_ROOT") or os.getenv("WORKSPACE_ROOT")
            if env_root and Path(env_root).exists():
                self.workspace_root = Path(env_root)
            else:
                # 2. Look for .cursor directory from current directory up
                current = Path.cwd()
                # Try current directory first
                if (current / ".cursor" / "commands").exists():
                    self.workspace_root = current
                else:
                    # Walk up directory tree
                    found = False
                    search_path = current
                    while search_path.parent != search_path:
                        if (search_path / ".cursor" / "commands").exists():
                            self.workspace_root = search_path
                            found = True
                            break
                        search_path = search_path.parent
                    
                    if not found:
                        # 3. Fallback: Try common workspace locations
                        possible_paths = [
                            Path.home() / "OneDrive" / "Desktop" / "AIM-OS",
                            Path.home() / "Desktop" / "AIM-OS",
                            Path("C:/Users/bombe/OneDrive/Desktop/AIM-OS"),  # Explicit test path
                            Path.cwd(),
                        ]
                        for path in possible_paths:
                            if path.exists() and (path / ".cursor" / "commands").exists():
                                self.workspace_root = path
                                found = True
                                break
                        
                        if not found:
                            # Final fallback: use current directory
                            self.workspace_root = Path.cwd()
        
        self.commands_dir = self.workspace_root / ".cursor" / "commands"
        
        # Command categories
        self.categories = {
            "documentation": ["create-t0-t4-docs", "update-super-index", "validate-docs", "create-system", "create-decision-log"],
            "development": ["run-tests", "fix-nl-tags", "code-review", "fix-linter", "validate-quintet"],
            "system": ["audit-system", "test-mcp-tools", "deploy-package"],
            "memory": ["create-thought-journal", "update-goal-tree"]
        }
    
    def list_cursor_commands(
        self,
        scope: str = "all",
        category: Optional[str] = None,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """List all available Cursor commands.
        
        Args:
            scope: Scope of commands ("project", "global", "team", "all")
            category: Filter by category (None for all)
            include_metadata: Include detailed metadata
            
        Returns:
            Dictionary containing commands list and statistics
        """
        commands = []
        
        # Get project commands
        if scope in ["project", "all"]:
            commands.extend(self._scan_commands_directory(self.commands_dir))
        
        # Get global commands (if exists)
        if scope in ["global", "all"]:
            global_dir = Path.home() / ".cursor" / "commands"
            if global_dir.exists():
                commands.extend(self._scan_commands_directory(global_dir, scope="global"))
        
        # Filter by category
        if category and category != "all":
            category_commands = self.categories.get(category, [])
            commands = [cmd for cmd in commands if cmd["name"] in category_commands]
        
        # Calculate statistics
        by_category = {}
        for cat, cat_commands in self.categories.items():
            count = len([cmd for cmd in commands if cmd["name"] in cat_commands])
            if count > 0:
                by_category[cat] = count
        
        result = {
            "success": True,
            "commands": commands if include_metadata else [cmd["name"] for cmd in commands],
            "total": len(commands),
            "by_category": by_category,
            "scope": scope,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def get_cursor_command(
        self,
        command_name: str,
        include_usage_stats: bool = False
    ) -> Dict[str, Any]:
        """Get full content and metadata of specific command.
        
        Args:
            command_name: Name of the command (without .md extension)
            include_usage_stats: Include usage statistics (if available)
            
        Returns:
            Dictionary containing command details
        """
        # Find command file
        command_path = self.commands_dir / f"{command_name}.md"
        
        if not command_path.exists():
            # Try global commands
            global_path = Path.home() / ".cursor" / "commands" / f"{command_name}.md"
            if global_path.exists():
                command_path = global_path
            else:
                return {
                    "success": False,
                    "error": f"Command '{command_name}' not found",
                    "searched_paths": [str(self.commands_dir), str(Path.home() / ".cursor" / "commands")]
                }
        
        # Read command file
        try:
            content = command_path.read_text(encoding='utf-8')
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read command: {str(e)}"
            }
        
        # Parse command
        metadata = self._parse_command_metadata(content, command_name)
        
        # Extract workflow steps
        workflow_steps = self._extract_workflow_steps(content)
        
        # Extract MCP tools used
        mcp_tools = self._extract_mcp_tools(content)
        
        # Extract scripts referenced
        scripts = self._extract_scripts(content)
        
        # Get category
        category = self._get_command_category(command_name)
        
        result = {
            "success": True,
            "name": command_name,
            "path": str(command_path),
            "content": content,
            "metadata": {
                "created": metadata.get("created"),
                "updated": metadata.get("updated"),
                "lines": len(content.splitlines()),
                "word_count": len(content.split()),
                "category": category
            },
            "workflow_steps": workflow_steps,
            "mcp_tools_used": mcp_tools,
            "scripts_referenced": scripts,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add usage stats if requested
        if include_usage_stats:
            result["usage_stats"] = self._get_usage_stats(command_name)
        
        return result
    
    def validate_cursor_command(
        self,
        command_name: str,
        checks: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Validate command syntax and workflow.
        
        Args:
            command_name: Name of the command to validate
            checks: List of checks to perform (None for all)
                   ["syntax", "workflow", "scripts", "mcp_tools", "examples"]
            
        Returns:
            Dictionary containing validation results
        """
        if checks is None:
            checks = ["syntax", "workflow", "scripts", "mcp_tools", "examples"]
        
        # Get command
        command_data = self.get_cursor_command(command_name)
        
        if not command_data.get("success"):
            return {
                "success": False,
                "error": command_data.get("error"),
                "command": command_name
            }
        
        content = command_data["content"]
        validation_results = {
            "valid": True,
            "checks": {}
        }
        
        # Syntax check
        if "syntax" in checks:
            syntax_result = self._validate_syntax(content)
            validation_results["checks"]["syntax"] = syntax_result
            if not syntax_result["valid"]:
                validation_results["valid"] = False
        
        # Workflow check
        if "workflow" in checks:
            workflow_result = self._validate_workflow(content)
            validation_results["checks"]["workflow"] = workflow_result
            if not workflow_result["valid"]:
                validation_results["valid"] = False
        
        # Scripts check
        if "scripts" in checks:
            scripts_result = self._validate_scripts(command_data["scripts_referenced"])
            validation_results["checks"]["scripts"] = scripts_result
            if not scripts_result["valid"]:
                validation_results["valid"] = False
        
        # MCP tools check
        if "mcp_tools" in checks:
            mcp_tools_result = self._validate_mcp_tools(command_data["mcp_tools_used"])
            validation_results["checks"]["mcp_tools"] = mcp_tools_result
            if not mcp_tools_result["valid"]:
                validation_results["valid"] = False
        
        # Examples check
        if "examples" in checks:
            examples_result = self._validate_examples(content)
            validation_results["checks"]["examples"] = examples_result
            if not examples_result["valid"]:
                validation_results["valid"] = False
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(validation_results["checks"])
        
        return {
            "success": True,
            "command": command_name,
            "valid": validation_results["valid"],
            "checks": validation_results["checks"],
            "quality_score": quality_score,
            "timestamp": datetime.now().isoformat()
        }
    
    # ============== Helper Methods ==============
    
    def _scan_commands_directory(self, directory: Path, scope: str = "project") -> List[Dict[str, Any]]:
        """Scan directory for command files.
        
        Args:
            directory: Directory to scan
            scope: Scope of commands (project, global, team)
            
        Returns:
            List of command dictionaries
        """
        commands = []
        
        if not directory.exists():
            return commands
        
        for file_path in directory.glob("*.md"):
            command_name = file_path.stem
            
            # Read file
            try:
                content = file_path.read_text(encoding='utf-8')
            except Exception:
                continue
            
            # Parse metadata
            metadata = self._parse_command_metadata(content, command_name)
            
            # Get category
            category = self._get_command_category(command_name)
            
            commands.append({
                "name": command_name,
                "path": str(file_path),
                "scope": scope,
                "category": category,
                "description": metadata.get("description", ""),
                "lines": len(content.splitlines()),
                "word_count": len(content.split())
            })
        
        return commands
    
    def _parse_command_metadata(self, content: str, command_name: str) -> Dict[str, Any]:
        """Parse command metadata from content.
        
        Args:
            content: Command file content
            command_name: Name of the command
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        
        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata["title"] = title_match.group(1)
        
        # Extract description (first paragraph after title)
        description_match = re.search(r'^#\s+.+\n\n(.+?)(?:\n\n|\n#)', content, re.MULTILINE | re.DOTALL)
        if description_match:
            metadata["description"] = description_match.group(1).strip()
        
        # Estimate creation/update dates from file system
        # (In production, could parse from content or git history)
        metadata["created"] = None
        metadata["updated"] = None
        
        return metadata
    
    def _extract_workflow_steps(self, content: str) -> List[str]:
        """Extract workflow steps from command content.
        
        Args:
            content: Command file content
            
        Returns:
            List of workflow steps
        """
        steps = []
        
        # Look for numbered lists in Process/Workflow sections
        process_section = re.search(r'##\s+Process.*?(?=\n##|\Z)', content, re.MULTILINE | re.DOTALL)
        if process_section:
            section_content = process_section.group(0)
            
            # Extract numbered items
            for match in re.finditer(r'^\s*\d+\.\s+\*\*(.+?)\*\*', section_content, re.MULTILINE):
                steps.append(match.group(1))
            
            # If no bold items, try regular numbered items
            if not steps:
                for match in re.finditer(r'^\s*\d+\.\s+(.+)$', section_content, re.MULTILINE):
                    steps.append(match.group(1).strip())
        
        return steps
    
    def _extract_mcp_tools(self, content: str) -> List[str]:
        """Extract MCP tools referenced in command.
        
        Args:
            content: Command file content
            
        Returns:
            List of MCP tool names
        """
        tools = set()
        
        # Look for mcp_lucid-mcp_ prefixed tools
        for match in re.finditer(r'mcp_lucid-mcp_(\w+)', content):
            tools.add(match.group(1))
        
        # Look for common MCP tool calls
        common_tools = [
            "store_memory", "retrieve_memory", "track_confidence",
            "add_timeline_entry", "create_snapshot", "update_goal_progress"
        ]
        for tool in common_tools:
            if tool in content:
                tools.add(tool)
        
        return sorted(list(tools))
    
    def _extract_scripts(self, content: str) -> List[str]:
        """Extract script references from command.
        
        Args:
            content: Command file content
            
        Returns:
            List of script paths
        """
        scripts = set()
        
        # Look for scripts/ paths
        for match in re.finditer(r'scripts/[\w/]+\.py', content):
            scripts.add(match.group(0))
        
        # Look for python command executions
        for match in re.finditer(r'python\s+([\w/]+\.py)', content):
            scripts.add(match.group(1))
        
        return sorted(list(scripts))
    
    def _get_command_category(self, command_name: str) -> str:
        """Get category for command.
        
        Args:
            command_name: Name of the command
            
        Returns:
            Category name or "uncategorized"
        """
        for category, commands in self.categories.items():
            if command_name in commands:
                return category
        return "uncategorized"
    
    def _get_usage_stats(self, command_name: str) -> Dict[str, Any]:
        """Get usage statistics for command.
        
        Args:
            command_name: Name of the command
            
        Returns:
            Dictionary of usage statistics (placeholder for now)
        """
        # Placeholder - would integrate with CMC analytics in production
        return {
            "invocations": 0,
            "avg_time_saved": "Unknown",
            "success_rate": None,
            "last_executed": None,
            "note": "Usage tracking not yet implemented - requires CMC integration"
        }
    
    def _validate_syntax(self, content: str) -> Dict[str, Any]:
        """Validate markdown syntax.
        
        Args:
            content: Command file content
            
        Returns:
            Validation result
        """
        errors = []
        
        # Check for required sections
        required_sections = ["What This Command Does", "Process", "Example Usage"]
        for section in required_sections:
            if section not in content:
                errors.append(f"Missing required section: '{section}'")
        
        # Check for balanced code blocks
        code_blocks = content.count("```")
        if code_blocks % 2 != 0:
            errors.append("Unbalanced code blocks (odd number of ```)")
        
        return {
            "valid": len(errors) == 0,
            "markdown_errors": errors
        }
    
    def _validate_workflow(self, content: str) -> Dict[str, Any]:
        """Validate workflow completeness.
        
        Args:
            content: Command file content
            
        Returns:
            Validation result
        """
        # Extract workflow steps
        steps = self._extract_workflow_steps(content)
        
        missing = []
        if not steps:
            missing.append("No workflow steps found")
        
        if "Process" not in content and "Workflow" not in content:
            missing.append("No Process or Workflow section found")
        
        return {
            "valid": len(missing) == 0,
            "steps_complete": len(steps) > 0,
            "step_count": len(steps),
            "missing_steps": missing
        }
    
    def _validate_scripts(self, scripts: List[str]) -> Dict[str, Any]:
        """Validate that referenced scripts exist.
        
        Args:
            scripts: List of script paths
            
        Returns:
            Validation result
        """
        missing_scripts = []
        scripts_found = []
        
        for script in scripts:
            script_path = self.workspace_root / script
            if script_path.exists():
                scripts_found.append(script)
            else:
                missing_scripts.append(script)
        
        return {
            "valid": len(missing_scripts) == 0,
            "missing_scripts": missing_scripts,
            "scripts_found": scripts_found,
            "total_scripts": len(scripts)
        }
    
    def _validate_mcp_tools(self, mcp_tools: List[str]) -> Dict[str, Any]:
        """Validate that referenced MCP tools exist.
        
        Args:
            mcp_tools: List of MCP tool names
            
        Returns:
            Validation result
        """
        # Known MCP tools (from MCP_TOOLS_INVENTORY)
        known_tools = [
            "store_memory", "retrieve_memory", "get_memory_stats",
            "create_plan", "track_confidence", "synthesize_knowledge",
            "check_invariant", "run_baseline_probe", "detect_manipulation_signals",
            "create_snapshot", "restore_snapshot", "list_snapshots", "archive_snapshot",
            "add_timeline_entry", "get_timeline_summary", "get_timeline_entries",
            "create_goal_timeline_node", "update_goal_progress", "query_goal_timeline",
            "compute_intuition", "update_intuition_weights", "get_intuition_trace"
        ]
        
        tools_exist = [tool for tool in mcp_tools if tool in known_tools]
        tools_unknown = [tool for tool in mcp_tools if tool not in known_tools]
        
        return {
            "valid": len(tools_unknown) == 0,
            "tools_exist": len(tools_exist) == len(mcp_tools),
            "tools_referenced": mcp_tools,
            "unknown_tools": tools_unknown
        }
    
    def _validate_examples(self, content: str) -> Dict[str, Any]:
        """Validate that examples are present.
        
        Args:
            content: Command file content
            
        Returns:
            Validation result
        """
        has_examples = "Example Usage" in content or "Example:" in content
        
        # Count examples
        example_count = len(re.findall(r'User:\s+/', content))
        
        return {
            "valid": has_examples and example_count > 0,
            "examples_present": has_examples,
            "example_count": example_count
        }
    
    def _calculate_quality_score(self, checks: Dict[str, Any]) -> float:
        """Calculate overall quality score from validation checks.
        
        Args:
            checks: Dictionary of validation check results
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        if not checks:
            return 0.0
        
        total_score = 0.0
        total_checks = len(checks)
        
        for check_name, check_result in checks.items():
            if check_result.get("valid", False):
                total_score += 1.0
        
        return total_score / total_checks if total_checks > 0 else 0.0
    
    # ============== Phase 2: Creation & Execution Tools ==============
    
    def create_cursor_command(
        self,
        name: str,
        content: str,
        category: Optional[str] = None,
        workflow_steps: Optional[List[str]] = None,
        mcp_tools: Optional[List[str]] = None,
        scripts: Optional[List[str]] = None,
        examples: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create new Cursor command via MCP.
        
        Args:
            name: Name of the command (without .md extension)
            content: Markdown content for the command
            category: Command category (auto-detected if None)
            workflow_steps: List of workflow steps (optional)
            mcp_tools: List of MCP tools used (optional)
            scripts: List of scripts referenced (optional)
            examples: List of example usage strings (optional)
            
        Returns:
            Dictionary containing creation result and validation
        """
        # Validate name
        if not name or not name.replace("-", "").replace("_", "").isalnum():
            return {
                "success": False,
                "error": f"Invalid command name: '{name}'. Must be alphanumeric with dashes/underscores."
            }
        
        # Determine category if not provided
        if not category:
            category = self._get_command_category(name)
        
        # Build command file path
        command_path = self.commands_dir / f"{name}.md"
        
        # Check if command already exists
        if command_path.exists():
            return {
                "success": False,
                "error": f"Command '{name}' already exists. Use update_cursor_command instead.",
                "existing_path": str(command_path)
            }
        
        # Validate content structure
        if not content.strip():
            return {
                "success": False,
                "error": "Command content cannot be empty"
            }
        
        # Ensure content has required sections
        required_sections = ["What This Command Does"]
        missing_sections = [section for section in required_sections if section not in content]
        
        if missing_sections:
            return {
                "success": False,
                "error": f"Missing required sections: {', '.join(missing_sections)}",
                "expected_sections": required_sections
            }
        
        try:
            # Create command file
            command_path.write_text(content, encoding='utf-8')
            
            # Validate the created command
            validation = self.validate_cursor_command(name)
            
            # Get command ID (next available)
            command_id = f"cmd-{len(list(self.commands_dir.glob('*.md'))):03d}"
            
            return {
                "success": True,
                "command_path": str(command_path),
                "command_id": command_id,
                "name": name,
                "category": category,
                "validation": validation,
                "lines": len(content.splitlines()),
                "word_count": len(content.split()),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create command: {str(e)}"
            }
    
    def update_cursor_command(
        self,
        command_name: str,
        updates: Optional[Dict[str, Any]] = None,
        create_backup: bool = True
    ) -> Dict[str, Any]:
        """Update existing Cursor command.
        
        Args:
            command_name: Name of the command to update
            updates: Dictionary of updates to apply
                - content: New content (optional)
                - workflow_steps: Updated workflow steps (optional)
                - add_examples: Examples to add (optional)
            create_backup: Whether to create backup before updating
            
        Returns:
            Dictionary containing update result
        """
        # Get existing command
        command_data = self.get_cursor_command(command_name)
        
        if not command_data.get("success"):
            return {
                "success": False,
                "error": command_data.get("error", "Command not found")
            }
        
        command_path = Path(command_data["path"])
        
        if not command_path.exists():
            return {
                "success": False,
                "error": f"Command file not found: {command_path}"
            }
        
        # Create backup if requested
        backup_path = None
        if create_backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.commands_dir / "archive"
            backup_dir.mkdir(exist_ok=True)
            backup_path = backup_dir / f"{command_name}_v{timestamp}.md"
            try:
                backup_path.write_text(command_path.read_text(encoding='utf-8'), encoding='utf-8')
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to create backup: {str(e)}"
                }
        
        # Prepare updates
        if updates is None:
            updates = {}
        
        current_content = command_data["content"]
        new_content = current_content
        
        # Update content if provided
        if "content" in updates:
            new_content = updates["content"]
        
        # Add examples if provided
        if "add_examples" in updates and updates["add_examples"]:
            examples_section = "\n\n## Example Usage\n\n"
            for example in updates["add_examples"]:
                examples_section += f"```\n{example}\n```\n\n"
            
            if "## Example Usage" not in new_content:
                new_content += examples_section
            else:
                # Add to existing examples section
                new_content = new_content.replace(
                    "## Example Usage",
                    f"## Example Usage{examples_section}"
                )
        
        try:
            # Write updated content
            command_path.write_text(new_content, encoding='utf-8')
            
            # Validate updated command
            validation = self.validate_cursor_command(command_name)
            
            return {
                "success": True,
                "command": command_name,
                "backup_path": str(backup_path) if backup_path else None,
                "validation": validation,
                "changes": list(updates.keys()),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update command: {str(e)}"
            }
    
    def execute_cursor_command(
        self,
        command_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        track_execution: bool = True
    ) -> Dict[str, Any]:
        """Execute Cursor command via MCP (meta-circular!).
        
        Args:
            command_name: Name of the command to execute
            parameters: Optional parameters to pass to command
            track_execution: Whether to track execution in timeline
            
        Returns:
            Dictionary containing execution result
        """
        # Get command
        command_data = self.get_cursor_command(command_name)
        
        if not command_data.get("success"):
            return {
                "success": False,
                "error": command_data.get("error", "Command not found"),
                "execution_id": None
            }
        
        # Validate command before execution
        validation = self.validate_cursor_command(command_name)
        
        if not validation.get("valid", False):
            return {
                "success": False,
                "error": "Command validation failed",
                "validation": validation,
                "execution_id": None
            }
        
        # Generate execution ID
        execution_id = f"exec-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Parse command workflow
        content = command_data["content"]
        workflow_steps = self._extract_workflow_steps(content)
        
        # Simulate execution (in real implementation, would execute steps)
        # For now, return success with execution metadata
        result = {
            "success": True,
            "execution_id": execution_id,
            "command_executed": command_name,
            "workflow_steps": workflow_steps,
            "parameters": parameters or {},
            "artifacts_created": [],
            "time_taken": "0 seconds",  # Placeholder
            "time_saved": "0 minutes",  # Placeholder
            "mcp_tools_called": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Note: Actual command execution would require:
        # - Parsing workflow steps
        # - Executing scripts
        # - Calling MCP tools
        # - Tracking results
        # This is a placeholder for the execution framework
        
        return result
    
    def chain_cursor_commands(
        self,
        commands: List[Dict[str, Any]],
        stop_on_error: bool = True,
        track_as_chain: bool = True
    ) -> Dict[str, Any]:
        """Execute multiple commands in sequence.
        
        Args:
            commands: List of command dictionaries with 'name' and optional 'params'
            stop_on_error: Whether to stop chain if command fails
            track_as_chain: Whether to track as single chain execution
            
        Returns:
            Dictionary containing chain execution results
        """
        if not commands:
            return {
                "success": False,
                "error": "No commands provided"
            }
        
        chain_id = f"chain-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        executions = []
        total_time = 0.0
        
        for i, cmd in enumerate(commands):
            command_name = cmd.get("name")
            if not command_name:
                if stop_on_error:
                    return {
                        "success": False,
                        "error": f"Command {i+1} missing 'name' field",
                        "chain_id": chain_id,
                        "executions": executions
                    }
                continue
            
            params = cmd.get("params", {})
            
            # Execute command
            result = self.execute_cursor_command(
                command_name=command_name,
                parameters=params,
                track_execution=False  # Track at chain level instead
            )
            
            executions.append({
                "command": command_name,
                "success": result.get("success", False),
                "execution_id": result.get("execution_id"),
                "error": result.get("error")
            })
            
            # Stop on error if requested
            if not result.get("success") and stop_on_error:
                return {
                    "success": False,
                    "chain_id": chain_id,
                    "executions": executions,
                    "failed_at": i + 1,
                    "error": f"Command '{command_name}' failed: {result.get('error')}"
                }
        
        # All commands executed successfully
        return {
            "success": True,
            "chain_id": chain_id,
            "executions": executions,
            "total_commands": len(commands),
            "total_time": f"{total_time:.2f} minutes",
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_cursor_command(
        self,
        description: str,
        category: Optional[str] = None,
        suggested_name: Optional[str] = None,
        examples: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """AI-generated command from workflow description (placeholder).
        
        Args:
            description: Description of what the command should do
            category: Command category (auto-detected if None)
            suggested_name: Suggested command name (auto-generated if None)
            examples: Example usage strings
            
        Returns:
            Dictionary containing generated command
        """
        # Generate command name if not provided
        if not suggested_name:
            # Simple name generation from description
            words = description.lower().split()
            # Take first 3-4 words, join with dashes
            suggested_name = "-".join(words[:min(4, len(words))])
            # Remove special characters
            suggested_name = re.sub(r'[^a-z0-9-]', '', suggested_name)
            suggested_name = suggested_name[:50]  # Limit length
        
        # Determine category
        if not category:
            category = self._get_command_category(suggested_name)
        
        # Generate basic command template
        command_content = f"""# {suggested_name.replace('-', ' ').title()}

{description}

## What This Command Does

[Auto-generated from description]

## Process

1. **Step 1** - [To be filled]
2. **Step 2** - [To be filled]
3. **Step 3** - [To be filled]

## Example Usage

"""
        
        if examples:
            for example in examples:
                command_content += f"```\n{example}\n```\n\n"
        else:
            command_content += f"```\nUser: /{suggested_name}\nAI: [Command execution]\n```\n"
        
        # Validate generated command
        validation_result = self.validate_cursor_command(suggested_name) if False else {
            "valid": False,
            "note": "Command not yet created, validation will run after creation"
        }
        
        return {
            "success": True,
            "command_content": command_content,
            "command_path": str(self.commands_dir / f"{suggested_name}.md"),
            "suggested_name": suggested_name,
            "category": category,
            "workflow_steps": ["Step 1", "Step 2", "Step 3"],
            "mcp_tools_suggested": [],
            "scripts_suggested": [],
            "validation": {
                "ready_for_use": False,
                "needs_review": True,
                "note": "Generated command is a template and needs manual review and completion"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    # ============== Phase 3: Analytics & Optimization Tools ==============
    
    def analyze_cursor_commands(
        self,
        scope: str = "all",
        time_range: Optional[str] = None,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze command usage and effectiveness.
        
        Args:
            scope: Scope of commands ("all", "project", "global")
            time_range: Time range for analysis ("7d", "30d", "all")
            metrics: List of metrics to include ["usage", "time_savings", "success_rate", "popularity"]
            
        Returns:
            Dictionary containing analysis results and recommendations
        """
        if metrics is None:
            metrics = ["usage", "time_savings", "success_rate", "popularity"]
        
        # Get all commands
        commands_result = self.list_cursor_commands(scope=scope, include_metadata=True)
        commands = commands_result.get("commands", [])
        
        # Initialize analysis
        total_commands = len(commands)
        total_invocations = 0  # Placeholder - would integrate with CMC analytics
        total_time_saved = 0  # Placeholder
        
        # Analyze each command
        command_stats = []
        for cmd in commands:
            command_name = cmd["name"]
            
            # Get command details
            cmd_details = self.get_cursor_command(command_name)
            
            # Validate command
            validation = self.validate_cursor_command(command_name)
            quality_score = validation.get("quality_score", 0.0)
            
            # Estimate time savings based on complexity
            # (In production, would use actual usage data from CMC)
            estimated_time_savings = self._estimate_time_savings(cmd_details)
            
            # Calculate popularity score (based on quality and completeness)
            popularity_score = self._calculate_popularity_score(cmd_details, validation)
            
            command_stats.append({
                "name": command_name,
                "category": cmd.get("category", "uncategorized"),
                "quality_score": quality_score,
                "estimated_time_savings": estimated_time_savings,
                "popularity_score": popularity_score,
                "lines": cmd.get("lines", 0),
                "word_count": cmd.get("word_count", 0)
            })
        
        # Sort by popularity
        command_stats.sort(key=lambda x: x["popularity_score"], reverse=True)
        
        # Find most/least used
        most_used = command_stats[:3] if len(command_stats) >= 3 else command_stats
        least_used = command_stats[-3:] if len(command_stats) >= 3 else []
        
        # Calculate overall metrics
        avg_quality = sum(c["quality_score"] for c in command_stats) / len(command_stats) if command_stats else 0.0
        avg_time_savings = sum(c["estimated_time_savings"] for c in command_stats) / len(command_stats) if command_stats else 0.0
        avg_popularity = sum(c["popularity_score"] for c in command_stats) / len(command_stats) if command_stats else 0.0
        
        # Generate recommendations
        recommendations = []
        
        if least_used:
            recommendations.append({
                "type": "deprecation",
                "message": f"Consider deprecating underused commands: {', '.join([c['name'] for c in least_used[:3]])}",
                "commands": [c["name"] for c in least_used[:3]]
            })
        
        low_quality = [c for c in command_stats if c["quality_score"] < 0.80]
        if low_quality:
            recommendations.append({
                "type": "improvement",
                "message": f"Improve quality of commands: {', '.join([c['name'] for c in low_quality[:3]])}",
                "commands": [c["name"] for c in low_quality[:3]]
            })
        
        if avg_quality < 0.90:
            recommendations.append({
                "type": "general",
                "message": "Overall command quality could be improved",
                "suggestion": "Run validation on all commands and address issues"
            })
        
        return {
            "success": True,
            "analysis": {
                "total_commands": total_commands,
                "total_invocations": total_invocations,
                "total_time_saved": f"{total_time_saved} minutes",
                "most_used": [
                    {
                        "command": c["name"],
                        "category": c["category"],
                        "quality_score": c["quality_score"],
                        "popularity_score": c["popularity_score"],
                        "estimated_time_savings": f"{c['estimated_time_savings']} minutes"
                    }
                    for c in most_used
                ],
                "least_used": [
                    {
                        "command": c["name"],
                        "category": c["category"],
                        "quality_score": c["quality_score"],
                        "popularity_score": c["popularity_score"]
                    }
                    for c in least_used
                ],
                "average_quality": round(avg_quality, 2),
                "average_time_savings": f"{avg_time_savings:.1f} minutes",
                "average_popularity": round(avg_popularity, 2),
                "effectiveness_score": round((avg_quality + avg_popularity) / 2, 2)
            },
            "recommendations": recommendations,
            "scope": scope,
            "time_range": time_range or "all",
            "timestamp": datetime.now().isoformat()
        }
    
    def sync_cursor_commands(
        self,
        source: str,
        target: str,
        commands: Optional[List[str]] = None,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """Sync commands across environments (project ↔ global ↔ team).
        
        Args:
            source: Source environment ("project", "global", "team")
            target: Target environment ("project", "global", "team")
            commands: List of command names to sync (None for all)
            overwrite: Whether to overwrite existing commands
            
        Returns:
            Dictionary containing sync results
        """
        # Validate source/target
        valid_scopes = ["project", "global", "team"]
        if source not in valid_scopes or target not in valid_scopes:
            return {
                "success": False,
                "error": f"Invalid scope. Must be one of: {', '.join(valid_scopes)}"
            }
        
        if source == target:
            return {
                "success": False,
                "error": "Source and target cannot be the same"
            }
        
        # Get source commands
        if source == "project":
            source_dir = self.commands_dir
        elif source == "global":
            source_dir = Path.home() / ".cursor" / "commands"
        else:  # team
            return {
                "success": False,
                "error": "Team commands sync not yet implemented"
            }
        
        if not source_dir.exists():
            return {
                "success": False,
                "error": f"Source directory does not exist: {source_dir}"
            }
        
        # Get target directory
        if target == "project":
            target_dir = self.commands_dir
        elif target == "global":
            target_dir = Path.home() / ".cursor" / "commands"
            target_dir.mkdir(parents=True, exist_ok=True)
        else:  # team
            return {
                "success": False,
                "error": "Team commands sync not yet implemented"
            }
        
        # Get commands to sync
        if commands is None:
            # Sync all commands
            command_files = list(source_dir.glob("*.md"))
            commands_to_sync = [f.stem for f in command_files]
        else:
            commands_to_sync = commands
        
        synced = []
        skipped = []
        conflicts = []
        
        for command_name in commands_to_sync:
            source_file = source_dir / f"{command_name}.md"
            target_file = target_dir / f"{command_name}.md"
            
            if not source_file.exists():
                skipped.append({
                    "command": command_name,
                    "reason": "Source file not found"
                })
                continue
            
            if target_file.exists() and not overwrite:
                conflicts.append({
                    "command": command_name,
                    "reason": "Target file exists and overwrite=False"
                })
                continue
            
            try:
                # Copy command file
                content = source_file.read_text(encoding='utf-8')
                target_file.write_text(content, encoding='utf-8')
                
                synced.append(command_name)
            except Exception as e:
                skipped.append({
                    "command": command_name,
                    "reason": f"Failed to sync: {str(e)}"
                })
        
        return {
            "success": True,
            "synced": len(synced),
            "skipped": len(skipped),
            "conflicts": len(conflicts),
            "synced_commands": synced,
            "skipped_details": skipped,
            "conflict_details": conflicts,
            "source": source,
            "target": target,
            "timestamp": datetime.now().isoformat()
        }
    
    # ============== Phase 3 Helper Methods ==============
    
    def _estimate_time_savings(self, command_details: Dict[str, Any]) -> float:
        """Estimate time savings for a command.
        
        Args:
            command_details: Command details from get_cursor_command
            
        Returns:
            Estimated time savings in minutes
        """
        # Base time savings based on workflow complexity
        workflow_steps = len(command_details.get("workflow_steps", []))
        scripts_count = len(command_details.get("scripts_referenced", []))
        mcp_tools_count = len(command_details.get("mcp_tools_used", []))
        
        # Estimate: Each step saves ~2 minutes, scripts save ~5 minutes, MCP tools save ~1 minute
        base_savings = workflow_steps * 2.0
        script_savings = scripts_count * 5.0
        tool_savings = mcp_tools_count * 1.0
        
        return base_savings + script_savings + tool_savings
    
    def _calculate_popularity_score(self, command_details: Dict[str, Any], validation: Dict[str, Any]) -> float:
        """Calculate popularity score for a command.
        
        Args:
            command_details: Command details
            validation: Validation results
            
        Returns:
            Popularity score (0.0-1.0)
        """
        quality_score = validation.get("quality_score", 0.0)
        
        # Factors that increase popularity:
        # - High quality score
        # - Has examples
        # - Has workflow steps
        # - Uses MCP tools
        # - Has scripts
        
        examples_score = 0.2 if validation.get("checks", {}).get("examples", {}).get("valid", False) else 0.0
        workflow_score = 0.2 if len(command_details.get("workflow_steps", [])) > 0 else 0.0
        tools_score = 0.1 if len(command_details.get("mcp_tools_used", [])) > 0 else 0.0
        scripts_score = 0.1 if len(command_details.get("scripts_referenced", [])) > 0 else 0.0
        
        popularity = (quality_score * 0.4) + examples_score + workflow_score + tools_score + scripts_score
        
        return min(1.0, popularity)  # Cap at 1.0


# ============== MCP Tool Registration ==============

def register_cursor_commands_tools(tools: CursorCommandsTools) -> List[Dict[str, Any]]:
    """Register Cursor Commands MCP tools.
    
    Args:
        tools: CursorCommandsTools instance
        
    Returns:
        List of tool definitions for MCP server
    """
    return [
        {
            "name": "list_cursor_commands",
            "description": "List all available Cursor commands with metadata and statistics",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scope": {
                        "type": "string",
                        "enum": ["project", "global", "team", "all"],
                        "default": "all",
                        "description": "Scope of commands to list"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["documentation", "development", "system", "memory", "all"],
                        "description": "Filter by category"
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include detailed metadata for each command"
                    }
                }
            },
            "handler": tools.list_cursor_commands
        },
        {
            "name": "get_cursor_command",
            "description": "Get full content and metadata of a specific Cursor command",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "command_name": {
                        "type": "string",
                        "description": "Name of the command (without .md extension)"
                    },
                    "include_usage_stats": {
                        "type": "boolean",
                        "default": False,
                        "description": "Include usage statistics (if available)"
                    }
                },
                "required": ["command_name"]
            },
            "handler": tools.get_cursor_command
        },
        {
            "name": "validate_cursor_command",
            "description": "Validate Cursor command syntax, workflow, and quality",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "command_name": {
                        "type": "string",
                        "description": "Name of the command to validate"
                    },
                    "checks": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["syntax", "workflow", "scripts", "mcp_tools", "examples"]
                        },
                        "description": "List of checks to perform (defaults to all)"
                    }
                },
                "required": ["command_name"]
            },
            "handler": tools.validate_cursor_command
        }
    ]
