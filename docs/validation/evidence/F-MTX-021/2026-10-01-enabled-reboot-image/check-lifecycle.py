import json
from pathlib import Path
meta = json.loads(Path('build/reboot-image-stack.json').read_text(encoding='utf-8-sig'))
rows = []
for p in Path('docs/validation/evidence').rglob('*.json'):
    d = json.loads(p.read_text(encoding='utf-8-sig'))
    if not isinstance(d, dict):
        continue
    if d.get('commit', {}).get('sha') != meta['source_commit'] or not d.get('scenario', '').startswith('reboot.'):
        continue
    assert d['result'] == 'pass' and d['commit']['dirty'] is False
    assert d['environment']['hub']['image_digest'] == meta['digest']
    logs = d['observations']['device_log']
    boots = [e for e in logs if e.get('channel') == 'sim' and e.get('command', '').startswith('reboot (')]
    attempts = [e for e in logs if e.get('channel') in ('http', 'telnet') and e.get('command') == 'reboot']
    assert len(boots) == len(attempts) == 1, (p, boots, attempts)
    assert attempts[0]['channel'] == 'telnet'
    events = d['observations']['ws_events']
    down = next(e for e in events if e['event'] == 'matrix_connection' and e['data']['connected'] is False and e['t_ms'] >= 0)
    up = next(e for e in events if e['event'] == 'matrix_connection' and e['data']['connected'] is True
              and e['data']['state'] == 'connected' and e['t_ms'] > down['t_ms'])
    assert d['observations']['state_diff'] == []
    rows.append({'record': p.as_posix(), 'boots': len(boots), 'attempts': len(attempts),
                 'disconnected_ms': down['t_ms'], 'recovered_ms': up['t_ms']})
assert len(rows) == 4, len(rows)
Path('build/reboot-image/lifecycle-check.json').write_text(json.dumps({'source_commit': meta['source_commit'],
    'image_digest': meta['digest'], 'result': 'pass', 'records': rows}, indent=2))
print('All four enabled-reboot records prove one actual simulator reboot and ordered disconnect/recovery.')