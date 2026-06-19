import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { BackendClient } from '../../../src/api/backendClient';
import { ApiError } from '../../../src/api/types';

function mockResponse(opts: {
  ok: boolean;
  status?: number;
  statusText?: string;
  json?: () => Promise<unknown>;
}): Response {
  return {
    ok: opts.ok,
    status: opts.status ?? 200,
    statusText: opts.statusText ?? 'OK',
    json: opts.json ?? (() => Promise.resolve({})),
  } as unknown as Response;
}

describe('BackendClient', () => {
  let fetchMock: ReturnType<typeof vi.fn>;
  let client: BackendClient;

  beforeEach(() => {
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    client = new BackendClient();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  describe('healthCheck()', () => {
    it('returns true when fetch resolves with an ok response', async () => {
      fetchMock.mockResolvedValue(mockResponse({ ok: true }));
      expect(await client.healthCheck()).toBe(true);
    });

    it('returns false when fetch throws', async () => {
      fetchMock.mockRejectedValue(new Error('Network down'));
      expect(await client.healthCheck()).toBe(false);
    });
  });

  describe('submitJob()', () => {
    it('POSTs to /api/jobs with correct Content-Type and JSON body', async () => {
      fetchMock.mockResolvedValue(
        mockResponse({ ok: true, json: () => Promise.resolve({ job_id: 'j1', status: 'queued' }) }),
      );
      await client.submitJob('problem text', []);
      expect(fetchMock).toHaveBeenCalledWith('/api/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input_type: 'jgex',
          problem_input: 'problem text',
          custom_theorems: [],
        }),
      });
    });
  });

  describe('getJobStatus()', () => {
    it('GETs /api/jobs/<encodeURIComponent(jobId)>', async () => {
      fetchMock.mockResolvedValue(
        mockResponse({ ok: true, json: () => Promise.resolve({ job_id: 'j/1', status: 'running', message: null }) }),
      );
      await client.getJobStatus('j/1');
      expect(fetchMock).toHaveBeenCalledWith('/api/jobs/j%2F1', undefined);
    });
  });

  describe('getJobResult()', () => {
    it('GETs /api/jobs/<encodeURIComponent(jobId)>/result', async () => {
      fetchMock.mockResolvedValue(
        mockResponse({ ok: true, json: () => Promise.resolve({ job_id: 'j/1', status: 'succeeded', result: null, error: null }) }),
      );
      await client.getJobResult('j/1');
      expect(fetchMock).toHaveBeenCalledWith('/api/jobs/j%2F1/result', undefined);
    });
  });

  describe('request error handling', () => {
    it('throws ApiError(0, "Network error: ...") when fetch itself throws an Error', async () => {
      fetchMock.mockRejectedValue(new Error('timeout'));
      await expect(client.getJobStatus('job1')).rejects.toSatisfy(
        (err: unknown) =>
          err instanceof ApiError &&
          err.httpStatus === 0 &&
          err.message === 'Network error: timeout',
      );
    });

    it('throws ApiError(0, "Network error: ...") when fetch throws a non-Error value', async () => {
      fetchMock.mockRejectedValue('string failure');
      await expect(client.getJobStatus('job1')).rejects.toSatisfy(
        (err: unknown) =>
          err instanceof ApiError &&
          err.httpStatus === 0 &&
          err.message === 'Network error: string failure',
      );
    });

    it('throws ApiError(status, detail) when response not ok and JSON body has detail', async () => {
      fetchMock.mockResolvedValue(
        mockResponse({
          ok: false,
          status: 422,
          statusText: 'Unprocessable Entity',
          json: () => Promise.resolve({ detail: 'Validation error' }),
        }),
      );
      await expect(client.getJobStatus('job1')).rejects.toSatisfy(
        (err: unknown) =>
          err instanceof ApiError && err.httpStatus === 422 && err.message === 'Validation error',
      );
    });

    it('throws ApiError(status, statusText) when response not ok and JSON body has no string detail', async () => {
      fetchMock.mockResolvedValue(
        mockResponse({
          ok: false,
          status: 503,
          statusText: 'Service Unavailable',
          json: () => Promise.resolve({ other: 'field' }),
        }),
      );
      await expect(client.getJobStatus('job1')).rejects.toSatisfy(
        (err: unknown) =>
          err instanceof ApiError &&
          err.httpStatus === 503 &&
          err.message === 'Service Unavailable',
      );
    });

    it('throws ApiError(status, statusText) when response not ok and JSON parse fails', async () => {
      fetchMock.mockResolvedValue(
        mockResponse({
          ok: false,
          status: 500,
          statusText: 'Internal Server Error',
          json: () => Promise.reject(new Error('invalid json')),
        }),
      );
      await expect(client.getJobStatus('job1')).rejects.toSatisfy(
        (err: unknown) =>
          err instanceof ApiError &&
          err.httpStatus === 500 &&
          err.message === 'Internal Server Error',
      );
    });

    it('returns parsed JSON when response is ok', async () => {
      const payload = { job_id: 'x', status: 'queued', message: null };
      fetchMock.mockResolvedValue(
        mockResponse({ ok: true, json: () => Promise.resolve(payload) }),
      );
      const result = await client.getJobStatus('x');
      expect(result).toEqual(payload);
    });
  });
});
