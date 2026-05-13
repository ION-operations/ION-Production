# MiKTeX Installation Guide

## Quick Install (Windows)

### Option 1: Download and Install Manually

1. **Download MiKTeX:**
   - Go to: https://miktex.org/download
   - Download "Basic MiKTeX Installer" (Windows x64)
   - Or direct link: https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/basic-miktex-24.1-x64.exe

2. **Run Installer:**
   - Double-click the downloaded installer
   - Choose "Install for all users" (requires admin) or "Install for current user"
   - Follow the installation wizard
   - **Important:** Check "Install missing packages automatically" when prompted

3. **Verify Installation:**
   ```powershell
   pdflatex --version
   ```

### Option 2: Using Chocolatey (if installed)

```powershell
choco install miktex -y
```

### Option 3: Using Winget (Windows 10/11)

```powershell
winget install MiKTeX.MiKTeX
```

## After Installation

1. **Refresh PATH:**
   - Close and reopen terminal/PowerShell
   - Or run: `refreshenv` (if Chocolatey installed)

2. **Test Installation:**
   ```powershell
   pdflatex --version
   ```

3. **Build PDF:**
   ```powershell
   cd north_star_project\latex
   pdflatex main.tex
   pdflatex main.tex  # Run 2-3 times for cross-references
   pdflatex main.tex
   ```

## Troubleshooting

**If pdflatex not found:**
- Add MiKTeX bin directory to PATH manually:
  - `C:\Program Files\MiKTeX\miktex\bin\x64` (system install)
  - `%USERPROFILE%\AppData\Local\Programs\MiKTeX\miktex\bin\x64` (user install)

**Missing packages:**
- MiKTeX will prompt to install missing packages automatically
- Or use: `miktex packages install <package-name>`

**Build errors:**
- Check `main.log` for detailed error messages
- Ensure all chapter.tex files exist
- Run `pdflatex` multiple times to resolve cross-references

