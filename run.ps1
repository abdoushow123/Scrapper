# Run project tasks: install deps, run cleaning, show summary
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
Write-Host "Using python: $python"

Write-Host "Installing requirements (if needed)..."
& $python -m pip install -r requirements.txt

Write-Host "Running data cleaning..."
& $python src/cleaning.py

Write-Host "Displaying last part of cleaning summary:" 
Get-Content data/cleaned\*cleaning_summary.txt -Tail 200

Write-Host "Run complete."
