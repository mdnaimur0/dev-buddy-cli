@echo off
setlocal EnableDelayedExpansion

REM ============================================================================
REM  buddy.bat - Dev Buddy CLI wrapper for Windows CMD
REM
REM  Runs main.py with all arguments. If the last line of stdout starts with
REM  "GOTO:", changes the shell's working directory to the specified path.
REM  Otherwise, prints all captured stdout as-is.
REM
REM  Usage:  buddy <command> [args...]
REM
REM  Note:   stderr is NOT redirected — interactive prompts and menus printed
REM          by Python to stderr appear on screen in real time. Only stdout
REM          is captured and inspected for the GOTO directive.
REM ============================================================================

set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%main.py"

REM --- Capture only stdout; let stderr flow to the console -------------------
set "TMPFILE=%SCRIPT_DIR%buddy_output_%RANDOM%_%RANDOM%.tmp"
python -u "%PYTHON_SCRIPT%" %* > "%TMPFILE%"

REM --- Read the last line of stdout ------------------------------------------
set "LAST_LINE="
set "LINE_COUNT=0"
for /f "usebackq delims=" %%L in ("%TMPFILE%") do (
    set /a LINE_COUNT+=1
    set "LAST_LINE=%%L"
)

REM --- Check if the last line starts with "GOTO:" ----------------------------
set "PREFIX=!LAST_LINE:~0,5!"
if "!PREFIX!"=="GOTO:" (
    REM Extract the path: skip "GOTO:" (5 chars) and trim leading spaces
    set "RAW_PATH=!LAST_LINE:~5!"
    for /f "tokens=* delims= " %%P in ("!RAW_PATH!") do set "TARGET_PATH=%%P"

    REM Clean up temp file while we still have access to local variables
    del "%TMPFILE%" 2>nul

    REM Propagate the directory change out of the setlocal block.
    REM The FOR variable %%D survives endlocal because FOR expansion happens
    REM at iteration time, not at parse time.
    for /f "delims=" %%D in ("!TARGET_PATH!") do (
        endlocal
        cd /d "%%D"
        echo Changed directory to: %%D
    )
    goto :eof
)

REM --- No GOTO: print all captured stdout as-is ------------------------------
type "%TMPFILE%"
del "%TMPFILE%" 2>nul

endlocal
goto :eof
