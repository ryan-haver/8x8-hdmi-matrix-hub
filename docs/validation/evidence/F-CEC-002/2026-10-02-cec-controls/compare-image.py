from pathlib import Path
root=Path('/app'); checkout=Path('/checkout')
paths=list((root/'src').rglob('*.py'))+[p for p in (root/'web').rglob('*') if p.is_file()]
paths += [root/n for n in ('run.py','run_server.py','driver.json','requirements.txt','requirements-uc.txt')]
bad=[str(p) for p in paths if p.read_bytes().replace(b'\r\n',b'\n') != (checkout/p.relative_to(root)).read_bytes().replace(b'\r\n',b'\n')]
assert not bad,bad
print(f'Image matches checkout: {len(paths)} source/web/runtime/dependency files.')