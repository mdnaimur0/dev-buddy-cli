param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

$PythonScript = "main.py"

# Run the Python script with all arguments
$result = & python -u $PythonScript @Arguments
$resultArr = @($result)
$lastLine = $resultArr[$resultArr.Length - 1]

# Check if the result is GOTO:<path>
if ($lastLine.StartsWith("GOTO:")) {
    # Fix: Properly extract the path part
    $pathStr = $lastLine.Substring(5).Trim()

    # Optionally change drive if needed
    $ExecutionContext.SessionState.Path.SetLocation([System.IO.Path]::GetPathRoot($pathStr))

    # Now change to the full path
    Set-Location -Path $pathStr
    Write-Output "Changed directory to: $pathStr"
} else {
    Write-Output $result
}
