import SourceGraphBinding
set_option autoImplicit false
namespace RepoProof.Contextual
open RepoProof SourceBinding
abbrev Bytes := List UInt8
structure Identity where
  repository : Bytes
  commit : Bytes
  path : Bytes
  deriving DecidableEq, BEq
structure Rule where
  repository : Bytes
  commit : Bytes
  importPrefix : Bytes
  target : Option (Bytes × Bytes)
  targetPrefix : Bytes

-- Rules are an explicitly accepted specification. No build language is executed.
def ruleMatches (r : Rule) (i : Identity) (p : Bytes) : Bool :=
  r.repository == i.repository && r.commit == i.commit && r.importPrefix.isPrefixOf p
def resolve (rules : List Rule) (i : Identity) (p : Bytes) : Option (Option Identity) :=
  match rules.filter (fun r => ruleMatches r i p) with
  | [r] => match r.target with
    | none => some none
    | some (repo,rev) => some (some ⟨repo,rev,r.targetPrefix ++ p.drop r.importPrefix.length⟩)
  | _ => none

structure File (n : Nat) where
  pieces : List SourceBytes.Piece
  resolutions : List (Bytes × Option (Fin n))
  targets : List (Fin n)

def resolutionOK {n : Nat} (names : Fin n → Identity) (rules : List Rule)
    (importer : Identity) (r : Bytes × Option (Fin n)) : Bool :=
  decide (resolve rules importer r.1 = some (r.2.map names))
def fileOK {n : Nat} (names : Fin n → Identity) (rules : List Rule)
    (v : Fin n) (f : File n) : Bool :=
  SourceBytes.checked SourceBytes.initial f.pieces &&
  SourceBytes.finish (SourceBytes.endState SourceBytes.initial f.pieces) &&
  decide (SourceBytes.events f.pieces = f.resolutions.map Prod.fst) &&
  f.resolutions.all (resolutionOK names rules (names v)) &&
  f.targets.all (fun t => f.resolutions.any (fun r => r.2 == some t)) &&
  f.resolutions.all (fun r => match r.2 with | none => true | some t => f.targets.contains t)

theorem fileOK_of_parts {n : Nat} (names : Fin n → Identity) (rules : List Rule)
    (v : Fin n) (f : File n)
    (hs : SourceBytes.checked SourceBytes.initial f.pieces = true)
    (hf : SourceBytes.finish (SourceBytes.endState SourceBytes.initial f.pieces) = true)
    (he : SourceBytes.events f.pieces = f.resolutions.map Prod.fst)
    (hr : f.resolutions.all (resolutionOK names rules (names v)) = true)
    (ha : f.targets.all (fun t => f.resolutions.any (fun r => r.2 == some t)) = true)
    (hb : f.resolutions.all (fun r => match r.2 with | none => true | some t => f.targets.contains t) = true) :
    fileOK names rules v f = true := by
  simp only [fileOK,hs,hf,he,decide_true,hr,ha,hb,Bool.true_and]

def Import {n : Nat} (names : Fin n → Identity) (rules : List Rule)
    (files : Fin n → File n) (a b : Fin n) : Prop :=
  ∃ p, SourceBytes.sourceImport (SourceBytes.textBytes (files a).pieces) p ∧
    resolve rules (names a) p = some (some (names b))

theorem target_iff {n : Nat} (names : Fin n → Identity) (rules : List Rule)
    (inj : Function.Injective names) (files : Fin n → File n) (a b : Fin n)
    (h : fileOK names rules a (files a) = true) :
    b ∈ (files a).targets ↔ Import names rules files a b := by
  simp only [fileOK, Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨⟨hs,hf⟩,he⟩,hr⟩,ha⟩,hb⟩ := h
  constructor
  · intro ht
    have ex : ∃ r ∈ (files a).resolutions, r.2 = some b := by
      simpa using List.all_eq_true.mp ha b ht
    obtain ⟨⟨p,t⟩,mem,eq⟩ := ex
    change t = some b at eq
    subst t
    refine ⟨p, (SourceBytes.import_iff_events _ hs hf p).mpr ?_, ?_⟩
    · rw [he]
      exact List.mem_map.mpr ⟨(p,some b),mem,rfl⟩
    · simpa [resolutionOK] using List.all_eq_true.mp hr (p,some b) mem
  · rintro ⟨p,hp,res⟩
    have event := (SourceBytes.import_iff_events _ hs hf p).mp hp
    rw [he] at event
    obtain ⟨⟨q,t⟩,mem,eq⟩ := List.mem_map.mp event
    change q = p at eq
    subst q
    have rr : resolve rules (names a) p = some (t.map names) := by
      simpa [resolutionOK] using List.all_eq_true.mp hr (p,t) mem
    rw [res] at rr
    cases t with
    | none => simp at rr
    | some u =>
      have same : names b = names u := by simpa using rr
      have bu := inj same
      subst u
      simpa using List.all_eq_true.mp hb (p,some b) mem

def graphOfFiles {n : Nat} (files : Fin n → File n) : FiniteGraph n :=
  SourceBinding.graphOfFiles (fun v => ⟨[],[],(files v).targets⟩)

theorem source_exact {n : Nat} (names : Fin n → Identity) (rules : List Rule)
    (files : Fin n → File n) (g : BlockedGraph n) (root : Fin n) (c : EnhancedCertificate n)
    (inj : Function.Injective names)
    (hf : ∀ v, fileOK names rules v (files v) = true)
    (he : (graphOfFiles files).edges = (eraseGraph g).edges)
    (hg : fastCheck g root c = true) (v : Fin n) :
    fastMember c v = true ↔ Reach (ReverseEdge (Import names rules files)) root v := by
  apply (fastCheck_exact g root c hg v).trans
  apply SourceBinding.reach_congr
  intro a b
  change (b,a) ∈ (eraseGraph g).edges ↔ Import names rules files b a
  rw [←he]
  exact (SourceBinding.graph_mem _ b a).trans (target_iff names rules inj files b a (hf b))

theorem answer_exact {n : Nat} (names : Fin n → Identity) (rules : List Rule)
    (files : Fin n → File n) (g : BlockedGraph n) (root : Fin n) (c : EnhancedCertificate n)
    (inj : Function.Injective names) (hf : ∀ v, fileOK names rules v (files v) = true)
    (he : (graphOfFiles files).edges = (eraseGraph g).edges)
    (hg : fastCheck g root c = true) (answer : List (Fin n))
    (ha : ∀ v, v ∈ answer ↔ fastMember c v = true) (p : Identity) :
    p ∈ answer.map names ↔ ∃ v, names v = p ∧
      Reach (ReverseEdge (Import names rules files)) root v := by
  simp only [List.mem_map]
  constructor
  · rintro ⟨v,hv,hp⟩
    exact ⟨v,hp,(source_exact names rules files g root c inj hf he hg v).mp ((ha v).mp hv)⟩
  · rintro ⟨v,hp,hv⟩
    exact ⟨v,(ha v).mpr ((source_exact names rules files g root c inj hf he hg v).mpr hv),hp⟩
end RepoProof.Contextual
#print axioms RepoProof.Contextual.target_iff
#print axioms RepoProof.Contextual.source_exact
#print axioms RepoProof.Contextual.answer_exact
