import ChromiumFast
open RepoProof ChromiumFast
def main : IO Unit := do
  let start ← IO.monoMsNow
  IO.println (fastCheck graph root certificate)
  let stop ← IO.monoMsNow
  IO.println s!"checker_and_output_ms={stop-start}"
