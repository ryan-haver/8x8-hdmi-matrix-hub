# Model and agent inventory

Checked 2026-10-18 for the next runtime-completion phases. This inventory
separates a model from its agent harness and separates discovery from access.
It does not change accounts, install providers or start billable model probes.

**Policy:** no Claude/Anthropic models in implementation, review, helper roles,
categories or automatic fallbacks. The historical six-model roster is retired
for future work. Unknown-provider aliases are not eligible just because their
display names do not contain "Claude".

## Evidence and access levels

- **Project-proven:** this project previously launched the agent/model and
  accepted tested work. This does not guarantee today's quota.
- **Catalog/configured:** a local catalog or settings file names it; a new
  launch still needs effective-model and access verification.
- **Catalog-only:** a provider advertises it, without verified account access,
  budget, tool compatibility or an accepted project run. Do not assign critical
  work until qualified.
- **Unavailable:** no usable provider is authenticated in the checked harness.

Read-only local discovery used Orca 1.4.229's version-matched guides, agent launch
help and command schema; the visible Codex model cache (fetched
`2026-10-18T20:55:59Z`); `opencode models`; OpenCode's primary/helper model
settings; and `pi --offline --no-extensions --no-mcp --list-models`.
Catalog results can change. Neither CLI installation nor a catalog entry proves
credentials, subscription entitlement, remaining quota or successful tool use.

## Preferred models and their role

The capability descriptions below come from the linked providers. Assignments
are our engineering judgment for this repository, not cross-provider benchmark
claims or guaranteed speed/cost measurements.

| Model | Harness / exact identifier | Access evidence | Best planned use / limitation |
| --- | --- | --- | --- |
| Sol 6.1 | Orca `codex`, `gpt-6.1-sol`, high | Project-proven; visible Codex catalog | Coordinator and core implementation. Default for consequential coding, with task-specific tests. |
| Astra | Orca `codex`, `gpt-6-astra`, high | Project-proven after the audit: R0 contract accepted as `0125ad2` | Difficult architecture and independent final review; use a fresh reviewer session. |
| Luna | Orca `codex`, `gpt-6-luna`, medium | Effective live dispatch confirmed; R7 guide preparation accepted after 375 independent checks | Bounded documentation, evidence indexing and focused follow-ups. Escalate architectural ambiguity. |
| Gemini 4 Argon | Orca `antigravity`, `gemini-4-argon`, high | Project-proven; also advertised in OpenCode catalog | UC integration and complex protocol/lifecycle reasoning; independent provider perspective. |
| Gemini 3.8 Flash | Orca `antigravity`, `gemini-3.8-flash-high` | Project-proven Orca alias; API ID is `gemini-3.8-flash` | Focused integration/client implementation and tests with clear contracts. |
| MiniMax M3 | Orca `opencode`; configured `minimax-coding-plan/MiniMax-M3` | Project-proven; current primary config; prior run exhausted quota | Bounded persistence wiring, conditional on refreshed quota and observed model. |
| MiniMax M3.1 Flash Preview | OpenCode catalog/helper config: `minimax-coding-plan/MiniMax-M3.1-Flash-Preview` | Catalog/configured; previous worktree requested M3.1 but actually ran M3 | Optional bounded client/visual work after explicit selection and proof. Never count an M3 launch as M3.1. |
| DeepSeek V4 Pro / Flash | OpenCode catalog: `deepseek/deepseek-v4-pro`, `deepseek/deepseek-flash` | Catalog/configured provider; access not probed | Candidate extra reviewer or bounded coding lane after qualification. Existing helper `deepseek/deepseek-reasoner` does not match these catalog IDs and needs reconciliation. |

[OpenAI's selection guidance](https://developers.openai.com/api/docs/guides/model-selection)
positions Astra for demanding/ambiguous work, Sol for complex tasks balancing
quality and cost, and Luna for scoped frequent work. The
[Sol 6.1 model page](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
describes complex coding and lower-cost near-Astra performance; this motivates
our Sol-first policy, not a claim about this account's billing.

Google describes [Argon](https://ai.google.dev/gemini-api/docs/models/gemini-4-argon)
as its flagship reasoning model for complex engineering and
[Flash 3.8](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash)
as an efficient model for sustained engineering/agent tasks. Both document tool
calling and high thinking. The API model ID and Orca's high-thinking alias
must not be interchanged without checking the adapter.

MiniMax describes [M3](https://www.minimax.io/blog/minimax-m3) as a coding model
with long context and multimodal inputs. Its
[M3.1 preview guide](https://agent.minimax.io/tools/m3-1-flash-preview)
adds coding/visual workflows and configurable reasoning while explicitly asking
users to confirm selected model and access. Those are provider descriptions;
the preview label is not evidence that it is better for every coding task.

[DeepSeek's model documentation](https://api-docs.deepseek.com/quick_start/pricing/)
is the reference for its current model names. Local helper labels and provider
catalog names must agree before dispatch; a stale alias is not an access check.

## Other models at our disposal: distinguish catalog from usable capacity

The visible Codex cache also lists `gpt-6-sol`, `gpt-5.6-sol`,
`gpt-5.6-terra` and `gpt-5.6-luna`. Keep these as explicit compatibility
fallbacks if needed, not additional mandatory roster slots. Hidden/internal
review/reserve entries are not user-selected worker assignments.

The OpenCode MiniMax coding-plan catalog also lists M2, M2.1, M2.5,
M2.5-highspeed, M2.7 and M2.7-highspeed. Prefer the configured M3 for this work
unless a measured constraint justifies a different qualified model.

OpenCode advertises models from OpenAI, Google, DeepSeek, MiniMax, GLM, Kimi,
Grok, Qwen, Mistral, Muse, Nemotron, LongCat and MiMo, plus opaque/free aliases.
The exact name-filtered non-Anthropic catalog is retained in
[OPENCODE_MODEL_CATALOG.txt](OPENCODE_MODEL_CATALOG.txt). This is **79 catalog
entries**, including duplicates across provider routes; it is not 79 verified
usable models. Names alone do not establish the provider behind opaque aliases.
These additional families stay catalog-only until access, costs, tool use,
model routing and representative test results are known. Do not spend credits
or add credentials just to expand the roster for this phase.

Pi is installed but its model listing returned **"No models available"** and
asked for login. It is unavailable for assignments until authenticated. Gemini
CLI is installed, but its account/model access was not probed; use the
project-proven Antigravity route first. CLI presence is not launch readiness.
The managed OpenCode account list is empty; the global OpenCode configuration
and its previous project runs are separate evidence. No account was selected
or changed in this audit. Other Orca-supported agent IDs are not evidence that
their executables, credentials or model selection are ready here.

## Execution since the audit

Execution after the initial audit confirmed Sol, Astra, Argon and Flash through
real Orca dispatches. Sol completed core, installed-entry, persistence and
cleanup corrections; Argon's UC correction and Flash's Flic replay work were
accepted after coordinator validation. Some candidates needed follow-up fixes,
so these outcomes support task-specific assignments and review gates, rather
than a general ranking of model quality.

MiniMax M3's persistence checkpoint was preserved after its full-scope failure;
Sol completed that track. M3.1 and DeepSeek remain conditional routes. Luna's
bounded guide assignment has confirmed requested/effective `gpt-6-luna` medium;
guide preparation `d956046` was accepted after 375 independent checks and merged
as `5608407`. Luna's final guides/index subsequently passed 413 independent
documentation tests and 214 local links and were merged at `b84ec72`. Catalog entries are
still distinct from proven current capacity. The no-Anthropic policy applies to
all retries, reviews and helpers.

The current corrective assignments remain scoped by demonstrated need: Sol
completed R5C's Linux deployment tests; Flash completed R6C's HA validation error
classification; Argon's R3E UI ordering correction is accepted; Sol completed
R1F's explicit-refresh CEC enable-cache correction; Luna owns the final
guides/index. Fresh Astra completed R8 and found two high defects in actual
source and images; fresh Sol 6.1 high owners now handle disjoint R2D persistence
and R1G rollback/reconnect corrections, now merged after validation. Fresh Astra
R8B passes their original six source/image cases but finds the remaining cleanup
deadline boundary, corrected by fresh Sol 6.1 high R1H. Fresh Astra R8C passes
all eight known source/image cases but reproduces original-state restoration
being skipped when candidate cleanup is interrupted; fresh Sol 6.1 high R1I owns
the complete restoration correction. Independent verification and fresh complete
candidate evidence remain required. A
separate Sol session completed a read-only R3E source-contract review without
editing tracked files. Its real-payload JavaScript probe demonstrates a startup
ordering race, while attribution to the first CI failure remains bounded.

Antigravity launch receipts and native UI display the requested Argon high
alias. Earlier backend self-reporting conflicted with that label; the underlying
backend identity remains unverified. Do not present the alias as independent
proof of a particular backend version. The native credit footer alone is also
not proof that an active worker failed or exited.

## Launch rules

Use these as recipes when executing the task plan; none
were run as launches during this planning audit. Resolve the integration base
and place the full ownership/acceptance brief in `$p` first.

```powershell
orca worktree create --name <name> --base-branch wp-runtime-completion --agent codex --model gpt-6.1-sol --effort high --prompt $p --json
orca worktree create --name <name> --base-branch wp-runtime-completion --agent codex --model gpt-6-astra --effort high --prompt $p --json
orca worktree create --name <name> --base-branch wp-runtime-completion --agent codex --model gpt-6-luna --effort medium --prompt $p --json
orca worktree create --name <name> --base-branch wp-runtime-completion --agent antigravity --model gemini-4-argon --effort high --prompt $p --json
orca worktree create --name <name> --base-branch wp-runtime-completion --agent antigravity --model gemini-3.8-flash-high --prompt $p --json
orca worktree create --name <name> --base-branch wp-runtime-completion --agent opencode --prompt $p --json
```

The last recipe means **the configured primary model**, currently M3. Prior
Orca OpenCode launches rejected `--model` with `capability_unsupported`; generic
launch help advertising that flag does not prove every adapter supports it.
The native `opencode run --help` now advertises `--model provider/model#variant`,
but that does not establish Orca's adapter support or effective helper routing.
Before assigning M3.1/DeepSeek, establish an explicit supported per-worktree
selection mechanism and observe the actual provider/model. Do not change global
preferences to make a conditional assignment appear ready.

OpenCode currently routes primary/deep tasks to M3, some helpers to M3.1 Flash
Preview, and several reasoning roles to `deepseek/deepseek-reasoner`. Audit
the effective full helper/category/fallback configuration, including defaults
provided by plugins. Do not assume the primary model controls nested workers.
Disable or pin unverified routes before dispatch; if that cannot be established,
use a confirmed Codex/Google alternative for the task instead.

For every dispatch: verify the effective provider/model and effort from the
session, confirm tools work inside its own worktree, record quota failures
honestly, and preserve the authoritative Orca receipt/handle. Never use an
Anthropic fallback after a quota or model-selection failure. Use a higher
reasoning level only for a concrete unresolved problem; no automatic `ultra`
delegation or unsupervised helper fan-out bypassing the roster.
Before creating the worktree, also inspect setup hooks and default agent tabs
so an otherwise valid launch does not start an excluded agent as a side effect.
