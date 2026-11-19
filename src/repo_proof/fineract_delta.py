"""Update witnessed literal hits by comparing pinned Git trees."""

import os
import re

from .fineract_oracle import ResultMismatch, SourceUnavailable, batch_objects, check_object, tree_entries
from .git_search import git_command, git_read


def update_hits(store, old, new, directories, literal, hits, scratch):
    """Carry hits across equal trees and check the new regular blobs of changed paths."""
    reads = {kind: {"count": 0, "bytes": 0} for kind in ("commit", "tree", "blob")}
    stats = {"tree_entries_compared": 0, "changed_regular_paths": 0, "new_regular_paths_checked": 0,
             "git_objects_read": reads}
    if old == new:
        return hits, stats

    def account(kind, raw):
        reads[kind]["count"] += 1
        reads[kind]["bytes"] += len(raw)

    for pin in (old, new):
        oid = pin["commit"]
        raw = git_read(store, "cat-file", "commit", oid)
        check_object(oid, "commit", raw)
        account("commit", raw)
        if raw.partition(b"\n")[0] != b"tree " + pin["root_tree"].encode("ascii"):
            raise SourceUnavailable("pinned Git commit does not identify the pinned root tree")

    scopes = tuple(directory.encode("utf-8") + b"/" for directory in directories)
    trees = {None: {}}

    def entries(oid):
        if oid not in trees:
            raw = git_read(store, "cat-file", "tree", oid)
            check_object(oid, "tree", raw)
            account("tree", raw)
            trees[oid] = {name: (mode, child) for mode, name, child in tree_entries(raw)}
        return trees[oid]

    def regular_oid(entry):
        return entry[1] if entry and entry[0] in (b"100644", b"100755") else None

    def tree_oid(entry):
        return entry[1] if entry and entry[0] == b"40000" else None

    changes = {}

    def walk(a, b, prefix):
        if a == b:
            return
        left, right = entries(a), entries(b)
        for name in left.keys() | right.keys():
            stats["tree_entries_compared"] += 1
            before, after = left.get(name), right.get(name)
            if before == after:
                continue
            path = prefix + name
            directory = path + b"/"
            if not scopes or directory.startswith(scopes) or any(scope.startswith(directory) for scope in scopes):
                walk(tree_oid(before), tree_oid(after), directory)
            if not scopes or path.startswith(scopes):
                old_oid, new_oid = regular_oid(before), regular_oid(after)
                if old_oid != new_oid:
                    changes[path.decode("utf-8", "surrogateescape")] = old_oid, new_oid

    walk(old["root_tree"], new["root_tree"], b"")
    added = sum(before is None for before, _ in changes.values())
    removed = sum(after is None for _, after in changes.values())
    if old["regular_paths"] + added - removed != new["regular_paths"]:
        raise SourceUnavailable("regular path counts differ from the manifest delta")

    new_oids = sorted({after for _, after in changes.values() if after is not None})
    pattern = re.compile(re.escape(literal.encode("ascii")))
    matches = {}
    if new_oids:
        env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
        for oid, raw in batch_objects(git_command(store), env, new_oids, "blob", scratch):
            account("blob", raw)
            occurrence = pattern.search(raw)
            if occurrence is not None:
                offset = occurrence.start()
                matches[oid] = (oid, offset, 1 + raw.count(b"\n", 0, offset))

    for path, (before, after) in changes.items():
        witness = hits.pop(path, None)
        if witness is not None and witness[0] != before:
            raise ResultMismatch("verified base witness differs from the old Git tree")
        if after in matches:
            hits[path] = matches[after]
    stats.update(changed_regular_paths=len(changes),
                 new_regular_paths_checked=sum(after is not None for _, after in changes.values()))
    return hits, stats
