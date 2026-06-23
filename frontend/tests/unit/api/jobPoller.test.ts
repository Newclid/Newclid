import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { JobPoller } from '../../../src/api/jobPoller';
import { ApiError } from '../../../src/api/types';
import type { BackendClient } from '../../../src/api/backendClient';
import type { AppStore } from '../../../src/store/appStore';

function makeClient(): Pick<BackendClient, 'getJobStatus' | 'getJobResult'> {
  return {
    getJobStatus: vi.fn(),
    getJobResult: vi.fn(),
  };
}

function makeStore(): Pick<AppStore, 'updateJob'> {
  return {
    updateJob: vi.fn(),
  };
}

const INTERVAL = 2000;

describe('JobPoller', () => {
  let client: ReturnType<typeof makeClient>;
  let store: ReturnType<typeof makeStore>;
  let poller: JobPoller;

  beforeEach(() => {
    vi.useFakeTimers();
    client = makeClient();
    store = makeStore();
    poller = new JobPoller(
      client as unknown as BackendClient,
      store as unknown as AppStore,
    );
  });

  afterEach(() => {
    poller.stop();
    vi.useRealTimers();
  });

  describe('start()', () => {
    it('begins polling after intervalMs elapses', async () => {
      vi.mocked(client.getJobStatus).mockResolvedValue({ job_id: 'j1', status: 'running', message: null });
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL);
      expect(client.getJobStatus).toHaveBeenCalledWith('j1');
    });

    it('calling start() again clears the previous interval and starts a fresh one', async () => {
      vi.mocked(client.getJobStatus).mockResolvedValue({ job_id: 'j1', status: 'running', message: null });
      poller.start('j1', INTERVAL);
      poller.start('j2', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL);
      expect(client.getJobStatus).toHaveBeenCalledTimes(1);
      expect(client.getJobStatus).toHaveBeenCalledWith('j2');
    });
  });

  describe('stop()', () => {
    it('clears the interval so no further ticks occur', async () => {
      vi.mocked(client.getJobStatus).mockResolvedValue({ job_id: 'j1', status: 'running', message: null });
      poller.start('j1', INTERVAL);
      poller.stop();
      await vi.advanceTimersByTimeAsync(INTERVAL * 3);
      expect(client.getJobStatus).not.toHaveBeenCalled();
    });

    it('is a no-op when no interval is active', () => {
      expect(() => poller.stop()).not.toThrow();
    });
  });

  describe('tick — non-terminal status', () => {
    beforeEach(() => {
      vi.mocked(client.getJobStatus).mockResolvedValue({ job_id: 'j1', status: 'running', message: 'In progress' });
    });

    it('calls getJobStatus with jobId', async () => {
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL);
      expect(client.getJobStatus).toHaveBeenCalledWith('j1');
    });

    it('calls store.updateJob with { status, message }', async () => {
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL);
      expect(store.updateJob).toHaveBeenCalledWith('j1', { status: 'running', message: 'In progress' });
    });

    it('does not stop — interval still fires on next tick', async () => {
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL * 2);
      expect(client.getJobStatus).toHaveBeenCalledTimes(2);
    });

    it('does not call getJobResult', async () => {
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL);
      expect(client.getJobResult).not.toHaveBeenCalled();
    });
  });

  describe('tick — terminal status', () => {
    const resultPayload = { status: 'succeeded' as const, message: 'Done', proof_text: null, proof_sections: null, run_info: null, sketch_points: [], stdout: '', stderr: '' };

    beforeEach(() => {
      vi.mocked(client.getJobStatus).mockResolvedValue({ job_id: 'j1', status: 'succeeded', message: 'Done' });
      vi.mocked(client.getJobResult).mockResolvedValue({ job_id: 'j1', status: 'succeeded', result: resultPayload, error: null });
    });

    it('calls store.updateJob with { status, message }', async () => {
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL);
      expect(store.updateJob).toHaveBeenCalledWith('j1', { status: 'succeeded', message: 'Done' });
    });

    it('stops polling after a terminal status', async () => {
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL * 3);
      expect(client.getJobStatus).toHaveBeenCalledTimes(1);
    });

    it('calls getJobResult with jobId', async () => {
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL);
      expect(client.getJobResult).toHaveBeenCalledWith('j1');
    });

    it('calls store.updateJob with { result, error } from result response', async () => {
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL);
      expect(store.updateJob).toHaveBeenCalledWith('j1', { result: resultPayload, error: null });
    });
  });

  describe('tick — retryable ApiError (httpStatus=503)', () => {
    beforeEach(() => {
      vi.mocked(client.getJobStatus).mockRejectedValue(new ApiError(503, 'Service unavailable'));
    });

    it('does not call store.updateJob with an error', async () => {
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL);
      expect(store.updateJob).not.toHaveBeenCalled();
    });

    it('keeps polling — second tick fires', async () => {
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL * 2);
      expect(client.getJobStatus).toHaveBeenCalledTimes(2);
    });
  });

  describe('tick — non-retryable ApiError (httpStatus=400)', () => {
    beforeEach(() => {
      vi.mocked(client.getJobStatus).mockRejectedValue(new ApiError(400, 'Bad request'));
    });

    it('calls store.updateJob with { error: err.message }', async () => {
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL);
      expect(store.updateJob).toHaveBeenCalledWith('j1', { error: 'Bad request' });
    });

    it('stops polling', async () => {
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL * 3);
      expect(client.getJobStatus).toHaveBeenCalledTimes(1);
    });
  });

  describe('fetchResult — result null, error non-null', () => {
    it('calls store.updateJob with { result: null, error: string } when getJobResult returns an error payload', async () => {
      vi.mocked(client.getJobStatus).mockResolvedValue({ job_id: 'j1', status: 'failed', message: null });
      vi.mocked(client.getJobResult).mockResolvedValue({ job_id: 'j1', status: 'failed', result: null, error: 'solver failed' });
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL);
      expect(store.updateJob).toHaveBeenCalledWith('j1', { result: null, error: 'solver failed' });
    });
  });

  describe('fetchResult error', () => {
    it('calls store.updateJob with { error: errorMessage } when getJobResult throws an Error', async () => {
      vi.mocked(client.getJobStatus).mockResolvedValue({ job_id: 'j1', status: 'succeeded', message: 'Done' });
      vi.mocked(client.getJobResult).mockRejectedValue(new Error('fetch failed'));
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL);
      expect(store.updateJob).toHaveBeenCalledWith('j1', { error: 'fetch failed' });
    });

    it('calls store.updateJob with stringified error when getJobResult throws a non-Error value', async () => {
      vi.mocked(client.getJobStatus).mockResolvedValue({ job_id: 'j1', status: 'succeeded', message: 'Done' });
      vi.mocked(client.getJobResult).mockRejectedValue('non-error string');
      poller.start('j1', INTERVAL);
      await vi.advanceTimersByTimeAsync(INTERVAL);
      expect(store.updateJob).toHaveBeenCalledWith('j1', { error: 'non-error string' });
    });
  });
});
