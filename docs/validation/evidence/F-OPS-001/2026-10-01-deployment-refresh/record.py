"""Run unchanged deployment assertions from a host-networked Docker Desktop runner."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.validate import gitinfo
from tests.deploy import test_compose

assert not gitinfo.dirty_files(), gitinfo.dirty_files()
source = gitinfo.head_sha()
original_docker = test_compose.docker

def desktop_docker(*args, **kwargs):
    # Compose's bind source belongs to the daemon, rather than the runner's /work mount.
    env = kwargs.get('env')
    if env and env.get('MATRIX_DATA_DIR', '').startswith('/work/'):
        kwargs['env'] = {**env, 'MATRIX_DATA_DIR': env['MATRIX_DATA_DIR'].replace(
            '/work/', '/run/desktop/mnt/host/c/scripts/unfoldedcircle-orei-hdmi-matrix-integration/', 1)}
    return original_docker(*args, **kwargs)

test_compose.docker = desktop_docker
os.environ.pop('USE_MOCK_MATRIX', None)
import pytest
result = pytest.main(['tests/deploy', '-m', 'docker', '-v', '--tb=short', '-p', 'no:cacheprovider',
                      '--basetemp=build/deploy-refresh-tmp'])
Path('build/deploy-refresh-run.json').write_text(json.dumps({
    'source_commit': source, 'branch': gitinfo.branch(), 'pytest_exit_code': int(result),
    'image': os.environ['HUB_IMAGE'], 'runner_network': 'host',
    'compose_bind_mapping': '/work/ -> /run/desktop/mnt/host/c/scripts/unfoldedcircle-orei-hdmi-matrix-integration/',
}, indent=2))
raise SystemExit(result)