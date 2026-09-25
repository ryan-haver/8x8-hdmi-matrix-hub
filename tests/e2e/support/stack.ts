// Helpers for the simulator control API (/_sim/*) and the hub REST API.
// See tools/simulator/README.md for the control API.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, type APIRequestContext, request as pwRequest } from '@playwright/test';
import { HUB_URL, SIM_URL } from './ports.mjs';

const SEED_STATE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..', 'tools', 'simulator', 'states', 'default.json');

export type SimState = {
  inputs: Array<{ name: string; signal: number; cable: number; edid: number; cec_enabled: number }>;
  outputs: Array<{ name: string; source: number; connected: number; [k: string]: unknown }>;
  presets: Array<{ name: string; routing: number[] }>;
  [k: string]: unknown;
};

export class Sim {
  constructor(private readonly api: APIRequestContext) {}

  static async create(): Promise<Sim> {
    return new Sim(await pwRequest.newContext({ baseURL: SIM_URL }));
  }

  async dispose() {
    await this.api.dispose();
  }

  /**
   * Back to the seed state (tools/simulator/states/default.json) and no faults.
   *
   * Deliberately NOT POST /_sim/reset: that also drops the hub's login session,
   * and the hub never logs in again (every later read gets "not logged in" and
   * /api/status falls back to default names and no routing; see BE-04). PUT
   * /_sim/state replaces the state but keeps sessions.
   */
  async reset() {
    const seed = JSON.parse(fs.readFileSync(SEED_STATE, 'utf8'));
    const res = await this.api.put('/_sim/state', { data: seed });
    expect(res.ok(), await res.text()).toBeTruthy();
    expect((await this.api.delete('/_sim/faults')).ok()).toBeTruthy();
  }

  async state(): Promise<SimState> {
    const res = await this.api.get('/_sim/state');
    expect(res.ok()).toBeTruthy();
    const body = await res.json();
    return (body.state ?? body.data ?? body) as SimState;
  }

  /** Deep-merge a partial state; ports are patched by index, e.g. {outputs: {"0": {connected: 0}}}. */
  async patch(partial: Record<string, unknown>) {
    const res = await this.api.patch('/_sim/state', { data: partial });
    expect(res.ok(), await res.text()).toBeTruthy();
  }

  async faults(faults: Record<string, unknown>) {
    const res = await this.api.post('/_sim/faults', { data: faults });
    expect(res.ok(), await res.text()).toBeTruthy();
  }

  async event(event: Record<string, unknown>) {
    const res = await this.api.post('/_sim/event', { data: event });
    expect(res.ok(), await res.text()).toBeTruthy();
  }
}

/** Hub REST API from the test side (not through the page). */
export async function hubApi(forwardedFor: string): Promise<APIRequestContext> {
  return pwRequest.newContext({ baseURL: HUB_URL, extraHTTPHeaders: { 'X-Forwarded-For': forwardedFor } });
}
