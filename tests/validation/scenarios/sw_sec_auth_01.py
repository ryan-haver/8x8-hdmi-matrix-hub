"""F-SEC-007 source campaigns: actual UI refusals, lockout and per-item controls.

The bounded browser sequence makes five real wrong-PIN attempts, observes the
locked click, then performs the measured action. Locked cases restart their
disposable hub because a locked item cannot authenticate cleanup. Existing
held-verifier pytest cases supply concurrent responsiveness and clocked expiry
proof; these scenarios do not claim that an after-only health read proves it.
"""

from tools.validate.model import (
    ClientState,
    CommandSent,
    Device,
    DeviceUnchanged,
    Hub,
    NoCommand,
    Response,
    Scenario,
    act,
)

from ._paths import HUB_CORE, PROFILES, SCENES, WEB_CORE, WEB_RUN

PIN = "1234"
WRONG_PIN = "9999"
PROFILE_ID = "sw_sec_auth_01_profile"
PEER_ID = "sw_sec_auth_01_peer"
SCENE_ID = "scene_goodnight01"
SCENE_PEER = "scene_kidslocked"
SCENE_STEPS = [{"type": "profile", "id": PROFILE_ID}]
ORIGINAL_STEPS = [
    {"type": "system_action", "id": "mute_all_audio"},
    {"type": "macro", "id": "macro_all_off"},
]
COVERS = (
    *HUB_CORE, *PROFILES, *SCENES, *WEB_CORE, *WEB_RUN,
    "src/password.py", "tools/validate/clients/browser.py", "tools/validate/clients/browser_driver.mjs",
    "tools/validate/clients/api.py", "tests/e2e/fixtures/data",
    "tools/validate/model.py", "tools/validate/runner.py",
    "tests/validation/scenarios/sw_sec_auth_01.py", "tests/validation/test_sw_sec_auth_01.py",
)


def request(method, path, body):
    return act("request", method=method, path=path, json=body)


def create_profile(profile_id, *, protected=True, source=6):
    return request("POST", "/api/profile", {
        "id": profile_id, "name": profile_id, "outputs": {"1": {"input": source}},
        **({"passcode": PIN} if protected else {}),
    })


def delete_profile(profile_id):
    return request("DELETE", f"/api/profile/{profile_id}", {"current_passcode": PIN})


SCENARIOS: list[Scenario] = []
for kind in ("profile", "scene"):
    is_profile = kind == "profile"
    item_id = PROFILE_ID if is_profile else SCENE_ID
    intent = "profile_recall" if is_profile else "scene_run"
    id_key = "profile_id" if is_profile else "scene_id"
    path = f"/api/profile/{item_id}" if is_profile else f"/api/v2/scenes/{item_id}"
    field = "data" if is_profile else "data.scene"
    setup = (create_profile(PROFILE_ID, protected=is_profile),)
    cleanup = (delete_profile(PROFILE_ID),)
    if not is_profile:
        setup += (request("PUT", path, {"passcode": PIN, "steps": SCENE_STEPS}),)
        cleanup = (request("PUT", path, {
            "remove_passcode": True, "current_passcode": PIN, "steps": ORIGINAL_STEPS,
        }), *cleanup)
    saved = (
        Hub(path, f"{field}.password_protected", equals=True),
        Hub(path, f"{field}.outputs" if is_profile else f"{field}.steps",
            equals={"1": {"input": 6, "enabled": True, "audio_mute": False}} if is_profile else SCENE_STEPS),
    )
    for allowed in (False, True):
        SCENARIOS.append(Scenario(
            id=f"sw_sec_auth_01.{kind}_{'allowed' if allowed else 'wrong_pin'}",
            title=f"Protected {kind}: {'correct PIN applies routing' if allowed else 'wrong PIN visibly refused'}",
            features=("F-SEC-007",), clients=("api", "browser"), targets=("sim",),
            kind="happy" if allowed else "failure", writes=("routing",) if allowed else (),
            action=act(intent, **{id_key: item_id}, passcode=PIN if allowed else WRONG_PIN),
            setup=setup, cleanup=cleanup, covers=COVERS,
            expect=(
                Response(status=200 if allowed else 403),
                Response(json={"success": allowed, **({"data": {"error": "invalid_passcode"}} if not allowed else {})},
                         clients=("api",)),
                *saved,
                *((Device("routing[0]", equals=6), CommandSent("video switch", {"source": [1, 6]}, count=1),
                   DeviceUnchanged(allow=("routing[0]", "outputs[0].source"))) if allowed else (
                    NoCommand(), DeviceUnchanged(),
                    ClientState("toast.error", equals="Invalid passcode", clients=("browser",), timeout=1),
                )),
            ),
            notes="Source API/browser proof only; PBKDF2 rendezvous, reset and expiry are separately tested; no image qualification.",
        ))
    for peer in (False, True):
        peer_id = PEER_ID if is_profile else SCENE_PEER
        SCENARIOS.append(Scenario(
            id=f"sw_sec_auth_01.{kind}_{'per_item' if peer else 'locked'}",
            title=f"{kind.title()} lockout: {'another protected item still executes' if peer else 'UI refuses further execution'}",
            features=("F-SEC-007",), clients=("browser",), targets=("sim",),
            kind="happy" if peer else "failure", writes=("routing",) if peer else (),
            action=act(intent, **{id_key: peer_id if peer else item_id},
                       **({"passcode": PIN} if peer else {}),
                       pin_lockout={"attempts": 5, "wrong_passcode": WRONG_PIN, "item_id": item_id}),
            setup=(*setup, *((create_profile(PEER_ID, source=7),) if is_profile and peer else ()),
                   *((request("PUT", f"/api/v2/scenes/{SCENE_PEER}", {"steps": SCENE_STEPS}),)
                     if peer and not is_profile else ())),
            restart_after=True, covers=COVERS,
            expect=(
                Response(status=200 if peer else 429),
                ClientState("pin.wrong_attempts", equals=5, timeout=1),
                ClientState("pin.lockout_visible", equals=True, timeout=1),
                ClientState("pin.retry_after_positive", equals=True, timeout=1),
                *saved,
                *((Device("routing[0]", equals=7 if is_profile else 6),
                   CommandSent("video switch", {"source": [1, 7 if is_profile else 6]}, count=1),
                   CommandSent("video switch", count=1),
                   DeviceUnchanged(allow=("routing[0]", "outputs[0].source"))) if peer else (
                    NoCommand(), DeviceUnchanged(),
                )),
            ),
            notes="Five wrong PINs and the lockout probe are real UI actions; the final action is a locked or independent item. "
                  "Runner-owned disposable hub restart discards the locked fixture; no attempted PIN cleanup during lockout.",
        ))
