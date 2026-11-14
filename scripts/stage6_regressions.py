"""Current-code regression view with the frozen Stage 5 README fixture.

The historical Stage 5 preflight tests require the Stage 4 README byte for
byte. Their sources and historical preservation checks remain unchanged.
The main working tree retains the user-requested Stage 6 README.
"""
import json
from pathlib import Path
import shutil
import subprocess

from stage4_support import file_info


def code_inventory(project):
    return {p.relative_to(project).as_posix(): file_info(p)
            for base in ('src', 'scripts', 'tests', 'formal')
            for p in (project / base).rglob('*') if p.suffix in ('.py', '.lean')}


def prepare_regression_view(project, folder):
    project, folder = Path(project).resolve(), Path(folder).resolve()
    if not folder.is_relative_to(project / 'local'):
        raise ValueError('regression view must be a new local project subdirectory')
    folder.mkdir(exist_ok=False)
    expected = code_inventory(project)
    for name in ('src', 'scripts', 'tests', 'formal', 'vendor', 'verification',
                 'docs', 'examples'):
        shutil.copytree(project / name, folder / name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    # Project anchor commands only read history. Fixture Git repositories
    # created by tests retain their own independent metadata directories.
    (folder / '.git').write_text('gitdir: ' + (project / '.git').as_posix() + '\n',
                                encoding='utf-8')
    for name in ('README.md', '.gitattributes', '.gitignore', 'corpus.lock.json',
                 'lean-toolchain', 'pyproject.toml'):
        shutil.copyfile(project / name, folder / name)
    # These actual-data binding tests must run, including in the isolated view.
    shutil.copytree(project / 'local/stage2', folder / 'local/stage2')
    baseline = json.loads((project / 'verification/stage5-baseline.json').read_bytes())
    historical = subprocess.check_output([
        'git', '-c', 'safe.directory=' + project.as_posix(), 'show',
        'e4984110743131d04ad984eaaa48d33d72867336:README.md'], cwd=project)
    (folder / 'README.md').write_bytes(historical)
    fixture = file_info(folder / 'README.md')
    if fixture != baseline['files']['README.md']:
        raise ValueError('historical README fixture differs from frozen Stage 5 inventory')
    if code_inventory(folder) != expected:
        raise ValueError('regression view changed current code or tests')
    return {'directory': str(folder), 'current_code_and_tests': expected,
            'readme_fixture': fixture, 'current_readme': file_info(project / 'README.md'),
            'reason': 'Unchanged Stage 5 tests require historical README identity',
            'only_content_override': 'README.md'}


def verify_regression_view(project, evidence):
    folder = Path(evidence['directory'])
    if (code_inventory(project) != evidence['current_code_and_tests']
            or code_inventory(folder) != evidence['current_code_and_tests']
            or file_info(folder / 'README.md') != evidence['readme_fixture']
            or file_info(Path(project) / 'README.md') != evidence['current_readme']):
        raise ValueError('regression view or main project changed during tests')
    return True
