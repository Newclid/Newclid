import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { BackendClient } from '../../src/api/backendClient';
import { JobPoller } from '../../src/api/jobPoller';
import { AppStore } from '../../src/store/appStore';
import { Scene } from '../../src/scene/scene';
import { emitScene } from '../../src/emit/jgex';
import { buildNameTable } from '../../src/emit/names';

type FetchMock = ReturnType<typeof vi.fn>;

function mockFetchOnce(data: unknown, status = 200): void {
  (globalThis.fetch as FetchMock).mockResolvedValueOnce(
    new Response(JSON.stringify(data), {
      status,
      headers: { 'Content-Type': 'application/json' },
    }),
  );
}

function mockFetchReject(error: Error): void {
  (globalThis.fetch as FetchMock).mockRejectedValueOnce(error);
}

describe('problem submission and job lifecycle', () => {
  let store: AppStore;
  let client: BackendClient;
  let poller: JobPoller;

  beforeEach(() => {
    vi.useFakeTimers();
    vi.stubGlobal('fetch', vi.fn());
    store = new AppStore();
    client = new BackendClient('/api');
    poller = new JobPoller(client, store);
  });

  afterEach(() => {
    poller.stop();
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  // emitScene walks a real Scene and produces the JGEX setup string for two free points
  it('converts a two-point scene into the correct JGEX setup string', () => {
    const scene = new Scene();
    scene.addPoint(0, 0);
    scene.addPoint(1, 0);
    const nameTable = buildNameTable(scene);
    const jgex = emitScene(scene);
    expect(nameTable.size).toBe(2);
    expect(jgex).toContain('free');
  });

  // submitJob must POST to /api/jobs with the correct body shape
  it('posts the problem to /api/jobs and returns the job_id', async () => {
    mockFetchOnce({ job_id: 'abc123', status: 'queued' });
    const resp = await client.submitJob('A = free A; B = free B', []);
    expect(resp.job_id).toBe('abc123');
    const call = (globalThis.fetch as FetchMock).mock.calls[0];
    const body = JSON.parse(call[1].body as string);
    expect(body.input_type).toBe('jgex');
    expect(body.problem_input).toBe('A = free A; B = free B');
  });

  // addJob must create a queued record and set it as the active job
  it('adds the returned job_id to the store with status queued', async () => {
    mockFetchOnce({ job_id: 'j1', status: 'queued' });
    const resp = await client.submitJob('A = free A', []);
    store.addJob(resp.job_id, 'A = free A');
    const record = store.jobs.get('j1');
    expect(record?.status).toBe('queued');
    expect(store.activeJobId).toBe('j1');
  });

  // the poller must update status from queued to running after the first tick
  it('transitions the job status from queued to running on the first poll tick', async () => {
    mockFetchOnce({ job_id: 'j1', status: 'queued' });
    const resp = await client.submitJob('A = free A', []);
    store.addJob(resp.job_id, 'A = free A');

    mockFetchOnce({ job_id: 'j1', status: 'running', message: null });
    poller.start('j1');
    await vi.advanceTimersByTimeAsync(2000);

    expect(store.jobs.get('j1')?.status).toBe('running');
  });

  // a succeeded response from the poller must fetch the result and store it
  it('fetches the result and updates the store when the job succeeds', async () => {
    store.addJob('j1', 'A = free A');

    // First tick: running
    mockFetchOnce({ job_id: 'j1', status: 'running', message: null });
    poller.start('j1');
    await vi.advanceTimersByTimeAsync(2000);

    // Second tick: succeeded then getJobResult
    mockFetchOnce({ job_id: 'j1', status: 'succeeded', message: null });
    mockFetchOnce({
      job_id: 'j1',
      status: 'succeeded',
      result: {
        status: 'succeeded',
        message: 'Proof found',
        proof_text: null,
        proof_sections: null,
        run_info: null,
        sketch_points: [],
        stdout: '',
        stderr: '',
      },
      error: null,
    });
    await vi.advanceTimersByTimeAsync(2000);
    await vi.runAllTimersAsync();

    expect(store.jobs.get('j1')?.status).toBe('succeeded');
    expect(store.jobs.get('j1')?.result?.status).toBe('succeeded');
  });

  // a network error during submitJob must reject with an ApiError message
  it('rejects with a network ApiError when the submit fetch fails', async () => {
    mockFetchReject(new TypeError('Failed to fetch'));
    await expect(client.submitJob('A = free A', [])).rejects.toThrow('Network error');
  });

  // a non-retryable 404 during polling must store the error and stop the interval
  it('stores the error and stops polling when the status endpoint returns 404', async () => {
    store.addJob('j1', 'A = free A');

    mockFetchOnce({ detail: 'Not found' }, 404);
    poller.start('j1');
    await vi.advanceTimersByTimeAsync(2000);
    await vi.runAllTimersAsync();

    expect(store.jobs.get('j1')?.error).toBeTruthy();

    const callCount = (globalThis.fetch as FetchMock).mock.calls.length;
    await vi.advanceTimersByTimeAsync(4000);
    expect((globalThis.fetch as FetchMock).mock.calls.length).toBe(callCount);
  });

  // a failed job must trigger fetchResult and then stop the poller
  it('fetches the result and stops polling when the job enters the failed state', async () => {
    store.addJob('j1', 'A = free A');

    mockFetchOnce({ job_id: 'j1', status: 'failed', message: 'No proof' });
    mockFetchOnce({
      job_id: 'j1',
      status: 'failed',
      result: {
        status: 'failed',
        message: 'No proof',
        proof_text: null,
        proof_sections: null,
        run_info: null,
        sketch_points: [],
        stdout: '',
        stderr: '',
      },
      error: null,
    });
    poller.start('j1');
    await vi.advanceTimersByTimeAsync(2000);
    await vi.runAllTimersAsync();

    expect(store.jobs.get('j1')?.status).toBe('failed');
    expect(store.jobs.get('j1')?.result?.status).toBe('failed');
  });

  // after a terminal status the poller interval must be cleared with no further status calls
  it('makes no further status calls after the job reaches a terminal status', async () => {
    store.addJob('j1', 'A = free A');

    mockFetchOnce({ job_id: 'j1', status: 'succeeded', message: null });
    mockFetchOnce({
      job_id: 'j1',
      status: 'succeeded',
      result: {
        status: 'succeeded',
        message: 'ok',
        proof_text: null,
        proof_sections: null,
        run_info: null,
        sketch_points: [],
        stdout: '',
        stderr: '',
      },
      error: null,
    });
    poller.start('j1');
    await vi.advanceTimersByTimeAsync(2000);
    await vi.runAllTimersAsync();

    const callCount = (globalThis.fetch as FetchMock).mock.calls.length;
    await vi.advanceTimersByTimeAsync(4000);
    expect((globalThis.fetch as FetchMock).mock.calls.length).toBe(callCount);
  });
});
