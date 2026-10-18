# RC1 validation summaries

These summary data and deployment records come from the actual candidate runs;
the original commit, tracked-change state, outcomes and timestamps are retained.

| Summary | Original artifact root | Scope |
| --- | --- | --- |
| [source.json](source.json) | `build/rc-validation/` | API, browser and scripted Remote against source processes; Flic replay is unimplemented |
| [home-assistant.json](home-assistant.json) | `build/rc-validation-ha/` | Real Home Assistant container using the component against a source-process hub |
| [shipped-image.json](shipped-image.json) | `build/rc-image-validation/` | Selected domain flows through the built hub image |
| [swagger.json](swagger.json) | `build/rc-swagger-review/` | All 177 documentation routes online/offline through the shipped image; synthetic PIN storage check |
| [regression-gate.log](regression-gate.log) | `build/rc-release-gate/` | Successful combined gate, zero known/unexplained failures |
| [deployment/](deployment/) | `build/rc-validation-deploy/` | Core/UC images and compose deployment tests |

`record` paths inside a summary are relative to its original artifact root,
not this summary directory. Full request/state evidence, screenshots and logs
remain there; CI also uploads validation and deployment artifacts. Reproduce
runs with `python -m tools.validate run` and the procedures in the validation
guide. The selected image stack procedure is retained locally in
`build/rc-image-stack.json`.

Source-process client runs alone do not establish the plan's shipped-image
condition. Consult [the report](../../VALIDATION_REPORT.md) for that distinction,
proof levels and the hardware/soak gates still outstanding.
