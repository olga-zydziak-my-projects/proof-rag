import copy
from types import SimpleNamespace
import unittest
from repo_proof.stage5_answer_v2 import expected_answer, check_answer, render_answer, check_human
from repo_proof.stage5_v2 import ROOT, canonical


def fixture():
    return SimpleNamespace(pin={'repository':'fixture', 'commit':'a'*40,
        'tree':'b'*40, 'manifest_sha256':'c'*64},
        blobs=(SimpleNamespace(path='dependent.mojom'), SimpleNamespace(path=ROOT)),
        graph={'nodes':['dependent.mojom',ROOT],'edges':[['dependent.mojom',ROOT]]},
        certificate={'candidates':[{'node':'dependent.mojom'}, {'node':ROOT}]})


def check_roundtrip(captured):
    value=expected_answer(captured)
    assert check_human(render_answer(value),captured)==check_answer(value,captured)
    assert canonical(expected_answer(captured))==canonical(value)


def check_attack(captured,attack):
    value=copy.deepcopy(expected_answer(captured))
    if attack=='omit': value['paths'].pop()
    elif attack=='add': value['paths'].append('extra.mojom')
    elif attack=='duplicate': value['paths'][0]=value['paths'][1]
    elif attack=='replace': value['paths'][0]='replacement.mojom'
    elif attack=='root': value['query']['root']='different.mojom'
    elif attack=='root_id': value['query']['root_id']=0
    elif attack=='direction': value['query']['edge_direction']='imported-to-importer'
    elif attack=='include_root': value['query']['include_root']=False
    elif attack=='wrong_type': value['query']['include_root']=1
    elif attack in ('commit','tree'): value['pin'][attack]='d'*40
    else: value['extra']='unverified'
    with unittest.TestCase().assertRaises(ValueError): check_answer(value,captured)
    if attack not in ('wrong_type','extra_field'):
        with unittest.TestCase().assertRaises(ValueError): check_human(render_answer(value),captured)


def check_human_mutations(captured):
    text=render_answer(expected_answer(captured))
    with unittest.TestCase().assertRaises(ValueError): check_human(text+'hidden.mojom\n',captured)
    with unittest.TestCase().assertRaises(ValueError): check_human('\n'.join(text.splitlines()[:-1])+'\n',captured)


class AnswerBindingTests(unittest.TestCase):
    def test_ambiguous_human_binding_is_rejected(self):
        captured=fixture()
        text=render_answer(expected_answer(captured))
        text=text.replace('Binding: {','Binding: {"identities":{},',1)
        with self.assertRaises(ValueError): check_human(text,captured)

    def test_returned_metadata_cannot_mutate_the_anchor(self):
        captured=fixture()
        value=expected_answer(captured)
        value['pin']['commit']='changed'
        self.assertEqual(captured.pin['commit'],'a'*40)
        with self.assertRaises(ValueError):
            check_answer(value,captured)

    def test_roundtrip(self):
        check_roundtrip(fixture())

    def test_substitutions(self):
        for attack in ['omit','add','duplicate','replace','root','root_id',
                       'direction','include_root','wrong_type','commit','tree','extra_field']:
            with self.subTest(attack=attack):
                check_attack(fixture(),attack)

    def test_human_mutations(self):
        check_human_mutations(fixture())
