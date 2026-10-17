/**
 * OREI Matrix Control - running profiles, scenes, and protected actions from the UI
 *
 * One path for every button that recalls a profile or runs a scene (Settings
 * drawer, dashboard cards, Profiles tab) and for two-level PIN auth prompts:
 * - UI-01: when the hub answers 403 "passcode_required", ask for the passcode
 *   and retry with it; a wrong passcode ("invalid_passcode") is reported.
 * - WP-F1: when the hub answers 401/403 "admin_pin_required" or "control_pin_required",
 *   prompt via confirmDialog.promptPasscode(...), call
 *   api.unlockAuth({ pin, level, remember_device: level === 'control' }),
 *   and retry the original action on success.
 * - VAL-11: the hub answers 200 (all applied), 207 with success:false (only
 *   part applied) or an error status (nothing applied). A partial run is
 *   reported as a warning that says what failed, never as success or silence.
 */

/**
 * Default passcode/PIN prompt implementation backed by window.prompt so both
 * interactive users and headless browser dialog handlers work seamlessly.
 * @param {string|Object} [options]
 * @returns {Promise<string|null>}
 */
async function defaultPromptPasscode(options = {}) {
    const opts = typeof options === 'string' ? { message: options } : (options || {});
    const level = opts.level === 'control' ? 'control' : 'admin';
    const fallbackMsg =
        level === 'control'
            ? 'Control PIN required. Enter Control PIN:'
            : 'Admin PIN required. Enter Admin PIN:';
    const promptText = opts.message || opts.title || fallbackMsg;
    if (typeof window === 'undefined' || typeof window.prompt !== 'function') {
        return null;
    }
    const raw = window.prompt(promptText);
    if (raw === null || raw === undefined) return null;
    const trimmed = String(raw).trim();
    return trimmed ? trimmed : null;
}

/**
 * Ensure confirmDialog.promptPasscode is registered on global dialog helpers.
 */
function ensureConfirmDialogPromptPasscode() {
    if (typeof window === 'undefined') return;
    if (window.ConfirmDialog && typeof window.ConfirmDialog.promptPasscode !== 'function') {
        window.ConfirmDialog.promptPasscode = defaultPromptPasscode;
    }
    if (!window.confirmDialog) {
        window.confirmDialog = window.ConfirmDialog || { promptPasscode: defaultPromptPasscode };
    } else if (typeof window.confirmDialog.promptPasscode !== 'function') {
        window.confirmDialog.promptPasscode = defaultPromptPasscode;
    }
}

/**
 * Prompt the user for a passcode or PIN via confirmDialog.promptPasscode(...).
 * @param {string|Object} [options]
 * @returns {Promise<string|null>}
 */
async function promptPasscode(options = {}) {
    ensureConfirmDialogPromptPasscode();
    if (typeof window !== 'undefined') {
        if (typeof window.confirmDialog?.promptPasscode === 'function') {
            return window.confirmDialog.promptPasscode(options);
        }
        if (typeof window.ConfirmDialog?.promptPasscode === 'function') {
            return window.ConfirmDialog.promptPasscode(options);
        }
    }
    return defaultPromptPasscode(options);
}

/**
 * Check whether an error is an Admin or Control PIN requirement.
 * @param {Error} err
 * @returns {boolean}
 */
function isAuthPinError(err) {
    if (!err) return false;
    if (err.code === 'admin_pin_required' || err.code === 'control_pin_required') {
        return true;
    }
    return (err.status === 401 || err.status === 403) && (err.level === 'admin' || err.level === 'control');
}

/**
 * Prompt for Admin PIN or Control PIN and unlock the session via api.unlockAuth.
 * @param {Object} [errOrOptions]
 * @returns {Promise<{status: 'ok'|'cancelled'|'failed', level?: string, error?: Error}>}
 */
async function promptAndUnlock(errOrOptions = {}) {
    const level =
        errOrOptions?.level ||
        (errOrOptions?.code === 'control_pin_required' ? 'control' : 'admin');
    const title = level === 'control' ? 'Control PIN Required' : 'Admin PIN Required';
    const message =
        errOrOptions?.promptMessage ||
        (level === 'control'
            ? 'Control PIN required. Enter Control PIN:'
            : 'Admin PIN required. Enter Admin PIN:');

    const pin = await promptPasscode({ title, message, level });
    if (!pin) {
        return { status: 'cancelled', level };
    }

    try {
        await window.api.unlockAuth({
            pin,
            level,
            remember_device: level === 'control',
        });
        if (typeof window !== 'undefined' && window.generalDrawer?.isOpen && typeof window.generalDrawer.loadAuthStatus === 'function') {
            window.generalDrawer.loadAuthStatus().catch(() => {});
        }
        return { status: 'ok', level };
    } catch (unlockErr) {
        if (typeof toast !== 'undefined' && toast?.error) {
            if (unlockErr?.status === 401 || unlockErr?.code === 'invalid_pin') {
                toast.error('Incorrect PIN');
            } else {
                toast.error(`Unlock failed: ${unlockErr.message}`);
            }
        }
        return { status: 'failed', level, error: unlockErr };
    }
}

/**
 * Run an arbitrary async action, automatically prompting to unlock on
 * admin_pin_required or control_pin_required and retrying once on success.
 * @param {Function} actionFn
 * @returns {Promise<*>}
 */
async function runWithAuth(actionFn) {
    try {
        return await actionFn();
    } catch (err) {
        if (!isAuthPinError(err) || err._authPromptHandled) {
            throw err;
        }
        const outcome = await promptAndUnlock(err);
        if (outcome.status !== 'ok') {
            throw outcome.error || err;
        }
        return actionFn();
    }
}

/**
 * Human-readable summary of a partial (HTTP 207) result.
 * @param {'profile'|'scene'} kind
 * @param {Object} data - the `data` of the hub's answer
 */
function describePartialRun(kind, data) {
    if (kind === 'scene') {
        const total = data?.total_steps ?? (data?.step_results || []).length;
        const done = data?.steps_completed ?? (data?.step_results || []).filter((s) => s.success).length;
        return `${done} of ${total} steps succeeded`;
    }
    const errors = Array.isArray(data?.errors) ? data.errors.filter(Boolean) : [];
    if (errors.length) return errors.join('; ');
    const failed = data?.failed_outputs || [];
    return failed.length ? `output ${failed.join(', ')} not applied` : 'some settings were not applied';
}

/**
 * Recall a profile or run a scene, handling PIN/passcode prompts and reporting
 * the outcome with a toast.
 * @param {'profile'|'scene'} kind
 * @param {string} id
 * @param {Object} [options]
 * @param {string} [options.name] - display name for messages
 * @param {string} [options.successMessage] - toast on full success
 * @returns {Promise<{status: 'ok'|'partial'|'failed'|'cancelled', result?: Object, error?: Error}>}
 */
async function runProfileOrScene(kind, id, { name, successMessage } = {}) {
    const label = name || (kind === 'scene' ? 'Scene' : 'Profile');
    const call = (passcode) =>
        kind === 'scene' ? window.api.executeScene(id, { passcode }) : window.api.recallProfile(id, { passcode });
    const isPasscodeError = (err, code) => err?.status === 403 && err?.code === code;

    let result;
    try {
        result = await call();
    } catch (err) {
        if (isAuthPinError(err)) {
            if (err._authPromptHandled) {
                if (err._authOutcome?.status === 'cancelled') {
                    return { status: 'cancelled' };
                }
                return { status: 'failed', error: err._authOutcome?.error || err };
            }
            const unlockOutcome = await promptAndUnlock(err);
            if (unlockOutcome.status === 'cancelled') {
                return { status: 'cancelled' };
            }
            if (unlockOutcome.status !== 'ok') {
                return { status: 'failed', error: unlockOutcome.error || err };
            }
            try {
                result = await call();
            } catch (retryErr) {
                if (isPasscodeError(retryErr, 'passcode_required')) {
                    const passcode = await promptPasscode({
                        title: 'Passcode Required',
                        message: `"${label}" is passcode protected. Enter passcode:`,
                    });
                    if (!passcode) return { status: 'cancelled' };
                    try {
                        result = await call(passcode);
                    } catch (err2) {
                        if (isPasscodeError(err2, 'invalid_passcode')) toast.error('Invalid passcode');
                        else toast.error(`Failed to run "${label}": ${err2.message}`);
                        return { status: 'failed', error: err2 };
                    }
                } else {
                    toast.error(`Failed to run "${label}": ${retryErr.message}`);
                    return { status: 'failed', error: retryErr };
                }
            }
        } else if (isPasscodeError(err, 'passcode_required')) {
            const passcode = await promptPasscode({
                title: 'Passcode Required',
                message: `"${label}" is passcode protected. Enter passcode:`,
            });
            if (!passcode) return { status: 'cancelled' };
            try {
                result = await call(passcode);
            } catch (err2) {
                if (isPasscodeError(err2, 'invalid_passcode')) toast.error('Invalid passcode');
                else toast.error(`Failed to run "${label}": ${err2.message}`);
                return { status: 'failed', error: err2 };
            }
        } else {
            toast.error(`Failed to run "${label}": ${err.message}`);
            return { status: 'failed', error: err };
        }
    }

    // UI-45: the recalled profile becomes the active one, so the CEC tray uses its CEC targets.
    // The profile's routing goes with it, so the routing_change events the
    // recall itself causes (WebSocket, WP-C2) do not end the active profile.
    const activate = async () => {
        if (kind !== 'profile') return;
        const profile = (window.state?.profiles || []).find((p) => p.id === id) || { id, name: label };
        let routing = null;
        try {
            const full = await window.api.getProfile(id);
            const outputs = (full?.data || full)?.outputs || {};
            routing = Object.fromEntries(Object.entries(outputs).map(([o, cfg]) => [String(o), Number(cfg.input)]));
        } catch (err) {
            console.warn('Could not read the profile routing:', err);
        }
        window.state?.setActiveProfile({ ...profile, routing });
    };
    if (result?.success) {
        toast.success(successMessage || `"${label}" ${kind === 'scene' ? 'executed' : 'recalled'}`);
        await activate();
        return { status: 'ok', result };
    }
    // A 2xx answer with success:false is a partial run (HTTP 207).
    const what = kind === 'scene' ? 'ran partly' : 'applied partly';
    toast.warning(`"${label}" ${what}: ${describePartialRun(kind, result?.data)}`, 6000);
    await activate();
    return { status: 'partial', result };
}

if (typeof window !== 'undefined') {
    ensureConfirmDialogPromptPasscode();
    if (typeof document !== 'undefined') {
        document.addEventListener('DOMContentLoaded', () => ensureConfirmDialogPromptPasscode());
    }
    window.RunAction = {
        runProfileOrScene,
        describePartialRun,
        promptPasscode,
        promptAndUnlock,
        runWithAuth,
    };
}
