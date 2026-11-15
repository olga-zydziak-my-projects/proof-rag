"""Array reverse index, BFS producer, independently structured reference/checker.

Integer IDs are local to the ordered file table, never global file identities.
"""
from array import array
from collections import deque
import numpy as np


def validate_graph(n, edges):
    edges = np.asarray(edges, dtype=np.int64).reshape((-1, 2))
    if type(n) is not int or n < 1 or np.any(edges < 0) or np.any(edges >= n):
        raise ValueError('graph bounds')
    if len(edges) and (len(np.unique(edges, axis=0)) != len(edges)):
        raise ValueError('duplicate edges')
    return edges


def reverse_index(n, edges):
    order = np.lexsort((edges[:, 0], edges[:, 1]))
    targets = edges[order, 1]
    offsets = np.r_[0, np.cumsum(np.bincount(targets, minlength=n))]
    return offsets, edges[order, 0]


def search(n, index, root):
    if type(root) is not int or not 0 <= root < n:
        raise ValueError('root bounds')
    offsets, sources = index
    parent = np.full(n, -2, dtype=np.int64)
    rank = np.full(n, -1, dtype=np.int64)
    parent[root], rank[root] = -1, 0
    queue = deque([root])
    while queue:
        v = queue.popleft()
        for a in sources[offsets[v]:offsets[v+1]]:
            if rank[a] < 0:
                parent[a], rank[a] = v, rank[v]+1
                queue.append(int(a))
    return np.flatnonzero(rank >= 0), parent, rank


def traverse(n, index, root):
    """Baseline reverse BFS query without certificate production."""
    if type(root) is not int or not 0 <= root < n:
        raise ValueError('root bounds')
    offsets, sources = index
    seen = np.zeros(n, dtype=bool)
    seen[root] = True
    queue = deque([root])
    while queue:
        v = queue.popleft()
        for a in sources[offsets[v]:offsets[v+1]]:
            if not seen[a]:
                seen[a] = True
                queue.append(int(a))
    return np.flatnonzero(seen)


def check_certificate(n, edges, root, ids, parents, ranks):
    """No traversal: parent-edge soundness and full-edge closure completeness."""
    if type(root) is not int or not 0 <= root < n:
        raise ValueError('certificate root')
    for xs in (ids, parents, ranks):
        if not isinstance(xs, np.ndarray) or xs.dtype != np.int64 or xs.ndim != 1:
            raise ValueError('certificate integer arrays')
    if (len(ids) != len(parents) or len(ids) != len(ranks) or not len(ids)
            or np.any(ids < 0) or np.any(ids >= n) or np.any(np.diff(ids) <= 0)):
        raise ValueError('certificate inventory')
    mask = np.zeros(n, dtype=bool)
    mask[ids] = True
    fullrank = np.full(n, -1, dtype=np.int64)
    fullrank[ids] = ranks
    atroot = ids == root
    if (not mask[root] or np.any(ranks < 0) or np.any(parents[atroot] != -1)
            or np.any(ranks[atroot] != 0)):
        raise ValueError('root witness')
    other = ~atroot
    ps = parents[other]
    if np.any(ps < 0) or np.any(ps >= n) or not np.all(mask[ps]):
        raise ValueError('parent inventory')
    if not np.all(ranks[other] > fullrank[ps]):
        raise ValueError('rank decrease')
    encoded = np.sort(edges[:, 0]*n+edges[:, 1])
    wanted = ids[other]*n+ps
    positions = np.searchsorted(encoded, wanted)
    if np.any(positions >= len(encoded)) or not np.array_equal(encoded[positions], wanted):
        raise ValueError('missing parent edge')
    if np.any(mask[edges[:, 1]] & ~mask[edges[:, 0]]):
        raise ValueError('incomplete reverse closure')
    return True


def reference(n, edges, root):
    """Independent dict-of-arrays DFS; no producer index, BFS or ranks."""
    incoming = {}
    for a, b in edges:
        incoming.setdefault(int(b), array('q')).append(int(a))
    visited = bytearray(n)
    visited[root] = 1
    stack = [root]
    while stack:
        v = stack.pop()
        for a in incoming.get(v, ()):
            if not visited[a]:
                visited[a] = 1
                stack.append(a)
    return np.flatnonzero(np.frombuffer(visited, dtype=np.uint8))


def fixed_point(n, edges, root):
    current = {root}
    while True:
        enlarged = current | {int(a) for a, b in edges if int(b) in current}
        if enlarged == current:
            return np.array(sorted(current), dtype=np.int64)
        current = enlarged


def synthetic(n, family, seed=808):
    """Three logical repos, no physical source files. Seed fixes extra branches."""
    rng = np.random.default_rng(seed)
    if family == 'chain':
        edges = np.column_stack((np.arange(1, n), np.arange(n-1)))
    elif family == 'modular':
        # Blocks of 100, chained internally; one inter-block bridge per block.
        a = np.arange(1, n)
        internal = a[a % 100 != 0]
        bridge = a[a % 100 == 0]
        edges = np.vstack((np.column_stack((internal, internal-1)),
                           np.column_stack((bridge, bridge-100))))
    elif family == 'cycles':
        # Last 10% isolated; directed 8-cycles plus seeded branch/bridge edges.
        live = (n*9//10)//8*8
        a = np.arange(live)
        cycle = np.column_stack((a, a//8*8+(a+1) % 8))
        b = np.arange(8, live, 8)
        branch = np.column_stack((b, b-8+rng.integers(0, 8, size=len(b))))
        edges = np.vstack((cycle, branch))
    else:
        raise ValueError('unknown synthetic family')
    edges = np.unique(edges.astype(np.int64), axis=0)
    return edges
