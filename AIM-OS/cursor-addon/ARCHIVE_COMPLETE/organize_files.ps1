# AUTOMATED FILE ORGANIZATION SCRIPT
# PowerShell script to categorize all markdown files

$basePath = "C:\Users\bombe\OneDrive\Desktop\AIM-OS\cursor-addon"
$archivePath = "$basePath\ARCHIVE_COMPLETE"

# Get all markdown files except archive
$files = Get-ChildItem -Path $basePath -Filter *.md -Recurse | Where-Object {
    $_.FullName -notlike "*\node_modules\*" -and
    $_.FullName -notlike "*\out\*" -and
    $_.FullName -notlike "*\dist\*" -and
    $_.FullName -notlike "*\ARCHIVE_COMPLETE\*"
}

foreach ($file in $files) {
    $category = ""
    $name = $file.Name.ToUpper()
    
    # Categorize based on filename patterns
    if ($name -like "*ERROR*" -or $name -like "*LOG*" -or $name -like "*FAILURE*" -or $name -like "*CRITICAL_SESSION*") {
        $category = "errors_logs"
    }
    elseif ($name -like "*DIAGNOSTIC*" -or $name -like "*ANALYSIS*" -or $name -like "*FINDING*" -or $name -like "*CHECKLIST*" -or $name -like "*SYSTEMATIC*") {
        $category = "diagnostic_reports"
    }
    elseif ($name -like "*ARCHITECTURE*" -or $name -like "*SYSTEM*" -or $name -like "*MAP*" -or $name -like "*BLUEPRINT*" -or $name -like "*OVERVIEW*" -or $name -like "*COMPLETE_*MAP*") {
        $category = "architecture_docs"
    }
    elseif ($name -like "*FIX*" -and ($name -like "*APPLIED*" -or $name -like "*COMPLETE*" -or $name -like "*SUCCESS*" -or $name -like "*THREE*" -or $name -like "*BOTH*")) {
        $category = "fix_attempts"
    }
    elseif ($name -like "*MCP*" -or $name -like "*COLLABORATION*" -or $name -like "*AI_*" -or $name -like "*SEV*" -or $name -like "*MAX*" -or $name -like "*CONSOLIDATED*") {
        $category = "mcp_collaboration"
    }
    elseif ($name -like "*RESEARCH*" -or $name -like "*INVESTIGATION*" -or $name -like "*BLANK_DASHBOARD*" -or $name -like "*CURSOR_WEBVIEW*") {
        $category = "research_findings"
    }
    elseif ($name -like "*IDEAS*" -or $name -like "*FEEDBACK*" -or $name -like "*FRUSTRATION*" -or $name -like "*TRUST*") {
        $category = "user_feedback"
    }
    elseif ($name -like "*FIX*" -or $name -like "*ATTEMPT*" -or $name -like "*FAILED*") {
        $category = "failed_attempts"
    }
    else {
        $category = "failed_attempts"  # Default category
    }
    
    # Copy file to appropriate category
    $destPath = "$archivePath\$category\$($file.Name)"
    if (-not (Test-Path $destPath)) {
        Copy-Item $file.FullName $destPath -Force
        Write-Host "Copied: $($file.Name) -> $category"
    }
}

Write-Host "`nOrganization complete!"



