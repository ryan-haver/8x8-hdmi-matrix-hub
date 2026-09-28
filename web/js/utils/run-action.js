/**
 * OREI Matrix Control - running profiles and scenes from the UI
 *
 * One path for every button that recalls a profile or runs a scene (Settings
 * drawer, dashboard cards, Profiles tab):
 * - UI-01: when the hub answers 403 "passcode_required", ask for the passcode
 *   and retry with it; a wrong passcode ("invalid_passcode") is reported.
 * - VAL-11: the hub answers 200 (all applied), 207 with success:false (only
 *   part applied) or an error status (nothing applied). A partial run is
 *   reported as a warning that says what failed, never as success or silence.
 */

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
 * Recall a profile or run a scene, handling the passcode prompt and reporting
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
        if (!isPasscodeError(err, 'passcode_required')) {
            toast.error(`Failed to run "${label}": ${err.message}`);
            return { status: 'failed', error: err };
        }
        const passcode = window.prompt(`"${label}" is passcode protected. Enter passcode:`);
        if (!passcode) return { status: 'cancelled' };
        try {
            result = await call(passcode);
        } catch (err2) {
            if (isPasscodeError(err2, 'invalid_passcode')) toast.error('Invalid passcode');
            else toast.error(`Failed to run "${label}": ${err2.message}`);
            return { status: 'failed', error: err2 };
        }
    }

    if (result?.success) {
        toast.success(successMessage || `"${label}" ${kind === 'scene' ? 'executed' : 'recalled'}`);
        return { status: 'ok', result };
    }
    // A 2xx answer with success:false is a partial run (HTTP 207).
    const what = kind === 'scene' ? 'ran partly' : 'applied partly';
    toast.warning(`"${label}" ${what}: ${describePartialRun(kind, result?.data)}`, 6000);
    return { status: 'partial', result };
}

if (typeof window !== 'undefined') {
    window.RunAction = { runProfileOrScene, describePartialRun };
}
