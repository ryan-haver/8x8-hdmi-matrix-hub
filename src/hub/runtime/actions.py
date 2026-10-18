"""Initial action envelope seam; final surface parity belongs to R4."""


async def run_action_envelope(runtime, kind, action_id, *, passcode=None):
    result = await runtime.run_action(kind, action_id, passcode=passcode)
    return result.to_response_dict()
