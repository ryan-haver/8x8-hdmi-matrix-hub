"""Disposable shipped-image stack for the WP-C4 tools.validate scenarios."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tests.deploy._docker import Container, docker, free_port, unique, wait_http

root = Path.cwd()
image = 'hdmi-matrix-hub:wp-c4'
network = unique('c4-proof-net')
volume = unique('c4-proof-data')
sim = Container(unique('c4-proof-sim'), 'hdmi-matrix-hub-sim:deploy-test')
hub = Container(unique('c4-proof-hub'), image)
port, control = free_port(), free_port()
try:
    docker('network', 'create', network)
    docker('volume', 'create', volume)
    docker('run', '--rm', '--user', 'root', '-v', f'{volume}:/data',
           '-v', f'{root / "tests/e2e/fixtures/data"}:/fixtures:ro', '--entrypoint', 'sh', image,
           '-c', 'cp /fixtures/*.json /data/; chown -R appuser:app /data')
    docker('run', '-d', '--name', sim.name, '--network', network, '--network-alias', 'c4-matrix',
           '-p', f'127.0.0.1:{control}:8444', '--no-healthcheck', sim.image,
           'python', '-m', 'tools.simulator', '--host', '0.0.0.0', '--https-port', '8443',
           '--telnet-port', '2323', '--control-port', '8444')
    wait_http(f'http://127.0.0.1:{control}/_sim/health', 60, sim.running)
    docker('run', '-d', '--name', hub.name, '--network', network, '-p', f'127.0.0.1:{port}:8080',
           '-v', f'{volume}:/data', '-e', 'MATRIX_HOST=c4-matrix', '-e', 'MATRIX_PORT=8443',
           '-e', 'OREI_TELNET_PORT=2323', '-e', 'UC_ENABLED=false',
           '-e', 'TRUST_PROXY_HEADERS=true', '-e', 'TRUSTED_PROXY_IPS=127.0.0.1,172.16.0.0/12,192.168.0.0/16', image)
    hub.wait_healthy_api(90)
    digest = docker('image', 'inspect', '-f', '{{.Id}}', image).stdout.strip()
    args = ['docker', 'run', '--rm', '--init', '--shm-size=1g', '-v', f'{root}:/work',
            '-v', 'hdmi-hub-ui-node-modules:/work/node_modules', '-v', 'hdmi-hub-ui-cache:/cache',
            '-w', '/work', 'mcr.microsoft.com/playwright:v1.63.0-noble', 'bash', '-c',
            'set -e; apt-get update -qq; apt-get install -y -qq --no-install-recommends git-lfs; '
            'git config --global core.filemode false; git config --global core.autocrlf true; '
            'git status --porcelain --untracked-files=no; '
            'test -z "$(git status --porcelain --untracked-files=no)"; '
            '/cache/venv/bin/python -m tools.validate run "$@"',
            'validate', '--target', 'sim', '--sim-control-url', f'http://host.docker.internal:{control}',
            '--hub-url', f'http://host.docker.internal:{port}', '--hub-image-digest', digest,
            '--client', 'api', '--client', 'browser', '--out', 'build/c4-image-validation']
    for fid in ('F-DOM-002', 'F-DOM-003', 'F-DOM-004', 'F-DOM-011', 'F-DOM-012', 'F-DOM-013',
                'F-DOM-014', 'F-DOM-016', 'F-DOM-020'):
        args += ['--feature', fid]
    args += sys.argv[1:]
    subprocess.run(args, check=True)
    (root / 'build/c4-image-stack.json').write_text(json.dumps({
        'image': image, 'digest': digest, 'hub': hub.name, 'simulator': sim.name,
        'procedure': args, 'scope': 'disposable simulator and fixture data; no real hardware',
    }, indent=2), encoding='utf-8')
finally:
    hub.remove()
    sim.remove()
    docker('volume', 'rm', volume, check=False)
    docker('network', 'rm', network, check=False)
