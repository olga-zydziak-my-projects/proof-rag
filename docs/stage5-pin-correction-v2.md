# Stage 5 correction annex, version 2

Authority: the user's explicit correction in this conversation. The source of
truth is corpus.lock.json from accepted Stage4 checkpoint
e4984110743131d04ad984eaaa48d33d72867336, not the erroneous earlier inventory.

Authoritative Chromium commit: 27cec857a08a0ee0e1b41f5eb18c07467a0ce093.
Authoritative root tree: 25131300fa459906dedb84bf592a8537b7848771.
The earlier 1ab171af2976555a2b12b9bca8b984c204962ba8 /
9e5b002b0ce384a82f6cb836fd3abaebab8a7da6 reference is withdrawn ONLY as an
incorrect source reference. No source checkout, corpus scope, selection rule,
query semantics, formal guarantee, success gate G1-G8 or other requirement changes.

The original contract (SHA256
5c323f4e9c2ae8d3bb498cd2b267e57ba8d4e76d09e2673c5d46979d3f44161d),
its blocked reports, all previous measurements and corpus bytes are preserved.
The old v1 preflight remains a reproducible diagnostic of the superseded input;
it is not used as the v2 input gate. Source identity still requires verification
against actual Git objects and all selected bytes, not just this textual amendment.
No gate is waived by resolving the pin. In particular G3-G7 still require proof,
answer binding, attacks and a successful operational run.
