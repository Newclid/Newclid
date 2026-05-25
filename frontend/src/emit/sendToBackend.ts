import type { Scene } from '../scene/scene';
import { emitScene } from './jgex';

export interface SendOptions {
  endpoint: string;
  goal?: string;
}

export interface SendResult {
  ok: boolean;
  status: number;
  sent: string;
  body: unknown;
}

export async function sendJgex(scene: Scene, opts: SendOptions): Promise<SendResult> {
  const setup = emitScene(scene);
  const body = opts.goal ? `${setup} ? ${opts.goal}` : setup;

  const res = await fetch(opts.endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'text/plain' },
    body,
  });

  return {
    ok: res.ok,
    status: res.status,
    sent: body,
    body: await res.json().catch(() => null),
  };
}