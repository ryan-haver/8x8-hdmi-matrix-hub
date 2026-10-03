# Reproduce deployment checks

Use the source commit in `runner.json` and the image in `image.json`. Build the
image from that checkout, or use the retained image after checking all 176
application files with `compare-image.py`. The suite never targets real hardware.

Copy `record.py` and `compare-image.py` into the ignored `build` directory as
`deploy-refresh-record.py` and `refresh-compare-image.py`. The wrapper keeps the
repository's deployment assertions unchanged. It maps the temporary Compose
bind directory from the runner's `/work` mount to Docker Desktop's daemon-side
`/run/desktop/mnt/host/c/scripts/unfoldedcircle-orei-hdmi-matrix-integration/`
path. Adjust that mapping for another checkout. Enable Docker Desktop host
networking for the host variant; check port 9095 is unused before running.

The runner uses `mcr.microsoft.com/playwright:v1.63.0-noble`, the Docker socket,
the repository mounted read-write at `/work`, and `hdmi-hub-ui-cache` at `/cache`.
Its `/cache/venv` needs this repository's dependencies, pytest, jsonschema and
cryptography. Run with `--network host`, `--init`, working directory `/work`,
and a unique task container name. Install Git LFS in the runner and set Git's
Linux mount settings: `core.filemode=false`, `core.autocrlf=true`,
`core.trustctime=false`, `core.checkStat=minimal`. Use
`GIT_CONFIG_PARAMETERS="'core.hooksPath=.githooks'"` for Git calls from Python.
Require a clean tracked checkout before recording.

Stage the Docker CLI and Compose plugin from a disposable `docker:29-cli`
container (remove it after copying): `/usr/local/bin/docker` and
`/usr/local/libexec/docker/cli-plugins/docker-compose`. Mount/copy the CLI to
`/work/build/refresh-bin/docker` and make it executable. Copy the executable
Compose plugin into `/tmp/deploy-docker-config/cli-plugins/docker-compose` in
the runner. Use `DOCKER_CONFIG=/tmp/deploy-docker-config` and prepend
`/work/build/refresh-bin` to PATH.

Set `HUB_IMAGE=hdmi-matrix-hub:wp-simulator-evidence-refresh` and
`DEPLOY_EVIDENCE_DIR=docs/validation/evidence`, then run:

```sh
/cache/venv/bin/python build/deploy-refresh-record.py
```

This calls `pytest tests/deploy -m docker -v --tb=short -p no:cacheprovider`
with disposable temporary files under `build/deploy-refresh-tmp`. The
simulator fixture builds its image from the hub image and simulator source.
Tests create uniquely named projects, networks, volumes and containers, and
remove them in fixture teardown. Preserve failures as failures. Only the
Remote connection check in core mode should skip on this setup.

Validate the records against `docs/validation/evidence.schema.json`, their
source identity, expected 25 pass/one n/a checks, exact two image digests and
restored simulator routing. Link the three records to their seven features.
Regenerate the ledger and run `tools.validate check` with the adjacent summary
and expected clients `api,uc`; a new run needs its own summary. Commit the
records and handoff through `.githooks/pre-commit`. Remove the task runner after
verification. The Compose record has no image digest because its existing
recorder does not set one; retain the image override and runner identity rather
than attributing an unmeasured value to that field.
