# Explicit conditional contract probes

These probes document stronger guarantees outside the supported product's
acceptance contract. Invoke them explicitly; they are not skipped, expected
failures, or passing evidence in the default product suite.

## R8D: disconnect fails before its real body runs

The [unchanged probe](r8d_conditional_disconnect_probe.py) replaces the public
disconnect implementation before Orei can apply its synchronous intentional-close
fence. An existing reconnect supervisor can then continue while composition keeps
its command fence. No natural Orei in-body bypass was demonstrated. The actual
in-body error and late-close controls pass in
[the supported review tests](../../../tests/test_runtime_review_r8d.py).

From the repository root with its test dependencies:

```powershell
python -m pytest docs/validation/reproductions/r8d_conditional_disconnect_probe.py -p tests.conftest -k original_public_disconnect -q
```

The reviewed result is **one failure, one pass, one deselection**, exit 1. The
unselected late-close control also passes when run. The probe's SHA-256 is
`defca6b53cd9f03e2c00cd26eb00d6c733e6e68fd93294ab455e59debb077df4`;
scoped Git attributes preserve those original bytes. Its failing oracle remains
unchanged. See [the R8D report](../RUNTIME_REVIEW_RESTORATION.md) for source/image
identities, actual wire observations, prior attempts and the coordinator's
explicit scope decision. This is a documented alternate-client extension limit,
not a passing universal disconnect guarantee.
