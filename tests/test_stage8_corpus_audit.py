"""Offline checks of complete pinned inventory and patch-path rejection."""
from hashlib import sha1
from copy import deepcopy
import unittest

from repo_proof.stage8_corpus_audit import check_inventory, check_reviewed_rules, _patch_paths


class CorpusInventoryTests(unittest.TestCase):
    def setUp(self):
        self.blob = sha1(b'blob 1\0x').hexdigest()
        tree = b'100644 file.patch\0' + bytes.fromhex(self.blob)
        self.tree = sha1(b'tree ' + str(len(tree)).encode() + b'\0' + tree).hexdigest()
        root = b'40000 nested\0' + bytes.fromhex(self.tree)
        self.root = sha1(b'tree ' + str(len(root)).encode() + b'\0' + root).hexdigest()
        self.rows = [{'path': 'patches/nested', 'type': 'tree', 'mode': '040000', 'sha': self.tree},
                     {'path': 'patches/nested/file.patch', 'type': 'blob', 'mode': '100644', 'sha': self.blob}]

    def test_complete_inventory_is_anchored_at_every_directory(self):
        check_inventory(self.rows, 'patches', self.root)
        for rows in (self.rows[:1], self.rows[1:], self.rows + self.rows[:1]):
            with self.assertRaises(ValueError):
                check_inventory(rows, 'patches', self.root)

    def test_substituted_blob_identity_is_rejected(self):
        rows = [dict(row) for row in self.rows]
        rows[1]['sha'] = '0' * 40
        with self.assertRaises(ValueError):
            check_inventory(rows, 'patches', self.root)

    def test_patch_rename_checks_both_old_and_new_paths(self):
        self.assertEqual(_patch_paths(b'diff --git a/old.mojom b/new.mojom\n'), {'old.mojom', 'new.mojom'})
        with self.assertRaises(ValueError):
            _patch_paths(b'+++ b/source.mojom\n')
        with self.assertRaises(ValueError):
            _patch_paths(b'diff --git unknown b/source.mojom\n')

    def test_rules_must_execute_independently_reviewed_mounts(self):
        manifest = {'repositories': [{'repo_id': name, 'commit': digit * 40}
                                      for name, digit in [('electron', '1'), ('brave', '2'), ('chromium', '3')]],
                    'rules': [{'id': 'brave-brave', 'from': ['brave', '2' * 40], 'prefix': 'brave/',
                               'to': ['brave', '2' * 40], 'target_prefix': '', 'evidence': 'brave-package.json'},
                              {'id': 'electron-url', 'from': ['electron', '1' * 40], 'prefix': 'url/',
                               'to': ['chromium', '3' * 40], 'target_prefix': 'url/', 'evidence': 'electron-DEPS'}]}
        imports = {'electron': ['url/mojom/url.mojom'], 'brave': ['brave/local.mojom'], 'chromium': []}
        check_reviewed_rules(manifest, imports)
        for field, value in [('prefix', ''), ('to', ['electron', '1' * 40]),
                             ('target_prefix', 'wrong/'), ('evidence', 'unreviewed')]:
            changed = deepcopy(manifest)
            changed['rules'][0][field] = value
            with self.assertRaisesRegex(ValueError, 'reviewed'):
                check_reviewed_rules(changed, imports)


if __name__ == '__main__':
    unittest.main()
