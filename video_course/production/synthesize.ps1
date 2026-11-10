param(
    [string]$TextPath,
    [string]$OutputPath,
    [string]$VoiceName = 'Microsoft Jakub',
    [switch]$Ssml,
    [string]$JobsPath,
    [double]$SpeakingRate = 0.98
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media.SpeechSynthesis, ContentType=WindowsRuntime]
$null = [Windows.Media.SpeechSynthesis.SpeechSynthesisStream, Windows.Media.SpeechSynthesis, ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.DataReader, Windows.Storage.Streams, ContentType=WindowsRuntime]
$academyAsTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
} | Select-Object -First 1
function Wait-AcademyOperation($Operation, [Type]$ResultType) {
    $academyTask = $academyAsTask.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    $academyTask.Wait()
    return $academyTask.Result
}
$academySynth = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer
try {
    $academyVoice = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | Where-Object {
        $_.DisplayName -eq $VoiceName -and $_.Language -eq 'cs-CZ'
    } | Select-Object -First 1
    if ($null -eq $academyVoice) { throw "Cesky hlas '$VoiceName' neni dostupny pres WinRT." }
    $academySynth.Voice = $academyVoice
    $academySynth.Options.SpeakingRate = $SpeakingRate
    if ($JobsPath) {
        $academyJobs = [IO.File]::ReadAllText((Resolve-Path -LiteralPath $JobsPath), [Text.Encoding]::UTF8) | ConvertFrom-Json
    } else {
        if (-not $TextPath -or -not $OutputPath) { throw 'Specify TextPath and OutputPath, or JobsPath.' }
        $academyJobs = @([pscustomobject]@{text_path=$TextPath; output_path=$OutputPath; ssml=$Ssml.IsPresent})
    }
    foreach ($academyJob in $academyJobs) {
    if (Test-Path -LiteralPath $academyJob.output_path) { continue }
    $academyText = [IO.File]::ReadAllText((Resolve-Path -LiteralPath $academyJob.text_path), [Text.Encoding]::UTF8)
    if ($academyJob.ssml) {
        $academyOperation = $academySynth.SynthesizeSsmlToStreamAsync($academyText)
    } else {
        $academyOperation = $academySynth.SynthesizeTextToStreamAsync($academyText)
    }
    $academyAudio = Wait-AcademyOperation $academyOperation ([Windows.Media.SpeechSynthesis.SpeechSynthesisStream])
    try {
        $academyReader = New-Object Windows.Storage.Streams.DataReader($academyAudio)
        $null = Wait-AcademyOperation ($academyReader.LoadAsync([uint32]$academyAudio.Size)) ([uint32])
        $academyBytes = New-Object byte[] ([int]$academyAudio.Size)
        $academyReader.ReadBytes($academyBytes)
        $academyAbsoluteOutput = [IO.Path]::GetFullPath($academyJob.output_path)
        $null = [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($academyAbsoluteOutput))
        [IO.File]::WriteAllBytes($academyAbsoluteOutput, $academyBytes)
        Write-Output "Microsoft Jakub cs-CZ -> $academyAbsoluteOutput ($($academyBytes.Length) bytes)"
    } finally { if ($academyReader) { $academyReader.Dispose() }; $academyAudio.Dispose() }
    }
} finally { $academySynth.Dispose() }
