import SourceByteScanner
import FastChecker
set_option autoImplicit false
namespace RepoProof.SourceBinding
open RepoProof
abbrev Path := List UInt8

def allVertices {n : Nat} (p : Fin n → Bool) : Bool :=
  (List.range n).all (fun i => if h : i<n then p ⟨i,h⟩ else false)
theorem allVertices_at {n : Nat} (p : Fin n → Bool) (h : allVertices p = true) (v : Fin n) :
    p v = true := by
  have t := List.all_eq_true.mp h v.val (List.mem_range.mpr v.isLt)
  simpa only [dite_eq_left v.isLt] using t
theorem allVertices_intro {n : Nat} (p : Fin n → Bool) (h : ∀ v,p v = true) :
    allVertices p = true := by
  apply List.all_eq_true.mpr
  intro i hi
  have bound := List.mem_range.mp hi
  simpa only [dite_eq_left bound] using h ⟨i,bound⟩
theorem index_from {n : Nat} (p : Fin n → Bool) (v : Fin n) (h : p v = true) :
    (if b : v.val<n then p ⟨v.val,b⟩ else false) = true := by
  simpa only [dite_eq_left v.isLt] using h
theorem allVertices_of_range {n : Nat} (p : Fin n → Bool)
    (h : (List.range' 0 n).all (fun i => if b : i<n then p ⟨i,b⟩ else false) = true) :
    allVertices p = true := by simpa only [allVertices,List.range_eq_range'] using h
theorem range_cons (start len : Nat) (p : Nat → Bool) (h : p start = true)
    (tail : (List.range' (start+1) len).all p = true) :
    (List.range' start (len+1)).all p = true := by
  change (p start && (List.range' (start+1) len).all p) = true
  exact Bool.and_eq_true_iff.mpr ⟨h,tail⟩

def mappingOK {n : Nat} (names : Fin n → Path) (inverse : Path → Option (Fin n)) : Bool :=
  allVertices (fun v => inverse (names v) == some v)
theorem mapping_injective {n : Nat} (names : Fin n → Path) (inverse : Path → Option (Fin n))
    (h : mappingOK names inverse = true) : Function.Injective names := by
  intro a b same
  have ha : inverse (names a) = some a := by simpa using allVertices_at _ h a
  have hb : inverse (names b) = some b := by simpa using allVertices_at _ h b
  rw [same,hb] at ha
  exact (Option.some.inj ha).symm

structure File (n : Nat) where
  pieces : List SourceBytes.Piece
  resolved : List (Path × Option (Fin n))
  targets : List (Fin n)

def resolveOK {n : Nat} (names : Fin n → Path) (r : Path × Option (Fin n)) : Bool :=
  match r.2 with
  | some v => r.1 == names v
  | none => allVertices (fun v => r.1 != names v)
theorem resolve_none_of_inverse {n : Nat} (names : Fin n → Path)
    (inverse : Path → Option (Fin n)) (h : mappingOK names inverse = true)
    (p : Path) (absent : inverse p = none) : resolveOK names (p,none) = true := by
  change allVertices (fun v => p != names v) = true
  apply allVertices_intro
  intro v
  have present : inverse (names v) = some v := by simpa using allVertices_at _ h v
  have notEq : p ≠ names v := by
    intro same
    rw [←same,absent] at present
    cases present
  simpa using notEq
def forwardOK {n : Nat} (f : File n) : Bool :=
  f.targets.all (fun v => f.resolved.any (fun r => r.2 == some v))
def backwardOK {n : Nat} (f : File n) : Bool :=
  f.resolved.all (fun r => match r.2 with | none => true | some v => f.targets.contains v)
def fileOK {n : Nat} (names : Fin n → Path) (f : File n) : Bool :=
  SourceBytes.checked SourceBytes.initial f.pieces &&
  SourceBytes.finish (SourceBytes.endState SourceBytes.initial f.pieces) &&
  decide (SourceBytes.events f.pieces = f.resolved.map Prod.fst) &&
  f.resolved.all (resolveOK names) && forwardOK f && backwardOK f

theorem fileOK_of_parts {n : Nat} (names : Fin n → Path) (f : File n)
    (hs : SourceBytes.checked SourceBytes.initial f.pieces = true)
    (hf : SourceBytes.finish (SourceBytes.endState SourceBytes.initial f.pieces) = true)
    (he : SourceBytes.events f.pieces = f.resolved.map Prod.fst)
    (hr : f.resolved.all (resolveOK names) = true)
    (ha : forwardOK f = true) (hb : backwardOK f = true) : fileOK names f = true := by
  simp only [fileOK,hs,hf,he,decide_true,hr,ha,hb,Bool.true_and]

theorem file_target_iff {n : Nat} (names : Fin n → Path) (injective : Function.Injective names)
    (f : File n) (h : fileOK names f = true) (v : Fin n) :
    v ∈ f.targets ↔ SourceBytes.sourceImport (SourceBytes.textBytes f.pieces) (names v) := by
  have parts := h
  simp only [fileOK,Bool.and_eq_true,decide_eq_true_eq] at parts
  obtain ⟨⟨⟨⟨⟨hs,hf⟩,he⟩,hr⟩,ha⟩,hb⟩ := parts
  rw [SourceBytes.import_iff_events f.pieces hs hf,he]
  constructor
  · intro hv
    have existsR : ∃ r ∈ f.resolved, r.2 = some v := by
      simpa [forwardOK] using List.all_eq_true.mp ha v hv
    obtain ⟨⟨p,t⟩,mem,ht⟩ := existsR
    change t = some v at ht
    subst t
    have hp : p = names v := by simpa [resolveOK] using List.all_eq_true.mp hr (p,some v) mem
    exact List.mem_map.mpr ⟨(p,some v),mem,hp⟩
  · intro hv
    obtain ⟨⟨p,t⟩,mem,hp⟩ := List.mem_map.mp hv
    change p = names v at hp
    subst p
    have resolve := List.all_eq_true.mp hr (names v,t) mem
    cases t with
    | none =>
      have hn : allVertices (fun w => names v != names w) = true := by simpa [resolveOK] using resolve
      have no := allVertices_at _ hn v
      simp at no
    | some u =>
      have equal : names v = names u := by simpa [resolveOK] using resolve
      have vu := injective equal
      subst u
      have back := List.all_eq_true.mp hb (names v,some v) mem
      simpa [backwardOK] using back

def graphOfFiles {n : Nat} (files : Fin n → File n) : FiniteGraph n :=
  ⟨(List.range n).flatMap (fun i => if h : i<n then
    (files ⟨i,h⟩).targets.map (fun p => (⟨i,h⟩,p)) else [])⟩
theorem graph_mem {n : Nat} (files : Fin n → File n) (a b : Fin n) :
    (a,b) ∈ (graphOfFiles files).edges ↔ b ∈ (files a).targets := by
  constructor
  · intro h
    obtain ⟨i,hi,edge⟩ := List.mem_flatMap.mp h
    have bound := List.mem_range.mp hi
    simp only [dite_eq_left bound,List.mem_map] at edge
    obtain ⟨p,hp,eq⟩ := edge
    cases eq
    exact hp
  · intro h
    apply List.mem_flatMap.mpr
    refine ⟨a.val,List.mem_range.mpr a.isLt,?_⟩
    simp only [dite_eq_left a.isLt,List.mem_map]
    exact ⟨b,h,rfl⟩

def sourceBinding {n : Nat} (names : Fin n → Path) (inverse : Path → Option (Fin n))
    (files : Fin n → File n) (g : BlockedGraph n) : Bool :=
  mappingOK names inverse && allVertices (fun v => fileOK names (files v)) &&
  decide ((graphOfFiles files).edges = (eraseGraph g).edges)
theorem sourceBinding_of_parts {n : Nat} (names : Fin n → Path) (inverse : Path → Option (Fin n))
    (files : Fin n → File n) (g : BlockedGraph n)
    (hm : mappingOK names inverse = true)
    (hf : allVertices (fun v => fileOK names (files v)) = true)
    (he : (graphOfFiles files).edges = (eraseGraph g).edges) :
    sourceBinding names inverse files g = true := by
  simp only [sourceBinding,hm,hf,he,decide_true,Bool.true_and]

def Import {n : Nat} (names : Fin n → Path) (files : Fin n → File n) (a b : Fin n) : Prop :=
  SourceBytes.sourceImport (SourceBytes.textBytes (files a).pieces) (names b)
theorem source_edge_iff {n : Nat} (names : Fin n → Path) (inverse : Path → Option (Fin n))
    (files : Fin n → File n) (g : BlockedGraph n)
    (h : sourceBinding names inverse files g = true) (a b : Fin n) :
    (a,b) ∈ (eraseGraph g).edges ↔ Import names files a b := by
  have parts : (mappingOK names inverse = true ∧ allVertices (fun v => fileOK names (files v)) = true) ∧
      (graphOfFiles files).edges = (eraseGraph g).edges := by
    simpa only [sourceBinding,Bool.and_eq_true,decide_eq_true_eq] using h
  rw [←parts.2,graph_mem]
  exact file_target_iff names (mapping_injective names inverse parts.1.1) (files a)
    (allVertices_at _ parts.1.2 a) b

theorem reach_congr {V : Type} (e f : V → V → Prop) (h : ∀ a b,e a b ↔ f a b)
    (root v : V) : Reach e root v ↔ Reach f root v := by
  constructor
  · intro r
    induction r with
    | refl => exact Reach.refl
    | step _ edge ih => exact Reach.step ih ((h _ _).mp edge)
  · intro r
    induction r with
    | refl => exact Reach.refl
    | step _ edge ih => exact Reach.step ih ((h _ _).mpr edge)

theorem source_exact {n : Nat} (names : Fin n → Path) (inverse : Path → Option (Fin n))
    (files : Fin n → File n) (g : BlockedGraph n) (root : Fin n) (c : EnhancedCertificate n)
    (hs : sourceBinding names inverse files g = true) (hg : fastCheck g root c = true) (v : Fin n) :
    fastMember c v = true ↔ Reach (ReverseEdge (Import names files)) root v := by
  exact (fastCheck_exact g root c hg v).trans (reach_congr _ _
    (fun a b => source_edge_iff names inverse files g hs b a) root v)
end RepoProof.SourceBinding
#print axioms RepoProof.SourceBinding.mapping_injective
#print axioms RepoProof.SourceBinding.file_target_iff
#print axioms RepoProof.SourceBinding.source_edge_iff
#print axioms RepoProof.SourceBinding.source_exact
