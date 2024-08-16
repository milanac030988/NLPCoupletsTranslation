@echo off
REM Get the directory of the currently running script
set SCRIPT_DIR=%~dp0

set RAW_DATA_DIR=%SCRIPT_DIR%\data\raw
set PROCESS_DATA_DIR=%SCRIPT_DIR%\data\processed
set INTERMEDIATE_DATA_DIR=%SCRIPT_DIR%\data\interim
set REFS_DIR=%SCRIPT_DIR%\references
set MOSSES_DECODER=%SCRIPT_DIR%\references\mossesdecoder
set PYTHON="%RobotPythonPath%"\python