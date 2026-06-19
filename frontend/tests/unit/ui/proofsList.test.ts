import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createProofsList } from '../../../src/ui/proofsList';
import { AppStore } from '../../../src/store/appStore';

describe('createProofsList', () => {
  let appStore: AppStore;
  let handle: ReturnType<typeof createProofsList>;

  beforeEach(() => {
    vi.stubGlobal('ResizeObserver', class {
      observe() {}
      unobserve() {}
      disconnect() {}
    });
    appStore = new AppStore();
    handle = createProofsList(appStore);
  });

  afterEach(() => {
    handle.destroy();
    vi.unstubAllGlobals();
  });

  // root must have proofs-list so the CSS list layout rules apply
  it('returns a root div with class proofs-list', () => {
    expect(handle.root.classList.contains('proofs-list')).toBe(true);
  });

  // when the store has no jobs the empty state must be visible
  it('shows empty state paragraph when no jobs exist', () => {
    const empty = handle.root.querySelector('.proofs-list-empty');
    expect(empty?.textContent).toBe('No proofs yet.');
  });

  // once a job exists the empty state must be gone
  it('does not show empty state when at least one job exists', () => {
    appStore.addJob('j1', 'problem');
    expect(handle.root.querySelector('.proofs-list-empty')).toBeNull();
  });

  // each job maps to exactly one row in the list
  it('renders one row per job', () => {
    appStore.addJob('j1', 'problem1');
    appStore.addJob('j2', 'problem2');
    const rows = handle.root.querySelectorAll('.proofs-list-item');
    expect(rows.length).toBe(2);
  });

  // the status badge communicates job state at a glance via CSS data-status coloring
  it('renders a status badge with the correct data-status for each job', () => {
    appStore.addJob('j1', 'problem');
    const badge = handle.root.querySelector('.proof-status-badge');
    expect(badge?.getAttribute('data-status')).toBe('queued');
  });

  // clicking the main area must activate the job and switch to the proof panel
  it('clicking the main area calls setActiveJob and enterProofMode', () => {
    appStore.addJob('j1', 'problem');
    const setActiveSpy = vi.spyOn(appStore, 'setActiveJob');
    const enterModeSpy = vi.spyOn(appStore, 'enterProofMode');
    const main = handle.root.querySelector('.proofs-list-item-main') as HTMLElement;
    main.click();
    expect(setActiveSpy).toHaveBeenCalledWith('j1');
    expect(enterModeSpy).toHaveBeenCalledOnce();
  });

  // a job without a custom name should display Solution N
  it('shows "Solution 1" as the default name for the first job', () => {
    appStore.addJob('j1', 'problem');
    const nameSpan = handle.root.querySelector('.proofs-list-name');
    expect(nameSpan?.textContent).toBe('Solution 1');
  });

  // the list must re-render when the store notifies about a new job
  it('re-renders when a new job is added', () => {
    expect(handle.root.querySelector('.proofs-list-item')).toBeNull();
    appStore.addJob('j1', 'problem');
    expect(handle.root.querySelector('.proofs-list-item')).toBeTruthy();
  });

  // destroy must unsubscribe so the list does not re-render after removal
  it('destroy unsubscribes so the list no longer re-renders on store changes', () => {
    handle.destroy();
    const snapshot = handle.root.innerHTML;
    appStore.addJob('j-after-destroy', 'problem');
    expect(handle.root.innerHTML).toBe(snapshot);
  });

  // destroy must disconnect the ResizeObserver to stop watching element size
  it('destroy calls disconnect on the ResizeObserver', () => {
    const disconnectSpy = vi.fn();
    vi.stubGlobal('ResizeObserver', class {
      observe() {}
      unobserve() {}
      disconnect = disconnectSpy;
    });
    const handle2 = createProofsList(appStore);
    handle2.destroy();
    expect(disconnectSpy).toHaveBeenCalledOnce();
  });
});
