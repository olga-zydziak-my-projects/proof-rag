import SourceGraphBinding
set_option autoImplicit false
namespace RepoProof.AnswerBinding
open RepoProof SourceBinding

def answerOK {n : Nat} (names : Fin n → Path) (c : EnhancedCertificate n)
    (ids : List (Fin n)) (paths : List Path) : Bool :=
  allVertices (fun v => fastMember c v == ids.contains v) &&
  decide ids.Nodup && decide (ids.map names = paths)

theorem answerOK_of_parts {n : Nat} (names : Fin n → Path) (c : EnhancedCertificate n)
    (ids : List (Fin n)) (paths : List Path)
    (coverage : allVertices (fun v => fastMember c v == ids.contains v) = true)
    (unique : ids.Nodup) (decoded : ids.map names = paths) :
    answerOK names c ids paths = true := by
  simp only [answerOK,coverage,unique,decoded,decide_true,Bool.true_and]

theorem answer_mem {n : Nat} (names : Fin n → Path) (c : EnhancedCertificate n)
    (ids : List (Fin n)) (paths : List Path) (h : answerOK names c ids paths = true) (p : Path) :
    p ∈ paths ↔ ∃ v, names v = p ∧ fastMember c v = true := by
  have parts : (allVertices (fun v => fastMember c v == ids.contains v) = true ∧ ids.Nodup) ∧
      ids.map names = paths := by simpa only [answerOK,Bool.and_eq_true,decide_eq_true_eq] using h
  rw [←parts.2,List.mem_map]
  constructor
  · rintro ⟨v,mem,same⟩
    have hv := allVertices_at _ parts.1.1 v
    have member : fastMember c v = true := by simpa [mem] using hv
    exact ⟨v,same,member⟩
  · rintro ⟨v,same,member⟩
    have hv := allVertices_at _ parts.1.1 v
    have mem : v ∈ ids := by simpa [member] using hv
    exact ⟨v,mem,same⟩

theorem answer_nodup {n : Nat} (names : Fin n → Path) (inverse : Path → Option (Fin n))
    (mapping : mappingOK names inverse = true) (c : EnhancedCertificate n)
    (ids : List (Fin n)) (paths : List Path) (h : answerOK names c ids paths = true) : paths.Nodup := by
  have parts : (allVertices (fun v => fastMember c v == ids.contains v) = true ∧ ids.Nodup) ∧
      ids.map names = paths := by simpa only [answerOK,Bool.and_eq_true,decide_eq_true_eq] using h
  rw [←parts.2]
  exact List.Pairwise.map names (fun _ _ different same =>
    different (mapping_injective names inverse mapping same)) parts.1.2

theorem source_to_answer {n : Nat} (names : Fin n → Path) (inverse : Path → Option (Fin n))
    (files : Fin n → File n) (g : BlockedGraph n) (root : Fin n) (c : EnhancedCertificate n)
    (ids : List (Fin n)) (paths : List Path)
    (hs : sourceBinding names inverse files g = true) (hg : fastCheck g root c = true)
    (ha : answerOK names c ids paths = true) (p : Path) :
    p ∈ paths ↔ ∃ v, names v = p ∧ Reach (ReverseEdge (Import names files)) root v := by
  rw [answer_mem names c ids paths ha]
  constructor
  · rintro ⟨v,name,mem⟩
    exact ⟨v,name,(source_exact names inverse files g root c hs hg v).mp mem⟩
  · rintro ⟨v,name,reach⟩
    exact ⟨v,name,(source_exact names inverse files g root c hs hg v).mpr reach⟩
end RepoProof.AnswerBinding
#print axioms RepoProof.AnswerBinding.answer_mem
#print axioms RepoProof.AnswerBinding.answer_nodup
#print axioms RepoProof.AnswerBinding.source_to_answer
