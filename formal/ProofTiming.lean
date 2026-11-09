import Lean
import Checker
open Lean Meta Elab Tactic
/-- Same kernel proof construction used by `decide +kernel`, with phase timers.
The kernel checks the auxiliary lemma; the tactic returns only its constant. -/
elab "timed_kernel_decide" : tactic => do
  let goal ← getMainGoal
  let target ← instantiateMVars (← goal.getType)
  IO.FS.writeFile "local/stage3-proof-progress.txt" s!"constructing {target}"
  let start ← IO.monoMsNow
  let proof ← mkDecideProof target
  let proof ← instantiateMVars proof
  let built ← IO.monoMsNow
  let name ← withOptions (Elab.async.set · false) do
    mkAuxLemma [] target proof
  let checked ← IO.monoMsNow
  IO.FS.writeFile "local/stage3-proof-progress.txt" s!"checked {target}"
  logInfo m!"proof_construction_ms={built-start}; kernel_check_and_insert_ms={checked-built}"
  goal.assign (mkConst name)
  replaceMainGoal []
