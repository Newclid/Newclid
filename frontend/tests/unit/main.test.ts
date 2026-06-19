import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// main.ts is a top-level imperative bootstrap script (not a function/class),
// so each test re-imports it fresh after vi.resetModules(). Heavy collaborators
// are mocked per tests/README.md ("replace external collaborators with fakes,
// stubs or mocks"). Scene/AppStore/theoremStore and the pure emit/* helpers are
// real, dependency-free state containers and pure functions.
vi.mock('../../src/geometry/viewport', () => ({
  Viewport: vi.fn(function (this: any) {
    this.width = 0;
    this.height = 0;
    this.fitPoints = vi.fn();
  }),
}));
vi.mock('../../src/render/renderer', () => ({
  Renderer: vi.fn(function (this: any) {
    this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    this.draw = vi.fn();
    this.resize = vi.fn();
    this.proofSketch = null;
  }),
}));
vi.mock('../../src/input/panZoom', () => ({ attachPanZoom: vi.fn() }));
vi.mock('../../src/input/toolDispatcher', () => ({ attachToolDispatcher: vi.fn() }));
vi.mock('../../src/input/shortcuts', () => ({ attachShortcuts: vi.fn() }));
vi.mock('../../src/ui/toolbar', () => ({
  createToolbar: vi.fn(() => ({ root: document.createElement('div'), destroy: vi.fn() })),
}));
vi.mock('../../src/api/backendClient', () => ({
  BackendClient: vi.fn(function (this: any) {
    this.submitJob = vi.fn();
    this.getJobStatus = vi.fn();
    this.getJobResult = vi.fn();
    this.healthCheck = vi.fn();
  }),
}));
vi.mock('../../src/api/jobPoller', () => ({
  JobPoller: vi.fn(function (this: any) {
    this.start = vi.fn();
    this.stop = vi.fn();
  }),
}));
vi.mock('../../src/ui/notifications', () => ({
  initNotifications: vi.fn(),
  notify: vi.fn(),
}));
vi.mock('../../src/ui/toolbarResizer', () => ({
  attachToolbarResizer: vi.fn(() => vi.fn()),
}));

const MAIN_PATH = '../../src/main';

// Re-imports main.ts fresh against the current mock/module registry epoch.
// Callers that need to inspect a mocked collaborator's calls must dynamically
// import that module too, AFTER this, within the same test (no further
// vi.resetModules() in between) so they share the same cached registry entry.
async function loadMain() {
  return import(MAIN_PATH);
}

describe('main.ts application shell bootstrap', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="app"></div>';
    localStorage.clear();
    vi.resetModules();
    vi.clearAllMocks();
    vi.stubGlobal(
      'ResizeObserver',
      class {
        observe() {}
        unobserve() {}
        disconnect() {}
      },
    );
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
    document.body.innerHTML = '';
  });

  describe('module bootstrap', () => {
    // bootstrap should fail loudly instead of silently doing nothing
    it('throws when #app element is missing from the document', async () => {
      document.body.innerHTML = '';
      await expect(loadMain()).rejects.toThrow('No #app element found in HTML');
    });

    // the toolbar is the first thing main.ts hands off to the DOM
    it('appends the toolbar root returned by createToolbar into #app', async () => {
      await loadMain();
      const { createToolbar } = await import('../../src/ui/toolbar');
      const fakeToolbar = (createToolbar as ReturnType<typeof vi.fn>).mock.results[0].value;

      const app = document.getElementById('app')!;
      expect(app.contains(fakeToolbar.root)).toBe(true);
    });

    // the resizer needs both elements to know what it's dragging between
    it('calls attachToolbarResizer with the app root and toolbar root', async () => {
      await loadMain();
      const { createToolbar } = await import('../../src/ui/toolbar');
      const { attachToolbarResizer } = await import('../../src/ui/toolbarResizer');
      const fakeToolbar = (createToolbar as ReturnType<typeof vi.fn>).mock.results[0].value;

      expect(attachToolbarResizer).toHaveBeenCalledWith({
        app: document.getElementById('app'),
        toolbar: fakeToolbar.root,
      });
    });

    // the notification banner should mount exactly once, not on every reload of this test
    it('calls initNotifications once on bootstrap', async () => {
      await loadMain();
      const { initNotifications } = await import('../../src/ui/notifications');
      expect(initNotifications).toHaveBeenCalledTimes(1);
    });

    // the canvas host is where the renderer and all the floating UI live
    it('creates a canvas-host div and appends it to #app', async () => {
      await loadMain();
      const canvasHost = document.querySelector('.canvas-host');
      expect(canvasHost).toBeTruthy();
      expect(document.getElementById('app')!.contains(canvasHost)).toBe(true);
    });

    // confirms the renderer gets wired up with the right host and viewport
    it('constructs Renderer with the canvasHost and a Viewport instance', async () => {
      await loadMain();
      const { Renderer } = await import('../../src/render/renderer');
      const { Viewport } = await import('../../src/geometry/viewport');
      const canvasHost = document.querySelector('.canvas-host');
      const viewportInstance = (Viewport as ReturnType<typeof vi.fn>).mock.results[0].value;

      const call = (Renderer as ReturnType<typeof vi.fn>).mock.calls[0];
      expect(call[0]).toBe(canvasHost);
      expect(call[1]).toBe(viewportInstance);
      expect(typeof call[2].subscribe).toBe('function'); // the real Scene instance
    });

    // these three are what make the canvas actually interactive, easy to forget wiring one up
    it('calls attachPanZoom, attachToolDispatcher, and attachShortcuts during bootstrap', async () => {
      await loadMain();
      const { attachPanZoom } = await import('../../src/input/panZoom');
      const { attachToolDispatcher } = await import('../../src/input/toolDispatcher');
      const { attachShortcuts } = await import('../../src/input/shortcuts');

      expect(attachPanZoom).toHaveBeenCalledTimes(1);
      expect(attachToolDispatcher).toHaveBeenCalledTimes(1);
      expect(attachShortcuts).toHaveBeenCalledTimes(1);
    });

    // both pills should start hidden, they only show up once the scene has something to say
    it('creates hidden slot-hint and slot-error elements inside canvas-host', async () => {
      await loadMain();
      const canvasHost = document.querySelector('.canvas-host')!;
      const hint = canvasHost.querySelector('.slot-hint') as HTMLElement;
      const error = canvasHost.querySelector('.slot-error') as HTMLElement;

      expect(hint.hidden).toBe(true);
      expect(error.hidden).toBe(true);
    });

    // redraw only makes sense once there's a result to redraw, so it starts hidden
    it('creates a hidden redraw-btn inside canvas-host', async () => {
      await loadMain();
      const redrawBtn = document.querySelector('.canvas-host .redraw-btn') as HTMLButtonElement;
      expect(redrawBtn.hidden).toBe(true);
    });
  });

  describe('exported singletons', () => {
    // other modules import this directly, so it has to actually be usable
    it('exports an AppStore-shaped instance as appStore', async () => {
      const mod = await loadMain();
      expect(mod.appStore.proofMode).toBe(false);
      expect(typeof mod.appStore.subscribe).toBe('function');
      expect(typeof mod.appStore.addJob).toBe('function');
    });

    // same idea, this is the only handle other code gets to talk to the backend
    it('exports a BackendClient-shaped instance as backendClient', async () => {
      const mod = await loadMain();
      expect(typeof mod.backendClient.submitJob).toBe('function');
      expect(typeof mod.backendClient.getJobStatus).toBe('function');
      expect(typeof mod.backendClient.getJobResult).toBe('function');
    });

    // and this is what actually drives polling once a job is submitted
    it('exports a JobPoller-shaped instance as jobPoller', async () => {
      const mod = await loadMain();
      expect(typeof mod.jobPoller.start).toBe('function');
      expect(typeof mod.jobPoller.stop).toBe('function');
    });
  });

  describe('job result notification (appStore subscription)', () => {
    // a successful proof should produce exactly one toast, not zero or several
    it('notifies success exactly once when a job result has status succeeded', async () => {
      const mod = await loadMain();
      const { notify } = await import('../../src/ui/notifications');

      mod.appStore.addJob('j1', 'problem');
      mod.appStore.updateJob('j1', {
        result: { status: 'succeeded', message: null } as any,
      });

      expect(notify).toHaveBeenCalledTimes(1);
      expect(notify).toHaveBeenCalledWith('success', 'Proof complete');
    });

    // the user should see why it failed, not just that it failed
    it('notifies error with the result message when job result status is failed', async () => {
      const mod = await loadMain();
      const { notify } = await import('../../src/ui/notifications');

      mod.appStore.addJob('j1', 'problem');
      mod.appStore.updateJob('j1', {
        result: { status: 'failed', message: 'no proof found' } as any,
      });

      expect(notify).toHaveBeenCalledWith('error', 'no proof found');
    });

    // covers the transport-level failure path, separate from a returned failed result
    it('notifies error with job.error when the job has an error and no result', async () => {
      const mod = await loadMain();
      const { notify } = await import('../../src/ui/notifications');

      mod.appStore.addJob('j1', 'problem');
      mod.appStore.updateJob('j1', { error: 'network down' });

      expect(notify).toHaveBeenCalledWith('error', 'network down');
    });

    // this guards the dedup key, an unrelated emit should not trigger a second toast
    it('does not re-notify for the same job result on a second unrelated appStore emit', async () => {
      const mod = await loadMain();
      const { notify } = await import('../../src/ui/notifications');

      mod.appStore.addJob('j1', 'problem');
      mod.appStore.updateJob('j1', {
        result: { status: 'succeeded', message: null } as any,
      });
      mod.appStore.setPanelTab('proofs'); // unrelated emit, same job/result/error

      expect(notify).toHaveBeenCalledTimes(1);
    });

    // with no active job there's nothing to report on, so notify should stay quiet
    it('does nothing when there is no activeJobId', async () => {
      const mod = await loadMain();
      const { notify } = await import('../../src/ui/notifications');

      mod.appStore.setPanelTab('proofs'); // emits with activeJobId still null

      expect(notify).not.toHaveBeenCalled();
    });
  });

  describe('redraw button (exercised via DOM + exported backendClient/appStore)', () => {
    function getRedrawBtn(): HTMLButtonElement {
      return document.querySelector('.redraw-btn') as HTMLButtonElement;
    }

    // redraw only makes sense when there's actually something on the canvas to redraw
    it('shows the redraw button when proofMode is active and the job result has sketch points', async () => {
      const mod = await loadMain();
      mod.appStore.addJob('j1', 'problem');
      mod.appStore.updateJob('j1', {
        result: { status: 'succeeded', message: null, sketch_points: [{ name: 'A', x: 0, y: 0 }] } as any,
      });

      expect(getRedrawBtn().hidden).toBe(false);
    });

    // outside proof mode the button has no job context to redraw against
    it('hides the redraw button when proofMode is false', async () => {
      const mod = await loadMain();
      mod.appStore.addJob('j1', 'problem');
      mod.appStore.updateJob('j1', {
        result: { status: 'succeeded', message: null, sketch_points: [{ name: 'A', x: 0, y: 0 }] } as any,
      });
      mod.appStore.exitProofMode();

      expect(getRedrawBtn().hidden).toBe(true);
    });

    // an empty sketch_points array means nothing to draw, so hide rather than show an empty redraw
    it('hides the redraw button when the job result has zero sketch points', async () => {
      const mod = await loadMain();
      mod.appStore.addJob('j1', 'problem');
      mod.appStore.updateJob('j1', {
        result: { status: 'succeeded', message: null, sketch_points: [] } as any,
      });

      expect(getRedrawBtn().hidden).toBe(true);
    });

    // this is the whole resubmit-and-poll loop end to end, the meaty one of the bunch
    it('clicking redraw resubmits the job, polls until terminal status, and updates job.result.sketch_points', async () => {
      vi.useFakeTimers();
      const mod = await loadMain();
      mod.appStore.addJob('j1', 'problem');
      mod.appStore.updateJob('j1', {
        result: { status: 'succeeded', message: null, sketch_points: [{ name: 'A', x: 0, y: 0 }] } as any,
      });

      mod.backendClient.submitJob.mockResolvedValueOnce({ job_id: 'j2', status: 'queued' });
      mod.backendClient.getJobStatus
        .mockResolvedValueOnce({ job_id: 'j2', status: 'running', message: null })
        .mockResolvedValueOnce({ job_id: 'j2', status: 'succeeded', message: null });
      mod.backendClient.getJobResult.mockResolvedValueOnce({
        result: { sketch_points: [{ name: 'B', x: 1, y: 1 }] },
      });

      getRedrawBtn().click();
      await vi.advanceTimersByTimeAsync(2000); // first poll tick: running
      await vi.advanceTimersByTimeAsync(2000); // second poll tick: succeeded -> fetch result

      expect(mod.appStore.jobs.get('j1')!.result!.sketch_points).toEqual([{ name: 'B', x: 1, y: 1 }]);
      expect(getRedrawBtn().disabled).toBe(false);
      expect(getRedrawBtn().textContent).toBe('Redraw');
    });

    // the redrawing flag should stop a double click from firing two submissions
    it('clicking redraw while already redrawing is a no-op', async () => {
      vi.useFakeTimers();
      const mod = await loadMain();
      mod.appStore.addJob('j1', 'problem');
      mod.appStore.updateJob('j1', {
        result: { status: 'succeeded', message: null, sketch_points: [{ name: 'A', x: 0, y: 0 }] } as any,
      });
      mod.backendClient.submitJob.mockResolvedValue({ job_id: 'j2', status: 'queued' });
      mod.backendClient.getJobStatus.mockResolvedValue({ job_id: 'j2', status: 'running', message: null });

      getRedrawBtn().click();
      getRedrawBtn().click(); // second click while redrawing=true

      expect(mod.backendClient.submitJob).toHaveBeenCalledTimes(1);
    });

    // a stray click with nothing active should bail out before touching the backend
    it('redraw click does nothing when there is no active job', async () => {
      const mod = await loadMain();
      // no job was added, the redraw button is hidden but can still receive a programmatic click
      getRedrawBtn().click();

      expect(mod.backendClient.submitJob).not.toHaveBeenCalled();
    });

    // a failed submit shouldn't leave the button stuck disabled and saying Redrawing forever
    it('redraw click silently swallows network errors and resets button state', async () => {
      const mod = await loadMain();
      mod.appStore.addJob('j1', 'problem');
      mod.appStore.updateJob('j1', {
        result: { status: 'succeeded', message: null, sketch_points: [{ name: 'A', x: 0, y: 0 }] } as any,
      });
      mod.backendClient.submitJob.mockRejectedValueOnce(new Error('network error'));

      getRedrawBtn().click();
      await Promise.resolve();
      await Promise.resolve();

      expect(getRedrawBtn().disabled).toBe(false);
      expect(getRedrawBtn().textContent).toBe('Redraw');
    });
  });
});
