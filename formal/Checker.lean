import Reachability
set_option autoImplicit false
namespace RepoProof
theorem all_split {α : Type} (xs : List α) (p : α → Bool) (k : Nat)
    (left : (xs.take k).all p = true) (right : (xs.drop k).all p = true) :
    xs.all p = true := by
  calc
    xs.all p = ((xs.take k) ++ (xs.drop k)).all p :=
      congrArg (fun ys => ys.all p) (List.take_append_drop k xs).symm
    _ = true := by simpa only [List.all_append, Bool.and_eq_true] using And.intro left right
structure FiniteGraph (n : Nat) where
  edges : List (Fin n × Fin n)
structure Witness (n : Nat) where
  parent : Fin n
  rank : Nat
structure FiniteCertificate (n : Nat) where
  entries : Fin n → Option (Witness n)

def member {n : Nat} (c : FiniteCertificate n) (v : Fin n) : Bool :=
  (c.entries v).isSome

def rank {n : Nat} (c : FiniteCertificate n) (v : Fin n) : Nat :=
  match c.entries v with | none => 0 | some w => w.rank

def localCheck {n : Nat} (g : FiniteGraph n) (root : Fin n)
    (c : FiniteCertificate n) (v : Fin n) : Bool :=
  match c.entries v with
  | none => true
  | some w => if v == root then w.parent == root && w.rank == 0 else
      member c w.parent && g.edges.contains (v, w.parent) && decide (rank c w.parent < w.rank)

def indexCheck {n : Nat} (g : FiniteGraph n) (root : Fin n)
    (c : FiniteCertificate n) (i : Nat) : Bool :=
  if h : i < n then localCheck g root c ⟨i, h⟩ else false

def check {n : Nat} (g : FiniteGraph n) (root : Fin n) (c : FiniteCertificate n) : Bool :=
  member c root && (List.range n).all (indexCheck g root c) &&
    g.edges.all (fun e => !member c e.2 || member c e.1)

theorem check_exact {n : Nat} (g : FiniteGraph n) (root : Fin n)
    (c : FiniteCertificate n) (accepted : check g root c = true) (v : Fin n) :
    member c v = true ↔ Reach (ReverseEdge (fun a b => (a,b) ∈ g.edges)) root v := by
  simp only [check, Bool.and_eq_true, List.all_eq_true] at accepted
  obtain ⟨⟨hr, hl⟩, hc⟩ := accepted
  apply exact_dependents (fun a b => (a,b) ∈ g.edges) (R := fun x => member c x = true) (rank c) hr (v := v)
  · intro x hx
    have hi := hl x.val (List.mem_range.mpr x.isLt)
    have h : localCheck g root c x = true := by
      simpa only [indexCheck, dite_eq_left x.isLt] using hi
    cases he : c.entries x with
    | none => simp [member, he] at hx
    | some w =>
      by_cases eq : x = root
      · exact Or.inl eq
      · right
        simp [localCheck, he, eq, Bool.and_eq_true] at h
        exact ⟨w.parent, h.1.1, by simpa using h.1.2, by simpa [rank, he] using h.2⟩
  · intro a b hb edge
    have h := hc (a,b) edge
    simpa [hb] using h

end RepoProof
#print axioms RepoProof.check_exact
#print axioms RepoProof.member
#print axioms RepoProof.rank
#print axioms RepoProof.localCheck
#print axioms RepoProof.check
#print axioms RepoProof.all_split
#print axioms RepoProof.indexCheck
