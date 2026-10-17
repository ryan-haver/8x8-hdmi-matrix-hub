"""
``SECURITY.md`` exists and documents the security baseline
(docs/REMEDIATION_PLAN.md §4.3 Phase 3, "Add SECURITY.md").

The policy is only useful if it keeps naming the variables and endpoints a user
has to set or firewall, so the checks below fail when the document drifts: a
renamed variable or a removed section breaks the build instead of silently
leaving the threat model, the access model or the disclosure instructions
undocumented.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SECURITY_MD = REPO_ROOT / "SECURITY.md"


@pytest.fixture(scope="module")
def policy() -> str:
    """The text of SECURITY.md, read once for the whole module."""
    assert SECURITY_MD.is_file(), "SECURITY.md is missing from the repository root"
    text = SECURITY_MD.read_text(encoding="utf-8")
    assert text.strip(), "SECURITY.md is empty"
    return text


def test_security_md_exists_and_is_not_empty(policy: str) -> None:
    """The policy file is present at the repository root and has content."""
    assert len(policy.strip()) > 500, "SECURITY.md is a stub; the policy must be written out"
    assert policy.lstrip().startswith("#"), "SECURITY.md must start with a Markdown heading"


@pytest.mark.parametrize(
    "variable",
    [
        "ADMIN_PIN",
        "ADMIN_PIN_RESET",
        "CONTROL_PIN",
        "ALLOWED_HOSTS",
        "CORS_ALLOWED_ORIGINS",
        "TRUSTED_PROXY_IPS",
        "UC_AUTH_TOKEN",
        "OREI_TLS_FINGERPRINT",
        # Always-on protections named in the plan: TLS, proxy trust, WS cap
        "OREI_VERIFY_SSL",
        "TRUST_PROXY_HEADERS",
        "MAX_WS_CLIENTS",
    ],
)
def test_documented_env_vars(policy: str, variable: str) -> None:
    """Every security-relevant environment variable is documented."""
    assert variable in policy, f"SECURITY.md does not document {variable}"


@pytest.mark.parametrize("token", ["8080", "9095"])
def test_documented_ports(policy: str, token: str) -> None:
    """Both listening ports are named, so readers know what to keep off the internet."""
    assert token in policy, f"SECURITY.md does not mention port {token}"


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/auth/unlock",
        "/api/auth/devices",
        "/api/auth/api-keys",
        "/api/settings/matrix-host",
    ],
)
def test_documented_endpoints(policy: str, endpoint: str) -> None:
    """The endpoints behind the access model and the SSRF guard are named."""
    assert endpoint in policy, f"SECURITY.md does not mention {endpoint}"


@pytest.mark.parametrize(
    "detail",
    [
        "orei_session",
        "orei_device_token",
        "X-API-Key",
        "X-Passcode",
        "current_passcode",
        "PBKDF2-HMAC-SHA256",
        "HttpOnly",
        "SameSite=Strict",
        "WireGuard",
        "Tailscale",
        "reverse proxy",
    ],
)
def test_documented_mechanisms(policy: str, detail: str) -> None:
    """The concrete protections are named, not just described in prose."""
    assert detail in policy, f"SECURITY.md does not mention {detail}"


@pytest.mark.parametrize(
    "section",
    [
        "Threat model",
        "Two-level access model",
        "PIN recovery",
        "Per-item profile and scene PINs",
        "Always-on protections",
        "Unfolded Circle Remote 3",
        "Reporting a vulnerability",
    ],
)
def test_required_sections(policy: str, section: str) -> None:
    """Every required section of the policy is present as a heading."""
    headings = [line for line in policy.splitlines() if line.startswith("#")]
    assert any(section in heading for heading in headings), f"SECURITY.md has no '{section}' section"


def test_internet_exposure_warning_is_explicit(policy: str) -> None:
    """The plan's core instruction: never expose 8080 (or 9095) to the internet."""
    lowered = policy.lower()
    assert "do not expose port 8080" in lowered, "SECURITY.md must tell users not to expose port 8080"
    assert "vpn" in lowered, "SECURITY.md must recommend a VPN"
    assert "https" in lowered, "SECURITY.md must recommend HTTPS at the proxy"


def test_vulnerability_reporting_is_private(policy: str) -> None:
    """Disclosure goes through GitHub Security Advisories, not a public issue."""
    assert "security/advisories" in policy, "SECURITY.md must link the GitHub Security Advisories form"
    assert "public issue" in policy.lower(), "SECURITY.md must say reports are not public issues"
