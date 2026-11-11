import Std
set_option autoImplicit false
namespace RepoProof.Source

/- The source specification is a deterministic character transition system for
the Mojom import projection. It is independent of graph data and certificates.
Characters denote their exact UTF-8 encoding. Full Mojom body/type validation
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
  stack : List Char := []
  header : Bool := true
  expect : Expect := .idle
  path : List Char := []
  collect : Bool := false
  deriving DecidableEq, Repr

def initial : Control := {}
def asciiWord (c : Char) : Bool :=
  ('a' ≤ c && c ≤ 'z') || ('A' ≤ c && c ≤ 'Z') || ('0' ≤ c && c ≤ '9') || c == '_'
def white (c : Char) : Bool := c == ' ' || c == '\t' || c == '\r' || c == '\n'
def canonicalChars : List Char → Nat → Bool → Bool
  | [], kind, _ => kind == 3
  | c::cs, kind, first =>
    if c == '/' then kind == 3 && canonicalChars cs 0 false
    else decide (32 ≤ c.toNat) && c != '\x7f' && c != '\\' && c != '"' &&
      !(first && c == ':') &&
      canonicalChars cs (if c == '.' then min (kind+1) 3 else 3) first

def startWord (c : Char) : Nat :=
  if c == 'i' then 1 else if c == 's' then 15 else if c == 'u' then 21
  else if c == 'e' then 26 else if c == 'c' then 30 else if c == 'f' then 35 else 0
def nextWord (w : Nat) (c : Char) : Nat :=
  match w with
  | 1 => if c == 'm' then 2 else if c == 'n' then 7 else 0
  | 2 => if c == 'p' then 3 else 0
  | 3 => if c == 'o' then 4 else 0
  | 4 => if c == 'r' then 5 else 0
  | 5 => if c == 't' then 6 else 0
  | 7 => if c == 't' then 8 else 0
  | 8 => if c == 'e' then 9 else 0
  | 9 => if c == 'r' then 10 else 0
  | 10 => if c == 'f' then 11 else 0
  | 11 => if c == 'a' then 12 else 0
  | 12 => if c == 'c' then 13 else 0
  | 13 => if c == 'e' then 14 else 0
  | 15 => if c == 't' then 16 else 0
  | 16 => if c == 'r' then 17 else 0
  | 17 => if c == 'u' then 18 else 0
  | 18 => if c == 'c' then 19 else 0
  | 19 => if c == 't' then 20 else 0
  | 21 => if c == 'n' then 22 else 0
  | 22 => if c == 'i' then 23 else 0
  | 23 => if c == 'o' then 24 else 0
  | 24 => if c == 'n' then 25 else 0
  | 26 => if c == 'n' then 27 else 0
  | 27 => if c == 'u' then 28 else 0
  | 28 => if c == 'm' then 29 else 0
  | 30 => if c == 'o' then 31 else 0
  | 31 => if c == 'n' then 32 else 0
  | 32 => if c == 's' then 33 else 0
  | 33 => if c == 't' then 34 else 0
  | 35 => if c == 'e' then 36 else 0
  | 36 => if c == 'a' then 37 else 0
  | 37 => if c == 't' then 38 else 0
  | 38 => if c == 'u' then 39 else 0
  | 39 => if c == 'r' then 40 else 0
  | 40 => if c == 'e' then 41 else 0
  | _ => 0
def escapeChar (c : Char) : Bool :=
  asciiWord c || ['.', '~', '!', '=', '&', '^', '-', '\\', '?', '\'', '"'].contains c
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

def normal (q : Control) (c : Char) : Control × Option String :=
  if !q.good then (q,none)
  else if asciiWord c then ({q with mode := .word, word := startWord c},none)
  else if white c then (q,none)
  else if c == '/' then ({q with mode := .slash},none)
  else if c == '"' then
    if q.expect == .semi then (bad q,none)
    else ({q with mode := .quoted, collect := q.expect == .path, path := []},none)
  else if c == ';' then
    if q.expect == .semi then ({q with expect := .idle, path := [], collect := false},some (String.ofList q.path.reverse))
    else if q.expect == .path then (bad q,none) else (q,none)
  else if q.expect != .idle then (bad q,none)
  else if ['(', '[', '{'].contains c then ({q with stack := c :: q.stack},none)
  else if [')', ']', '}'].contains c then
    match q.stack with
    | [] => (bad q,none)
    | h :: t =>
      if (h == '(' && c == ')') || (h == '[' && c == ']') || (h == '{' && c == '}')
      then ({q with stack := t},none) else (bad q,none)
  else if ['-', '+', '?', '=', '>', '<', ',', '|', '&', '.', '@'].contains c then (q,none)
  else (bad q,none)

def step (q : Control) (c : Char) : Control × Option String :=
  if !q.good then (q,none) else
  match q.mode with
  | .normal => normal q c
  | .word =>
    if asciiWord c then
      if q.word == 0 then (q,none) else ({q with word := nextWord q.word c},none)
    else normal (flush q) c
  | .slash =>
    if c == '/' then ({q with mode := .line},none)
    else if c == '*' then ({q with mode := .block},none) else (bad q,none)
  | .line => (if c == '\n' then {q with mode := .normal} else q,none)
  | .block => (if c == '*' then {q with mode := .star} else q,none)
  | .star => (if c == '/' then {q with mode := .normal}
              else if c == '*' then q else {q with mode := .block},none)
  | .quoted =>
    if c == '\n' then (bad q,none)
    else if c == '\\' then
      (if q.collect then bad q else {q with mode := .escaped},none)
    else if c == '"' then
      if q.collect then
        (if canonicalChars q.path.reverse 0 true then {q with mode := .normal, expect := .semi}
          else bad q,none)
      else ({q with mode := .normal},none)
    else (if q.collect then {q with path := c::q.path} else q,none)
  | .escaped => (if escapeChar c then {q with mode := .quoted} else bad q,none)

def finish (q : Control) : Bool :=
  let r := if q.mode == .word then flush q
           else if q.mode == .line then {q with mode := .normal} else q
  r.good && r.mode == .normal && r.stack.isEmpty && r.expect == .idle

def run (q : Control) : List Char → Control × List String
  | [] => (q,[])
  | c :: cs =>
    let (r,e) := step q c
    let (s,es) := run r cs
    (s,e.toList ++ es)

inductive Trace : Control → List Char → Control → List String → Prop where
  | nil (q : Control) : Trace q [] q []
  | cons (q : Control) (c : Char) (cs : List Char) (r : Control) (e : Option String)
      (s : Control) (es : List String) :
      step q c = (r,e) → Trace r cs s es → Trace q (c::cs) s (e.toList ++ es)

theorem trace_iff_run (q : Control) (cs : List Char) (s : Control) (es : List String) :
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

theorem run_append (q : Control) (xs ys : List Char) :
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

structure Piece where
  text : String
  after : Control
  events : List String

def textChars (pieces : List Piece) : List Char := pieces.flatMap (fun p => p.text.toList)
def events (pieces : List Piece) : List String := pieces.flatMap Piece.events
def endState (q : Control) : List Piece → Control
  | [] => q
  | p :: ps => endState p.after ps
def checked (q : Control) : List Piece → Bool
  | [] => true
  | p :: ps => decide (run q p.text.toList = (p.after,p.events)) && checked p.after ps

theorem checked_cons (q : Control) (p : Piece) (ps : List Piece)
    (h : run q p.text.toList = (p.after,p.events)) (tail : checked p.after ps = true) :
    checked q (p::ps) = true := by simp only [checked, h, decide_true, Bool.true_and, tail]

theorem checked_sound (q : Control) (ps : List Piece) (h : checked q ps = true) :
    run q (textChars ps) = (endState q ps,events ps) := by
  induction ps generalizing q with
  | nil => rfl
  | cons p ps ih =>
    have parts : run q p.text.toList = (p.after,p.events) ∧ checked p.after ps = true := by
      simpa only [checked, Bool.and_eq_true, decide_eq_true_eq] using h
    change run q (p.text.toList ++ textChars ps) = (endState p.after ps,p.events ++ events ps)
    simp only [run_append,parts.1,ih p.after parts.2]

def sourceImport (bytesAsChars : List Char) (path : String) : Prop :=
  ∃ q es, Trace initial bytesAsChars q es ∧ finish q = true ∧ path ∈ es

theorem import_iff_events (ps : List Piece) (h : checked initial ps = true)
    (done : finish (endState initial ps) = true) (path : String) :
    sourceImport (textChars ps) path ↔ path ∈ events ps := by
  have runEq := checked_sound initial ps h
  constructor
  · rintro ⟨q,es,t,_,mem⟩
    have eq := (trace_iff_run initial (textChars ps) q es).mp t
    rw [runEq] at eq
    cases eq
    exact mem
  · intro mem
    exact ⟨_,_,(trace_iff_run _ _ _ _).mpr runEq,done,mem⟩
end RepoProof.Source

#print axioms RepoProof.Source.trace_iff_run
#print axioms RepoProof.Source.run_append
#print axioms RepoProof.Source.checked_sound
#print axioms RepoProof.Source.import_iff_events
