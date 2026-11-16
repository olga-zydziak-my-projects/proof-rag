import ContextualSourceBinding
set_option autoImplicit false
namespace RepoProof.Stage9
open RepoProof SourceBinding Contextual

theorem inverse_injective {n : Nat} (names : Fin n → Identity)
    (inverse : Identity → Option (Fin n))
    (h : allVertices (fun v => inverse (names v) == some v) = true) :
    Function.Injective names := by
  intro a b same
  have ha : inverse (names a) = some a := by simpa using allVertices_at _ h a
  have hb : inverse (names b) = some b := by simpa using allVertices_at _ h b
  rw [same, hb] at ha
  exact (Option.some.inj ha).symm

end RepoProof.Stage9
#print axioms RepoProof.Stage9.inverse_injective
