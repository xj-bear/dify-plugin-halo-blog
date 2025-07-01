# Halo Blog Tools Plugin Packaging Script
# Creates a .difypkg file for Dify plugin distribution

Write-Host "Creating Halo Blog Tools plugin package..."

# Define files and directories to include
$FilesToInclude = @(
    "manifest.yaml",
    "main.py", 
    "requirements.txt",
    "PRIVACY.md",
    "README.md",
    "provider",
    "tools", 
    "halo_plugin",
    "_assets"
)

# Check if files exist
foreach ($file in $FilesToInclude) {
    if (-not (Test-Path $file)) {
        Write-Host "File or directory not found: $file"
        exit 1
    }
}

# Create ZIP file
$OutputPath = "../halo-blog-tools-v0.0.1.zip"
try {
    Compress-Archive -Path $FilesToInclude -DestinationPath $OutputPath -Force
    Write-Host "ZIP file created successfully: $OutputPath"
} catch {
    Write-Host "Failed to create ZIP file: $($_.Exception.Message)"
    exit 1
}

# Rename to .difypkg
$DifypkgPath = "../halo-blog-tools-v0.0.1.difypkg"
try {
    if (Test-Path $DifypkgPath) {
        Remove-Item $DifypkgPath -Force
    }
    Rename-Item $OutputPath $DifypkgPath
    Write-Host "Plugin package created successfully: $DifypkgPath"
} catch {
    Write-Host "Failed to rename file: $($_.Exception.Message)"
    exit 1
}

Write-Host "Packaging completed!"
Write-Host "Output file: $DifypkgPath" 