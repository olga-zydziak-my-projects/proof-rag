"""Stage 6 output grammar for the fresh query kernel process.

Historical Stage 1–5 audits retain their original parser. The query process
prints only timing records and one complete axiom record per required theorem.
Every nonempty output line must match one of those two forms.
"""
import re


STANDARD_AXIOMS = frozenset({'propext', 'Classical.choice', 'Quot.sound'})
QUERY_THEOREMS = (
    'QueryProof.accepted',
    'QueryProof.erased_accepted',
    'QueryProof.paths_unique',
    'QueryProof.source_to_answer',
)
_TIMING = re.compile(r'proof_construction_ms=[0-9]+; kernel_check_and_insert_ms=[0-9]+')
_REPORT = re.compile(
    r"'([A-Za-z_][A-Za-z_0-9.]*)' "
    r'(?:does not depend on any axioms|depends on axioms: '
    r'\[([A-Za-z_][A-Za-z_0-9.]*(?:, [A-Za-z_][A-Za-z_0-9.]*)*)?\])'
)


def audit(output, names=QUERY_THEOREMS, allowed=STANDARD_AXIOMS):
    """Read all records, rejecting ambiguity and any unparsed process output."""
    names = tuple(names)
    if not names or len(set(names)) != len(names):
        raise ValueError('invalid required axiom theorem inventory')
    result = {}
    for line in output.splitlines():
        if not line or _TIMING.fullmatch(line):
            continue
        match = _REPORT.fullmatch(line)
        if match is None:
            raise ValueError('malformed query axiom process output: ' + line)
        name, raw = match.groups()
        if name not in names:
            raise ValueError('unexpected axiom report: ' + name)
        if name in result:
            raise ValueError('duplicate axiom report: ' + name)
        used = raw.split(', ') if raw else []
        if len(set(used)) != len(used):
            raise ValueError('duplicate axiom in report: ' + name)
        if not set(used) <= allowed:
            raise ValueError('unexpected axioms: ' + name + str(used))
        result[name] = used
    missing = set(names) - result.keys()
    if missing:
        raise ValueError('missing axiom reports: ' + ', '.join(sorted(missing)))
    return {name: result[name] for name in names}
