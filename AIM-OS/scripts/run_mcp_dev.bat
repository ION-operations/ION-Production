@echo off
REM LUCID-MCP dev launcher: HHNI_LOCAL=1, MCP_MEMORY_DIR, PYTHONPATH
set SCRIPT_DIR=%~dp0
set AIMOS_ROOT=%SCRIPT_DIR%..
set HHNI_LOCAL=1
set MCP_MEMORY_DIR=%AIMOS_ROOT%\mcp_memory
set PYTHONPATH=%AIMOS_ROOT%;%AIMOS_ROOT%\packages
cd /d "%AIMOS_ROOT%"
python lucid_mcp_server.py
