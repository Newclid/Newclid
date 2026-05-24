import type { BackendClient } from './backendClient';
import { ApiError, TERMINAL_STATUSES } from './types';
import type { AppStore } from '../store/appStore';

export class JobPoller {
  private intervalId: ReturnType<typeof setInterval> | null = null;

  constructor(
    private readonly client: BackendClient,
    private readonly store: AppStore,
  ) {}

  start(jobId: string, intervalMs = 2000): void {
    this.stop();
    this.intervalId = setInterval(() => void this.tick(jobId), intervalMs);
  }

  stop(): void {
    if (this.intervalId !== null) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  private async tick(jobId: string): Promise<void> {
    try {
      const statusResp = await this.client.getJobStatus(jobId);
      this.store.updateJob(jobId, {
        status: statusResp.status,
        message: statusResp.message,
      });
      if (TERMINAL_STATUSES.has(statusResp.status)) {
        this.stop();
        await this.fetchResult(jobId);
      }
    } catch (err) {
      if (err instanceof ApiError && !err.retryable) {
        this.store.updateJob(jobId, { error: err.message });
        this.stop();
      }
      // retryable errors (network blip, 503): keep polling
    }
  }

  private async fetchResult(jobId: string): Promise<void> {
    try {
      const resultResp = await this.client.getJobResult(jobId);
      this.store.updateJob(jobId, {
        result: resultResp.result ?? null,
        error: resultResp.error ?? null,
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      this.store.updateJob(jobId, { error: msg });
    }
  }
}
