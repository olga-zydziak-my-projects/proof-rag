import Std

/-!
# Exact reachability from a certificate

The graph and the candidate predicate are inputs to this theorem. The theorem
does not establish that a graph was extracted faithfully from source code.
No finiteness assumption is needed for the logical result below.
-/

set_option autoImplicit false

universe u

namespace RepoProof

/-- A finite directed path, including the path of length zero at `root`. -/
inductive Reach {V : Type u} (Edge : V → V → Prop) (root : V) : V → Prop where
  | refl : Reach Edge root root
  | step {a b : V} : Reach Edge root a → Edge a b → Reach Edge root b

/-- Obligations checked for a candidate set of reachable vertices.

`sound` must be justified by paths or another checked proof: it is not inferred
from a search engine's claim. `closed` quantifies over every supplied graph edge.
-/
structure Certificate {V : Type u} (Edge : V → V → Prop)
    (root : V) (R : V → Prop) : Prop where
  root_mem : R root
  sound : ∀ v : V, R v → Reach Edge root v
  closed : ∀ {a b : V}, R a → Edge a b → R b

/-- Root inclusion and edge closure imply that no reachable vertex is omitted. -/
theorem complete {V : Type u} {Edge : V → V → Prop}
    {root : V} {R : V → Prop} (certificate : Certificate Edge root R)
    {v : V} (reachable : Reach Edge root v) : R v := by
  induction reachable with
  | refl => exact certificate.root_mem
  | step previous edge ih => exact certificate.closed ih edge

/-- A certified candidate contains exactly the vertices reachable from the root. -/
theorem exact_reachability {V : Type u} {Edge : V → V → Prop}
    {root : V} {R : V → Prop} (certificate : Certificate Edge root R)
    (v : V) : R v ↔ Reach Edge root v := by
  constructor
  · intro member
    exact certificate.sound v member
  · intro reachable
    exact complete certificate reachable

/-- A parent edge with strictly decreasing natural rank yields a real path.

The explicit disjunction and existential witnesses avoid any need to choose
parents globally. Strict rank decrease rules out cyclic parent justifications.
-/
theorem soundness_from_ranked_witnesses {V : Type u}
    {Edge : V → V → Prop} {root : V} {R : V → Prop}
    (rank : V → Nat)
    (witnesses : ∀ v : V, R v →
      v = root ∨ ∃ p : V, R p ∧ Edge p v ∧ rank p < rank v) :
    ∀ v : V, R v → Reach Edge root v := by
  have by_rank : ∀ n : Nat, ∀ v : V,
      rank v = n → R v → Reach Edge root v := by
    intro n
    refine Nat.strongRecOn n ?_
    intro k ih v rank_eq member
    rcases witnesses v member with at_root | ⟨p, parent_member, edge, smaller⟩
    · subst v
      exact Reach.refl
    · have smaller_k : rank p < k := by
        simpa only [rank_eq] using smaller
      have parent_reachable : Reach Edge root p :=
        ih (rank p) smaller_k p rfl parent_member
      exact Reach.step parent_reachable edge
  intro v member
  exact by_rank (rank v) v rfl member

/-- Parent/rank witnesses, root inclusion and edge closure certify exactness.

This connects the local witness conditions to the abstract certificate theorem.
It does not prove that an external implementation checks those conditions.
-/
theorem ranked_exact_reachability {V : Type u}
    {Edge : V → V → Prop} {root : V} {R : V → Prop}
    (rank : V → Nat)
    (root_mem : R root)
    (witnesses : ∀ v : V, R v →
      v = root ∨ ∃ p : V, R p ∧ Edge p v ∧ rank p < rank v)
    (closed : ∀ {a b : V}, R a → Edge a b → R b)
    (v : V) : R v ↔ Reach Edge root v := by
  have certificate : Certificate Edge root R := {
    root_mem := root_mem
    sound := soundness_from_ranked_witnesses rank witnesses
    closed := closed
  }
  exact exact_reachability certificate v

/-- The obligations are consistent: actual reachability satisfies them. -/
theorem reachability_has_certificate {V : Type u} (Edge : V → V → Prop)
    (root : V) : Certificate Edge root (Reach Edge root) := by
  constructor
  · exact Reach.refl
  · intro v reachable
    exact reachable
  · intro a b reachable edge
    exact Reach.step reachable edge

/-- Original imports point from importer to dependency; queries walk backward. -/
def ReverseEdge {V : Type u} (Import : V → V → Prop) (a b : V) : Prop :=
  Import b a

/-- Specialization matching the Python certificate's original-edge orientation. -/
theorem exact_dependents {V : Type u}
    (Import : V → V → Prop) {root : V} {R : V → Prop}
    (rank : V → Nat)
    (root_mem : R root)
    (witnesses : ∀ v : V, R v →
      v = root ∨ ∃ p : V, R p ∧ Import v p ∧ rank p < rank v)
    (closed : ∀ {importer imported : V},
      R imported → Import importer imported → R importer)
    (v : V) : R v ↔ Reach (ReverseEdge Import) root v := by
  exact ranked_exact_reachability (Edge := ReverseEdge Import)
    rank root_mem witnesses closed v

end RepoProof

-- Expected audit result: these declarations do not depend on any axioms.
#print axioms RepoProof.complete
#print axioms RepoProof.exact_reachability
#print axioms RepoProof.soundness_from_ranked_witnesses
#print axioms RepoProof.ranked_exact_reachability
#print axioms RepoProof.reachability_has_certificate
#print axioms RepoProof.exact_dependents
