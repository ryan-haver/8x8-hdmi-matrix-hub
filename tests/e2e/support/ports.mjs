// Fixed ports for the Playwright stack (distinct from dev_stack.py's defaults
// 8080/8443/2323/8444 so a running dev stack does not collide with a test run).
export const PORTS = Object.freeze({
  api: Number(process.env.E2E_API_PORT ?? 18080),
  https: Number(process.env.E2E_HTTPS_PORT ?? 18443),
  telnet: Number(process.env.E2E_TELNET_PORT ?? 12323),
  control: Number(process.env.E2E_CONTROL_PORT ?? 18444),
});

export const HUB_URL = `http://127.0.0.1:${PORTS.api}`;
export const SIM_URL = `http://127.0.0.1:${PORTS.control}`;
