param(
    [ValidateSet("on","off")][string]$Mode = "on",
    [string[]]$Specs = @(
        "probes.promptinject",
        "probes.latentinjection",
        "probes.goodside",
        "probes.encoding"
    ),
    [string]$Model = "Qwen3.6-35B-A3B-NVFP4"
)

$env:OPENAICOMPATIBLE_API_KEY = "dummy"
Start-Transcript -Path "run_log_think$Mode.txt" -Append

foreach ($s in $Specs) {
    $name = $s -replace '^probes\.', ''
    $prefix = "run_think${Mode}_$name"
    Write-Host "=== $s started $(Get-Date) ==="

    $garakArgs = @(
        "--target_type", "openai.OpenAICompatible",
        "--target_name", $Model,
        "--generator_option_file", "ft.json",
        "--spec", $s,
        "--generations", "1",
        "--seed", "42",
        "--report_prefix", $prefix
    )
    & garak @garakArgs

    if ($LASTEXITCODE -ne 0) { Write-Host "FAILED: $s (exit code $LASTEXITCODE)" }
    Write-Host "=== $s finished $(Get-Date) ==="
}

Stop-Transcript