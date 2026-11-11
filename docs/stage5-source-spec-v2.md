# Stage 5 byte import projection

This document specifies the relation proved in `SourceByteScanner.lean`. It does
not claim a proof of the full Chromium Mojom parser or type checker.

The input is the complete ordered sequence of bytes of a selected file. UTF-8
must be valid (including rejection of overlong encodings, surrogate encodings,
and values above U+10FFFF). Bytes are preserved: no newline, Unicode, case or
path normalization occurs. A BOM is unsupported. Packed proof blocks have an
explicit length and a natural number below 256 to that length; unpacking is
little endian and therefore preserves leading and trailing zero bytes.

The finite lexical state distinguishes normal text, words, slash, line comments,
block comments and their possible closing star, quoted strings, and escapes.
Line comments end at LF or EOF; block comments end at their first closing
delimiter. Quotes and import-like text in comments or ordinary strings do not
emit imports. Escape processing is explicit in the transition function. Import
paths containing escapes are unsupported and rejected. Newlines inside strings
are rejected. Braces, brackets and parentheses are balanced by a stack.

An exact finite keyword trie recognizes `import` and the top-level declaration
keywords `interface`, `struct`, `union`, `enum`, `const`, and `feature`. It is not
a hash. A top-level import is accepted in the header, outside all delimiters,
and consists of the keyword, a quoted canonical path and a semicolon, allowing
intervening whitespace and comments. Attributes are traversed as balanced
brackets; their conditions are not evaluated. Import events retain order and
duplicates. Top-level declaration keywords end the import header. Bare import
keywords outside the permitted position are rejected.

A canonical path is nonempty, has no empty, dot or dot-dot segment, no control
byte, DEL, backslash or quote, and no colon in its first segment. Resolution is
exact comparison with the complete selected filename mapping. Imports outside
that mapping remain recorded as external events and create no internal edge.
The resulting graph has all selected vertices, including files without imports,
and contains an edge from importer to imported selected file exactly when the
byte automaton emits its path. Multiple declarations collapse to the same graph
edge. Filename injectivity and resolution in both directions are checked.

The normative transition details are `lexicalStep`, `step`, `finish` and `Trace`
in the Lean module. `sourceImport` is defined through a trace of these byte
transitions, independently of the supplied graph or extraction event list.
`import_iff_events` connects this relation with checked per-block witnesses.
`source_edge_iff` proves both directions of the source-to-graph correspondence;
`source_to_answer` composes it with the existing exact reachability theorem and
the checked complete output path list.

The public input capture also runs the existing pinned full Mojom parser and
requires complete extraction. That is an operational malformed-body rejection,
not a formally verified full grammar. The formal theorem is specifically about
this import projection on the complete anchored bytes. The IO boundary still
assumes the Lean executable/kernel, filesystem reads, Git object verification
and the independent full byte comparison function as documented. A kernel proof
does not prove that a remote GitHub server or a displayed editor buffer is honest.
