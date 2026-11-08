from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def test_docker_installs_package_and_make_install_is_complete():
    assert 'pip install --no-cache-dir ./prototype' in (ROOT/'Dockerfile').read_text()
    assert '-e prototype' in (ROOT/'Makefile').read_text()
def test_security_and_prototype_execute_real_checks():
    text=(ROOT/'.github/workflows/security.yml').read_text()
    assert 'pip-audit' in text and 'bandit' in text and 'gitleaks' in text and 'run: echo' not in text
    assert 'adjudication.cli run' in (ROOT/'.github/workflows/prototype.yml').read_text()
def test_all_confidential_outputs_ignored():
    import subprocess
    r=subprocess.run(['git','check-ignore','output/a.json','data/private.pdf','any.xlsx','prototype/output/b.csv'],cwd=ROOT,capture_output=True,text=True)
    assert len(r.stdout.splitlines())==4
