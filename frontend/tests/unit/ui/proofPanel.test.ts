import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createProofPanel, statusLabel } from '../../../src/ui/proofPanel';
import { AppStore } from '../../../src/store/appStore';
import type { JobResultPayload } from '../../../src/api/types';

function makeSucceededResult(overrides?: Partial<JobResultPayload>): JobResultPayload {
  return {
    status: 'succeeded',
    message: 'ok',
    proof_text: null,
    proof_sections: {
      points: [],
      assumptions: ['a = b'],
      numerical_checks: [],
      trivial_predicates: [],
      proven_goals: ['goal1'],
      unproven_goals: [],
      proof_steps: [],
      appendix_ar: [],
      construction_signatures: [],
      step_signatures: [],
      goal_signatures: [],
      step_premise_indices: [],
    },
    run_info: null,
    sketch_points: [],
    stdout: '',
    stderr: '',
    ...overrides,
  };
}

describe('statusLabel', () => {
  // queued is the initial state right after a job is submitted
  it('returns "Queued…" for queued', () => {
    expect(statusLabel('queued')).toBe('Queued…');
  });

  // running means the prover is actively working
  it('returns "Running…" for running', () => {
    expect(statusLabel('running')).toBe('Running…');
  });

  // succeeded means a proof was found
  it('returns "Proved" for succeeded', () => {
    expect(statusLabel('succeeded')).toBe('Proved');
  });

  // failed means the prover found no proof
  it('returns "Failed" for failed', () => {
    expect(statusLabel('failed')).toBe('Failed');
  });

  // timed_out means the backend hit its time limit
  it('returns "Timed out" for timed_out', () => {
    expect(statusLabel('timed_out')).toBe('Timed out');
  });

  // cancelled means the user aborted the run
  it('returns "Cancelled" for cancelled', () => {
    expect(statusLabel('cancelled')).toBe('Cancelled');
  });

  // unknown values fall back to the raw string so no label is ever blank
  it('returns the raw status string for unrecognised values', () => {
    expect(statusLabel('something_new')).toBe('something_new');
  });
});

describe('createProofPanel', () => {
  let appStore: AppStore;
  let handle: ReturnType<typeof createProofPanel>;

  beforeEach(() => {
    appStore = new AppStore();
    handle = createProofPanel(appStore);
  });

  afterEach(() => {
    handle.destroy();
  });

  // root must carry proof-panel so the CSS layout rules apply
  it('returns a root div with class proof-panel', () => {
    expect(handle.root.tagName).toBe('DIV');
    expect(handle.root.classList.contains('proof-panel')).toBe(true);
  });

  // the back button must exist before any job is active
  it('renders a back button with class proof-back-btn', () => {
    expect(handle.root.querySelector('.proof-back-btn')).toBeTruthy();
  });

  // clicking back exits proof mode so the canvas becomes editable again
  it('clicking the back button calls appStore.exitProofMode', () => {
    const spy = vi.spyOn(appStore, 'exitProofMode');
    const btn = handle.root.querySelector('.proof-back-btn') as HTMLButtonElement;
    btn.click();
    expect(spy).toHaveBeenCalledOnce();
  });

  // with no active job the content area renders nothing
  it('renders no status row when no active job is set', () => {
    expect(handle.root.querySelector('.proof-status-row')).toBeNull();
  });

  // a running job should show the spinner so the user knows to wait
  it('shows a spinner when the active job status is running', () => {
    appStore.addJob('j1', 'problem');
    appStore.updateJob('j1', { status: 'running' });
    expect(handle.root.querySelector('.proof-spinner')).toBeTruthy();
  });

  // the status badge uses data-status as the CSS hook for color coding
  it('renders a status badge with the correct data-status attribute', () => {
    appStore.addJob('j1', 'problem');
    const badge = handle.root.querySelector('.proof-status-badge');
    expect(badge?.getAttribute('data-status')).toBe('queued');
  });

  // a succeeded job with proof sections should surface the assumptions list
  it('renders Assumptions section when job succeeded with proof sections', () => {
    appStore.addJob('j1', 'problem');
    appStore.updateJob('j1', { status: 'succeeded', result: makeSucceededResult() });
    const sectionTitle = Array.from(handle.root.querySelectorAll('.proof-section-title')).find(
      (el) => el.textContent === 'Assumptions',
    );
    expect(sectionTitle).toBeTruthy();
  });

  // destroy must unsubscribe so the panel does not re-render after removal
  it('destroy unsubscribes so the panel no longer re-renders on store changes', () => {
    handle.destroy();
    const content = handle.root.querySelector('.proof-panel-content') as HTMLElement;
    const snapshot = content.innerHTML;
    appStore.addJob('j-after-destroy', 'problem');
    expect(content.innerHTML).toBe(snapshot);
  });
});
