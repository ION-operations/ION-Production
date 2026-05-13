# Create all floating files organization directories
$basePath = "knowledge_architecture/FLOATING_FILES_ORGANIZED"

# Create main directories
$directories = @(
    "$basePath/SESSION_HISTORY/BREAKTHROUGHS",
    "$basePath/SESSION_HISTORY/CONSOLIDATION_SESSIONS", 
    "$basePath/SESSION_HISTORY/MCP_DEVELOPMENT",
    "$basePath/SYSTEM_INTEGRATION/ICIP_INTEGRATION",
    "$basePath/SYSTEM_INTEGRATION/LUCID_ORCHESTRATOR",
    "$basePath/SYSTEM_INTEGRATION/SNAPSHOT_SYSTEMS",
    "$basePath/DEVELOPMENT_TOOLS/PYTHON_SCRIPTS",
    "$basePath/DEVELOPMENT_TOOLS/GIT_MANAGEMENT",
    "$basePath/DEVELOPMENT_TOOLS/CONFIGURATION_FILES",
    "$basePath/EXTERNAL_DOCUMENTATION/README_VERSIONS",
    "$basePath/EXTERNAL_DOCUMENTATION/USER_GUIDES",
    "$basePath/EXTERNAL_DOCUMENTATION/PROJECT_ANALYSIS"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force
    Write-Host "Created: $dir"
}
