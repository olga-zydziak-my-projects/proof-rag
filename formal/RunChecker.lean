import Chromium
open RepoProof Chromium
def main : IO Unit := do
  let start ← IO.monoMsNow
  IO.println (check graph root certificate)
  let stop ← IO.monoMsNow
  IO.println s!"checker_and_output_ms={stop-start}"
