import Std
set_option autoImplicit false
namespace RepoProof.SourceBytes

/- The source specification is a deterministic byte transition system for
the Mojom import projection. It is independent of graph data and certificates.
Source chunks are canonical packed natural-number blocks; the automaton consumes UInt8 values. Full Mojom body/type validation
remains an additional operational check, not an assumed extraction theorem. -/
inductive Mode where
  | normal | word | slash | line | block | star | quoted | escaped
  deriving DecidableEq, Repr
inductive Expect where
  | idle | path | semi
  deriving DecidableEq, Repr
structure Control where
  good : Bool := true
  mode : Mode := .normal
  word : Nat := 0
  stack : List UInt8 := []
  header : Bool := true
  expect : Expect := .idle
  path : List UInt8 := []
  collect : Bool := false
  utf8 : Nat := 0
  deriving DecidableEq, Repr

def initial : Control := {}
def asciiWord (c : UInt8) : Bool :=
  (97 ≤ c && c ≤ 122) || (65 ≤ c && c ≤ 90) || (48 ≤ c && c ≤ 57) || c == 95
def white (c : UInt8) : Bool := c == 32 || c == 9 || c == 13 || c == 10
def canonicalBytes : List UInt8 → Nat → Bool → Bool
  | [], kind, _ => kind == 3
  | c::cs, kind, first =>
    if c == 47 then kind == 3 && canonicalBytes cs 0 false
    else decide (32 ≤ c.toNat) && c != 127 && c != 92 && c != 34 &&
      !(first && c == 58) &&
      canonicalBytes cs (if c == 46 then min (kind+1) 3 else 3) first

def startWord (c : UInt8) : Nat :=
  if c == 105 then 1 else if c == 115 then 15 else if c == 117 then 21
  else if c == 101 then 26 else if c == 99 then 30 else if c == 102 then 35 else 0
def nextWord (w : Nat) (c : UInt8) : Nat :=
  match w with
  | 1 => if c == 109 then 2 else if c == 110 then 7 else 0
  | 2 => if c == 112 then 3 else 0
  | 3 => if c == 111 then 4 else 0
  | 4 => if c == 114 then 5 else 0
  | 5 => if c == 116 then 6 else 0
  | 7 => if c == 116 then 8 else 0
  | 8 => if c == 101 then 9 else 0
  | 9 => if c == 114 then 10 else 0
  | 10 => if c == 102 then 11 else 0
  | 11 => if c == 97 then 12 else 0
  | 12 => if c == 99 then 13 else 0
  | 13 => if c == 101 then 14 else 0
  | 15 => if c == 116 then 16 else 0
  | 16 => if c == 114 then 17 else 0
  | 17 => if c == 117 then 18 else 0
  | 18 => if c == 99 then 19 else 0
  | 19 => if c == 116 then 20 else 0
  | 21 => if c == 110 then 22 else 0
  | 22 => if c == 105 then 23 else 0
  | 23 => if c == 111 then 24 else 0
  | 24 => if c == 110 then 25 else 0
  | 26 => if c == 110 then 27 else 0
  | 27 => if c == 117 then 28 else 0
  | 28 => if c == 109 then 29 else 0
  | 30 => if c == 111 then 31 else 0
  | 31 => if c == 110 then 32 else 0
  | 32 => if c == 115 then 33 else 0
  | 33 => if c == 116 then 34 else 0
  | 35 => if c == 101 then 36 else 0
  | 36 => if c == 97 then 37 else 0
  | 37 => if c == 116 then 38 else 0
  | 38 => if c == 117 then 39 else 0
  | 39 => if c == 114 then 40 else 0
  | 40 => if c == 101 then 41 else 0
  | _ => 0
def escapeChar (c : UInt8) : Bool :=
  asciiWord c || [46, 126, 33, 61, 38, 94, 45, 92, 63, 39, 34].contains c
def bad (q : Control) : Control := {q with good := false}
def flush (q : Control) : Control :=
  let r := {q with mode := .normal, word := 0}
  if q.word == 6 then
    if q.header && q.stack.isEmpty && q.expect == .idle then {r with expect := .path}
    else bad r
  else if q.expect != .idle then bad r
  else if q.stack.isEmpty && [20,25,14,29,34,41].contains q.word
    then {r with header := false}
  else r

def normal (q : Control) (c : UInt8) : Control × Option (List UInt8) :=
  if !q.good then (q,none)
  else if asciiWord c then ({q with mode := .word, word := startWord c},none)
  else if white c then (q,none)
  else if c == 47 then ({q with mode := .slash},none)
  else if c == 34 then
    if q.expect == .semi then (bad q,none)
    else ({q with mode := .quoted, collect := q.expect == .path, path := []},none)
  else if c == 59 then
    if q.expect == .semi then ({q with expect := .idle, path := [], collect := false},some q.path.reverse)
    else if q.expect == .path then (bad q,none) else (q,none)
  else if q.expect != .idle then (bad q,none)
  else if [40, 91, 123].contains c then ({q with stack := c :: q.stack},none)
  else if [41, 93, 125].contains c then
    match q.stack with
    | [] => (bad q,none)
    | h :: t =>
      if (h == 40 && c == 41) || (h == 91 && c == 93) || (h == 123 && c == 125)
      then ({q with stack := t},none) else (bad q,none)
  else if [45, 43, 63, 61, 62, 60, 44, 124, 38, 46, 64].contains c then (q,none)
  else (bad q,none)

def lexicalStep (q : Control) (c : UInt8) : Control × Option (List UInt8) :=
  if !q.good then (q,none) else
  match q.mode with
  | .normal => normal q c
  | .word =>
    if asciiWord c then
      if q.word == 0 then (q,none) else ({q with word := nextWord q.word c},none)
    else normal (flush q) c
  | .slash =>
    if c == 47 then ({q with mode := .line},none)
    else if c == 42 then ({q with mode := .block},none) else (bad q,none)
  | .line => (if c == 10 then {q with mode := .normal} else q,none)
  | .block => (if c == 42 then {q with mode := .star} else q,none)
  | .star => (if c == 47 then {q with mode := .normal}
              else if c == 42 then q else {q with mode := .block},none)
  | .quoted =>
    if c == 10 then (bad q,none)
    else if c == 92 then
      (if q.collect then bad q else {q with mode := .escaped},none)
    else if c == 34 then
      if q.collect then
        (if canonicalBytes q.path.reverse 0 true then {q with mode := .normal, expect := .semi}
          else bad q,none)
      else ({q with mode := .normal},none)
    else (if q.collect then {q with path := c::q.path} else q,none)
  | .escaped => (if escapeChar c then {q with mode := .quoted} else bad q,none)

/-- Canonical UTF-8: no overlong forms, surrogate encodings or scalars above 10FFFF. -/
def utf8Step (state : Nat) (b : UInt8) : Nat :=
  if state == 0 then
    if b < 128 then 0
    else if 194 ≤ b && b ≤ 223 then 1
    else if b == 224 then 4
    else if b == 237 then 5
    else if (225 ≤ b && b ≤ 236) || (238 ≤ b && b ≤ 239) then 2
    else if b == 240 then 6
    else if b == 244 then 7
    else if 241 ≤ b && b ≤ 243 then 3 else 255
  else if state == 4 then if 160 ≤ b && b ≤ 191 then 1 else 255
  else if state == 5 then if 128 ≤ b && b ≤ 159 then 1 else 255
  else if state == 6 then if 144 ≤ b && b ≤ 191 then 2 else 255
  else if state == 7 then if 128 ≤ b && b ≤ 143 then 2 else 255
  else if 1 ≤ state && state ≤ 3 && 128 ≤ b && b ≤ 191 then state-1 else 255

def step (q : Control) (c : UInt8) : Control × Option (List UInt8) :=
  if !q.good then (q,none) else
  if q.utf8 == 0 && c < 128 then lexicalStep q c else
  let u := utf8Step q.utf8 c
  if u == 255 then (bad {q with utf8 := u},none)
  else lexicalStep {q with utf8 := u} c

def finish (q : Control) : Bool :=
  let r := if q.mode == .word then flush q
           else if q.mode == .line then {q with mode := .normal} else q
  r.good && r.mode == .normal && r.stack.isEmpty && r.expect == .idle && r.utf8 == 0

def run (q : Control) : List UInt8 → Control × List (List UInt8)
  | [] => (q,[])
  | c :: cs =>
    let (r,e) := step q c
    let (s,es) := run r cs
    (s,e.toList ++ es)

inductive Trace : Control → List UInt8 → Control → List (List UInt8) → Prop where
  | nil (q : Control) : Trace q [] q []
  | cons (q : Control) (c : UInt8) (cs : List UInt8) (r : Control) (e : Option (List UInt8))
      (s : Control) (es : List (List UInt8)) :
      step q c = (r,e) → Trace r cs s es → Trace q (c::cs) s (e.toList ++ es)

theorem trace_iff_run (q : Control) (cs : List UInt8) (s : Control) (es : List (List UInt8)) :
    Trace q cs s es ↔ run q cs = (s,es) := by
  constructor
  · intro h
    induction h with
    | nil q => rfl
    | cons q c cs r e s es hs htail ih => simp only [run, hs, ih]
  · intro h
    induction cs generalizing q s es with
    | nil => cases h; exact Trace.nil q
    | cons c cs ih =>
      cases hs : step q c with
      | mk r e =>
        cases hr : run r cs with
        | mk t ts =>
          simp only [run, hs, hr, Prod.mk.injEq] at h
          obtain ⟨rfl,rfl⟩ := h
          exact Trace.cons q c cs r e t ts hs (ih r t ts hr)

theorem run_append (q : Control) (xs ys : List UInt8) :
    run q (xs ++ ys) =
      let (r,es) := run q xs
      let (s,fs) := run r ys
      (s,es ++ fs) := by
  induction xs generalizing q with
  | nil => rfl
  | cons c cs ih =>
    cases hs : step q c with
    | mk r e =>
      cases hr : run r cs with
      | mk t ts =>
        cases hy : run t ys with
        | mk u us => simp only [List.cons_append, run, hs, ih, hr, hy, List.append_assoc]

structure Block where
  size : Nat
  packed : Nat

def unpack : Nat → Nat → List UInt8
  | 0, _ => []
  | n+1, x => UInt8.ofNat (x % 256) :: unpack n (x / 256)
def Block.bytes (b : Block) : List UInt8 := unpack b.size b.packed
def Block.valid (b : Block) : Bool := decide (b.packed < 256 ^ b.size)

structure Piece where
  block : Block
  after : Control
  events : List (List UInt8)

def textBytes (pieces : List Piece) : List UInt8 := pieces.flatMap (fun p => p.block.bytes)
def events (pieces : List Piece) : List (List UInt8) := pieces.flatMap Piece.events
def endState (q : Control) : List Piece → Control
  | [] => q
  | p :: ps => endState p.after ps
def checked (q : Control) : List Piece → Bool
  | [] => true
  | p :: ps => p.block.valid && decide (run q p.block.bytes = (p.after,p.events)) && checked p.after ps

theorem checked_cons (q : Control) (p : Piece) (ps : List Piece)
    (valid : p.block.valid = true) (h : run q p.block.bytes = (p.after,p.events)) (tail : checked p.after ps = true) :
    checked q (p::ps) = true := by simp only [checked, valid, h, decide_true, Bool.true_and, tail]

theorem checked_sound (q : Control) (ps : List Piece) (h : checked q ps = true) :
    run q (textBytes ps) = (endState q ps,events ps) := by
  induction ps generalizing q with
  | nil => rfl
  | cons p ps ih =>
    have pieces : (p.block.valid = true ∧ run q p.block.bytes = (p.after,p.events)) ∧ checked p.after ps = true := by
      simpa only [checked, Bool.and_eq_true, decide_eq_true_eq] using h
    have parts := And.intro pieces.1.2 pieces.2
    change run q (p.block.bytes ++ textBytes ps) = (endState p.after ps,p.events ++ events ps)
    simp only [run_append,parts.1,ih p.after parts.2]

def sourceImport (sourceBytes : List UInt8) (path : List UInt8) : Prop :=
  ∃ q es, Trace initial sourceBytes q es ∧ finish q = true ∧ path ∈ es

theorem import_iff_events (ps : List Piece) (h : checked initial ps = true)
    (done : finish (endState initial ps) = true) (path : List UInt8) :
    sourceImport (textBytes ps) path ↔ path ∈ events ps := by
  have runEq := checked_sound initial ps h
  constructor
  · rintro ⟨q,es,t,_,mem⟩
    have eq := (trace_iff_run initial (textBytes ps) q es).mp t
    rw [runEq] at eq
    cases eq
    exact mem
  · intro mem
    exact ⟨_,_,(trace_iff_run _ _ _ _).mpr runEq,done,mem⟩
end RepoProof.SourceBytes

#print axioms RepoProof.SourceBytes.trace_iff_run
#print axioms RepoProof.SourceBytes.run_append
#print axioms RepoProof.SourceBytes.checked_sound
#print axioms RepoProof.SourceBytes.import_iff_events
