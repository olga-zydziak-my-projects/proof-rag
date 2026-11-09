import Checker
set_option autoImplicit false

namespace RepoProof

/-- The original directed edges, partitioned into ordered finite blocks. -/
structure BlockedGraph (n : Nat) where
  blocks : List (List (Fin n × Fin n))

/-- Hints name an actual block and position; neither index is trusted. -/
structure EnhancedWitness (n : Nat) where
  parent : Fin n
  rank : Nat
  hint : Option (Nat × Nat)

structure EnhancedCertificate (n : Nat) where
  entries : Fin n → Option (EnhancedWitness n)

def eraseGraph {n : Nat} (g : BlockedGraph n) : FiniteGraph n :=
  ⟨g.blocks.flatten⟩

def EnhancedWitness.erase {n : Nat} (w : EnhancedWitness n) : Witness n :=
  ⟨w.parent, w.rank⟩

def eraseHints {n : Nat} (c : EnhancedCertificate n) : FiniteCertificate n :=
  ⟨fun v => (c.entries v).map EnhancedWitness.erase⟩

def fastMember {n : Nat} (c : EnhancedCertificate n) (v : Fin n) : Bool :=
  (c.entries v).isSome

def edgeHint {n : Nat} (g : BlockedGraph n) (v : Fin n)
    (w : EnhancedWitness n) : Bool :=
  match w.hint with
  | none => false
  | some (block, position) =>
    ((g.blocks[block]?).bind (fun b => b[position]?)) == some (v, w.parent)

/-- The parent record is inspected once; its membership and rank come from it. -/
def fastLocalCheck {n : Nat} (g : BlockedGraph n) (root : Fin n)
    (c : EnhancedCertificate n) (v : Fin n) : Bool :=
  match c.entries v with
  | none => true
  | some w => if v == root then w.parent == root && w.rank == 0 && w.hint.isNone else
      match c.entries w.parent with
      | none => false
      | some p => edgeHint g v w && decide (p.rank < w.rank)

def fastIndexCheck {n : Nat} (g : BlockedGraph n) (root : Fin n)
    (c : EnhancedCertificate n) (i : Nat) : Bool :=
  if h : i < n then fastLocalCheck g root c ⟨i, h⟩ else false

def fastClosure {n : Nat} (c : EnhancedCertificate n) (e : Fin n × Fin n) : Bool :=
  !fastMember c e.2 || fastMember c e.1

def fastCheck {n : Nat} (g : BlockedGraph n) (root : Fin n)
    (c : EnhancedCertificate n) : Bool :=
  fastMember c root && (List.range n).all (fastIndexCheck g root c) &&
    g.blocks.all (fun b => b.all (fastClosure c))

theorem erase_member {n : Nat} (c : EnhancedCertificate n) (v : Fin n) :
    member (eraseHints c) v = fastMember c v := by
  cases h : c.entries v <;> simp [member, eraseHints, fastMember, h]

theorem edgeHint_sound {n : Nat} (g : BlockedGraph n) (v : Fin n)
    (w : EnhancedWitness n) (accepted : edgeHint g v w = true) :
    (v, w.parent) ∈ (eraseGraph g).edges := by
  cases hh : w.hint with
  | none => simp [edgeHint, hh] at accepted
  | some hint =>
    have lookup : ((g.blocks[hint.1]?).bind (fun b => b[hint.2]?)) =
        some (v, w.parent) := by simpa [edgeHint, hh] using accepted
    cases hb : g.blocks[hint.1]? with
    | none => simp [hb] at lookup
    | some b =>
      have hp : b[hint.2]? = some (v, w.parent) := by simpa [hb] using lookup
      exact List.mem_flatten.mpr ⟨b, List.mem_of_getElem? hb, List.mem_of_getElem? hp⟩

theorem fastLocalCheck_refines {n : Nat} (g : BlockedGraph n) (root : Fin n)
    (c : EnhancedCertificate n) (v : Fin n)
    (accepted : fastLocalCheck g root c v = true) :
    localCheck (eraseGraph g) root (eraseHints c) v = true := by
  cases hv : c.entries v with
  | none => simp [localCheck, eraseHints, hv]
  | some w =>
    by_cases eq : v = root
    · subst v
      have hs : ((w.parent == root && w.rank == 0) && w.hint.isNone) = true := by
        simpa [fastLocalCheck, hv] using accepted
      have h : (w.parent == root && w.rank == 0) = true :=
        (Bool.and_eq_true_iff.mp hs).1
      simpa [localCheck, eraseHints, hv, EnhancedWitness.erase] using h
    · cases hp : c.entries w.parent with
      | none => simp [fastLocalCheck, hv, eq, hp] at accepted
      | some p =>
        have h : edgeHint g v w = true ∧ p.rank < w.rank := by
          simpa [fastLocalCheck, hv, eq, hp] using accepted
        have edge := edgeHint_sound g v w h.1
        simp [localCheck, eraseHints, hv, eq, EnhancedWitness.erase, member, rank, hp, edge, h.2]

theorem fastCheck_refines {n : Nat} (g : BlockedGraph n) (root : Fin n)
    (c : EnhancedCertificate n) (accepted : fastCheck g root c = true) :
    check (eraseGraph g) root (eraseHints c) = true := by
  have parts := Bool.and_eq_true_iff.mp accepted
  have root_and_local := Bool.and_eq_true_iff.mp parts.1
  unfold check
  apply Bool.and_eq_true_iff.mpr
  constructor
  · apply Bool.and_eq_true_iff.mpr
    constructor
    · simpa only [erase_member] using root_and_local.1
    · apply List.all_eq_true.mpr
      intro i hi
      have hl := List.all_eq_true.mp root_and_local.2 i hi
      by_cases bound : i < n
      · have hlocal : fastLocalCheck g root c ⟨i, bound⟩ = true := by
          simpa only [fastIndexCheck, dite_eq_left bound] using hl
        simpa only [indexCheck, dite_eq_left bound] using
          fastLocalCheck_refines g root c ⟨i, bound⟩ hlocal
      · simp [fastIndexCheck, bound] at hl
  · apply List.all_eq_true.mpr
    intro e he
    obtain ⟨b, hb, hm⟩ := List.mem_flatten.mp he
    have h := List.all_eq_true.mp (List.all_eq_true.mp parts.2 b hb) e hm
    simpa only [fastClosure, erase_member] using h

theorem fastCheck_exact {n : Nat} (g : BlockedGraph n) (root : Fin n)
    (c : EnhancedCertificate n) (accepted : fastCheck g root c = true) (v : Fin n) :
    fastMember c v = true ↔
      Reach (ReverseEdge (fun a b => (a, b) ∈ (eraseGraph g).edges)) root v := by
  simpa only [erase_member] using
    check_exact (eraseGraph g) root (eraseHints c) (fastCheck_refines g root c accepted) v

/-- Direct range pieces avoid repeatedly dropping prefixes of the global range. -/
theorem all_range'_split (start left right : Nat) (p : Nat → Bool)
    (hl : (List.range' start left).all p = true)
    (hr : (List.range' (start + left) right).all p = true) :
    (List.range' start (left + right)).all p = true := by
  rw [← List.range'_append_1, List.all_append, Bool.and_eq_true]
  exact ⟨hl, hr⟩

/-- Assemble already checked elements without reducing their predicates again. -/
theorem all_cons_true {α : Type} (x : α) (xs : List α) (p : α → Bool)
    (hx : p x = true) (hxs : xs.all p = true) :
    (x :: xs).all p = true := by
  simpa only [List.all_cons, Bool.and_eq_true] using And.intro hx hxs

/-- Each actual edge block may be checked independently; the full checker remains unchanged. -/
theorem fastCheck_of_parts {n : Nat} (g : BlockedGraph n) (root : Fin n)
    (c : EnhancedCertificate n)
    (hr : fastMember c root = true)
    (hl : (List.range' 0 n).all (fastIndexCheck g root c) = true)
    (hc : g.blocks.all (fun b => b.all (fastClosure c)) = true) :
    fastCheck g root c = true := by
  simpa only [fastCheck, List.range_eq_range', Bool.and_eq_true] using
    And.intro (And.intro hr hl) hc

end RepoProof

#print axioms RepoProof.eraseGraph
#print axioms RepoProof.eraseHints
#print axioms RepoProof.fastMember
#print axioms RepoProof.edgeHint
#print axioms RepoProof.fastLocalCheck
#print axioms RepoProof.fastIndexCheck
#print axioms RepoProof.fastClosure
#print axioms RepoProof.fastCheck
#print axioms RepoProof.erase_member
#print axioms RepoProof.edgeHint_sound
#print axioms RepoProof.fastLocalCheck_refines
#print axioms RepoProof.fastCheck_refines
#print axioms RepoProof.fastCheck_exact
#print axioms RepoProof.all_range'_split
#print axioms RepoProof.all_cons_true
#print axioms RepoProof.fastCheck_of_parts
