$ErrorActionPreference = "Stop"

$currentPath = Get-Location
Write-Host "Running git add . in $currentPath"
git add .

$date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$commitMessage = "Auto commit $date"

Write-Host "Committing with message: $commitMessage"
git commit -m $commitMessage

Write-Host "Pushing to remote"
git push