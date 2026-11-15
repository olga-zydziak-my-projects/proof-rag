"""Independent complete grammar audit for stage 8 blocked graph exports."""
import json
import re
from review_stage4_binding import TreeParser, section
from stage5_v2_audit_bytes import route_body


def audit_graph(text, n, edges, root, ids, parents, ranks):
    position = 0

    def consume(line):
        nonlocal position
        token = line + '\n'
        if not text.startswith(token, position):
            raise ValueError('graph export outside closed grammar at ' + str(position))
        position += len(token)

    def definition(name, declaration, multiline=False):
        body = section(text, name)
        consume('def ' + name + declaration + ' :=' + ('' if multiline else ' ' + body))
        if multiline:
            consume('  ' + body)
        return body

    for line in ('import FastChecker', 'import ProofTiming', 'set_option maxRecDepth 100000',
                 'set_option maxHeartbeats 0', 'namespace Stage8Graph', 'open RepoProof'):
        consume(line)
    names = []
    path_blocks = []
    for i in range((n + 63) // 64):
        name = 'pathBlock' + str(i)
        body = section(text, name)
        consume('def ' + name + ' : Array String := #[')
        block = json.loads(body[1: ])
        for j, value in enumerate(block):
            consume('  ' + json.dumps(value, ensure_ascii=False) + (',' if j + 1 < len(block) else ''))
        consume(']')
        names.extend(block)
        path_blocks.append(name)
    if names != [str(i).zfill(len(str(n))) for i in range(n)]:
        raise ValueError('complete node table mismatch')
    if definition('nodePaths', ' : Array String') != ' ++ '.join(path_blocks):
        raise ValueError('path block references')
    fin = r'⟨([0-9]+), by decide \+kernel⟩'
    edge_pattern = r'\(' + fin + ', ' + fin + r'\)'
    decoded_edges = []
    blocks = []
    for i in range((len(edges) + 63) // 64):
        name = 'edgeBlock' + str(i)
        body = section(text, name)
        pairs = re.findall(edge_pattern, body)
        if not re.fullmatch(r'\[\s*' + edge_pattern + r'(?:,\s*' + edge_pattern + r')*\s*\]', body):
            raise ValueError('edge block syntax')
        consume(f'def {name} : List (Fin {n} × Fin {n}) := [')
        for j, (a, b) in enumerate(pairs):
            consume(f'  (⟨{a}, by decide +kernel⟩, ⟨{b}, by decide +kernel⟩)' + (',' if j + 1 < len(pairs) else ''))
        consume(']')
        decoded_edges.extend((int(a), int(b)) for a, b in pairs)
        blocks.append(name)
    if decoded_edges != [tuple(map(int, e)) for e in edges]:
        raise ValueError('complete graph mismatch')
    if definition('graph', f' : BlockedGraph {n}') != '⟨[' + ', '.join(blocks) + ']⟩':
        raise ValueError('graph block references')
    if definition('root', f' : Fin {n}') != f'⟨{root}, by decide +kernel⟩':
        raise ValueError('root mismatch')
    decoded = []
    for i in range((n + 63) // 64):
        body = definition('witnessBlock' + str(i), f' (v : Fin {n}) : Option (EnhancedWitness {n})', True)
        parser = TreeParser(body)
        decoded.extend(parser.witnesses(i * 64, min(n, (i + 1) * 64)))
        parser.complete()
    body = definition('certificate', f' : EnhancedCertificate {n}')
    if not body.startswith('⟨fun v =>\n  ') or not body.endswith('⟩'):
        raise ValueError('certificate wrapper')
    parser = TreeParser(body[len('⟨fun v =>'): -1])
    parser.routes(0, (n + 63) // 64)
    parser.complete()
    locations = {e: (i // 64, i % 64) for i, e in enumerate(decoded_edges)}
    expected = [None] * n
    for v, p, r in zip(ids, parents, ranks):
        v, p, r = int(v), int(p), int(r)
        expected[v] = (root if v == root else p, r, None if v == root else locations[(v, p)])
    if decoded != expected:
        raise ValueError('complete witness/hint mismatch')
    for line in ('theorem accepted : fastCheck graph root certificate = true := by',
                 '  apply fastCheck_of_parts', '  · timed_kernel_decide', '  ·'):
        consume(line)
    def interval(start, length, indent):
        if length <= 64:
            consume(indent + 'timed_kernel_decide')
            return
        half = length // 2
        consume(indent + f"apply all_range'_split {start} {half} {length - half}")
        consume(indent + '·')
        interval(start, half, indent + '  ')
        consume(indent + '·')
        interval(start + half, length - half, indent + '  ')
    interval(0, n, '    ')
    consume('  · change ([' + ', '.join(blocks) + ']).all (fun b => b.all (fastClosure certificate)) = true')
    for _ in blocks:
        consume('    apply all_cons_true')
        consume('    · timed_kernel_decide')
    for line in ('    rfl',
        'theorem erased_accepted : check (eraseGraph graph) root (eraseHints certificate) = true :=',
        '  fastCheck_refines graph root certificate accepted', f'theorem exact (v : Fin {n}) :',
        '    fastMember certificate v = true ↔',
        '      Reach (ReverseEdge (fun a b => (a,b) ∈ (eraseGraph graph).edges)) root v :=',
        '  fastCheck_exact graph root certificate accepted v',
        f'def answer : List (Fin {n}) := (List.finRange {n}).filter (fastMember certificate)',
        f'theorem answer_exact (v : Fin {n}) : v ∈ answer ↔',
        '    Reach (ReverseEdge (fun a b => (a,b) ∈ (eraseGraph graph).edges)) root v := by',
        '  simpa [answer, List.mem_filter] using exact v', 'end Stage8Graph',
        '#print axioms Stage8Graph.accepted', '#print axioms Stage8Graph.erased_accepted', '#print axioms Stage8Graph.exact',
        '#print axioms Stage8Graph.answer_exact'):
        consume(line)
    if position != len(text):
        raise ValueError('unparsed graph export suffix')
    return True


def audit_source(text, identities, sources, rules, edges, ids):
    """Read every literal, every byte and every proof command in the module."""
    n = len(identities)
    position = 0
    def consume(line):
        nonlocal position
        token = line + '\n'
        if not text.startswith(token, position):
            raise ValueError('source export outside closed grammar at ' + str(position))
        position += len(token)
    def body(name, decl, multiline=False):
        value = section(text, name)
        consume('def ' + name + decl + ' :=' + ('' if multiline else ' ' + value))
        if multiline:
            consume('  ' + value)
        return value
    array = r'\[(?:[0-9]+(?:, [0-9]+)*)?\]'
    fin = r'⟨([0-9]+), by decide \+kernel⟩'
    for line in ('import ContextualSourceBinding', 'import GraphProof',
                 'set_option maxRecDepth 100000', 'set_option maxHeartbeats 0',
                 'namespace Stage8Source', 'open RepoProof RepoProof.Contextual'):
        consume(line)
    for i, identity in enumerate(identities):
        value = body('identity' + str(i), ' : Identity')
        match = re.fullmatch('⟨(' + array + '), (' + array + '), (' + array + ')⟩', value)
        if not match or [bytes(json.loads(v)).decode('utf-8') for v in match.groups()] != list(identity):
            raise ValueError('identity byte table mismatch')
    value = body('names', f' (v : Fin {n}) : Identity', True)
    if route_body(value, r'identity\d+', n) != ['identity' + str(i) for i in range(n)]:
        raise ValueError('identity routing mismatch')
    consume('def rules : List Rule := [')
    rule_pattern = '  ⟨(' + array + '), (' + array + '), (' + array + '), (none|some \\((' + array + '), (' + array + ')\\)), (' + array + ')⟩'
    for i, rule in enumerate(rules):
        line = text[position: text.index('\n', position)]
        match = re.fullmatch(rule_pattern + (',' if i + 1 < len(rules) else ''), line)
        if not match:
            raise ValueError('resolver rule syntax')
        repo, rev, prefix, target, tr, tc, tp = match.groups()
        decode = lambda v: bytes(json.loads(v)).decode('utf-8')
        actual = [decode(repo), decode(rev), decode(prefix), None if target == 'none' else [decode(tr), decode(tc)], decode(tp)]
        if actual != [*rule['from'], rule['prefix'], rule['to'], rule['target_prefix']]:
            raise ValueError('complete resolver specification mismatch')
        consume(line)
    consume(']')
    control = r'⟨(?:true|false), \.(?:normal|word|slash|line|block|star|quoted|escaped), [0-9]+, ' + array + r', (?:true|false), \.(?:idle|path|semi), ' + array + r', (?:true|false), [0-9]+⟩'
    events = r'\[(?:' + array + r'(?:, ' + array + r')*)?\]'
    piece = r'⟨⟨[0-9]+, 0x[0-9a-f]+⟩, ' + control + ', ' + events + '⟩'
    resolution = r'\(' + array + ', (?:none|some ' + fin + r')\)'
    graph_targets = {i: [] for i in range(n)}
    for a, b in edges:
        graph_targets[int(a)].append(int(b))
    for i, data in enumerate(sources):
        value = body('file' + str(i), f' : File {n}')
        match = re.fullmatch('⟨(\\[(?:' + piece + '(?:, ' + piece + ')*)?\\]), (\\[(?:' + resolution + '(?:, ' + resolution + ')*)?\\]), (\\[(?:' + fin + '(?:, ' + fin + ')*)?\\])⟩', value)
        if not match:
            raise ValueError('source file literal grammar')
        # Capture indices inside Fin literals are immaterial to framing.
        packed = re.findall(r'⟨⟨([0-9]+), 0x([0-9a-f]+)⟩,', value)
        chunks = []
        for size, raw in packed:
            size, packed_number = int(size), int(raw, 16)
            if packed_number >= 256 ** size:
                raise ValueError('noncanonical packed source')
            chunks.append(packed_number.to_bytes(size, 'little'))
        if b''.join(chunks) != data:
            raise ValueError('complete source bytes mismatch')
        targets = value.rsplit('], [', 1)[1][: -2]
        if [int(v) for v in re.findall(fin, targets)] != sorted(set(graph_targets[i])):
            raise ValueError('source target table mismatch')
        consume(f'theorem file{i}_checked : fileOK names rules ⟨{i}, by decide +kernel⟩ file{i} = true := by')
        consume('  apply fileOK_of_parts')
        consume('  ·')
        for _ in packed:
            for line in ('    apply SourceBytes.checked_cons', '    · decide +kernel', '    · decide +kernel'):
                consume(line)
        consume('    rfl')
        for _ in range(5):
            consume('  · decide +kernel')
    value = body('files', f' (v : Fin {n}) : File {n}', True)
    if route_body(value, r'file\d+', n) != ['file' + str(i) for i in range(n)]:
        raise ValueError('complete source routing mismatch')
    for line in ('theorem names_injective : Function.Injective names := by', '  intro a b h',
        '  have checked : ∀ a b, names a = names b → a = b := by decide +kernel', '  exact checked a b h',
        f'theorem files_checked (v : Fin {n}) : fileOK names rules v (files v) = true := by'):
        consume(line)
    for i in range(n):
        for line in (f'  by_cases h{i} : v.val = {i}',
            f'  · have hv : v = ⟨{i}, by decide +kernel⟩ := Fin.ext h{i}',
            '    subst v', f'    exact file{i}_checked'):
            consume(line)
    for line in ('  have bound := v.isLt', '  omega',
        'theorem graph_checked : (graphOfFiles files).edges = (eraseGraph Stage8Graph.graph).edges := by decide +kernel'):
        consume(line)
    value = body('answer', f' : List (Fin {n})')
    if not re.fullmatch(r'\[' + fin + '(?:, ' + fin + r')*\]', value) or [int(v) for v in re.findall(fin, value)] != list(map(int, ids)):
        raise ValueError('complete source answer mismatch')
    for line in (f'theorem answer_checked (v : Fin {n}) : v ∈ answer ↔ fastMember Stage8Graph.certificate v = true := by',
        '  have checked : ∀ v, v ∈ answer ↔ fastMember Stage8Graph.certificate v = true := by decide +kernel',
        '  exact checked v', 'def payload : List Identity := answer.map names',
        'theorem source_to_answer (p : Identity) : p ∈ payload ↔ ∃ v, names v = p ∧',
        '    Reach (ReverseEdge (Import names rules files)) Stage8Graph.root v :=',
        '  answer_exact names rules files Stage8Graph.graph Stage8Graph.root Stage8Graph.certificate',
        '    names_injective files_checked graph_checked Stage8Graph.accepted answer answer_checked p',
        'end Stage8Source', '#print axioms Stage8Source.names_injective',
        '#print axioms Stage8Source.files_checked', '#print axioms Stage8Source.graph_checked',
        '#print axioms Stage8Source.answer_checked', '#print axioms Stage8Source.source_to_answer'):
        consume(line)
    if position != len(text):
        raise ValueError('unparsed source module suffix')
    return True
