import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

vi.mock('../../../src/geometry/hitTest', () => ({
  pickNearestPoint: vi.fn(() => null),
}));
vi.mock('../../../src/emit/names', () => ({
  buildNameTable: vi.fn(() => new Map()),
}));
vi.mock('../../../src/emit/jgex', () => ({
  emitScene: vi.fn(() => ''),
}));

import { createProofByPointsPanel } from '../../../src/ui/proofByPointsPanel';
import { AppStore } from '../../../src/store/appStore';
import { Scene } from '../../../src/scene/scene';

describe('createProofByPointsPanel', () => {
  let appStore: AppStore;
  let scene: Scene;
  let handle: ReturnType<typeof createProofByPointsPanel>;

  beforeEach(() => {
    appStore = new AppStore();
    scene = new Scene();
    vi.clearAllMocks();
    handle = createProofByPointsPanel(appStore, scene);
  });

  afterEach(() => {
    handle.destroy();
  });

  // root must have proof-panel so it inherits the shared panel CSS layout
  it('returns a root div with class proof-panel', () => {
    expect(handle.root.classList.contains('proof-panel')).toBe(true);
  });

  // the back button must be present so the user can return to canvas editing
  it('renders a back button with class proof-back-btn', () => {
    expect(handle.root.querySelector('.proof-back-btn')).toBeTruthy();
  });

  // clicking back must call exitProofByPoints to restore the canvas state
  it('clicking the back button calls appStore.exitProofByPoints', () => {
    const spy = vi.spyOn(appStore, 'exitProofByPoints');
    const btn = handle.root.querySelector('.proof-back-btn') as HTMLButtonElement;
    btn.click();
    expect(spy).toHaveBeenCalledOnce();
  });

  // predicate buttons are the primary controls for choosing what to prove
  it('renders predicate buttons for visible goal predicates', () => {
    const buttons = handle.root.querySelectorAll('.goal-pred-btn');
    expect(buttons.length).toBeGreaterThan(0);
  });

  // hidden predicates must stay out of the grid to keep the UI uncluttered
  it('does not render hidden predicates in the grid', () => {
    const labels = Array.from(handle.root.querySelectorAll('.goal-pred-label')).map(
      (el) => el.textContent,
    );
    expect(labels).not.toContain('Obtuse Angle');
  });

  // destroy must unsubscribe so the panel no longer reacts after removal
  it('destroy unsubscribes so the panel no longer re-renders on store changes', () => {
    handle.destroy();
    const snapshot = handle.root.innerHTML;
    appStore.enterProofByPoints();
    expect(handle.root.innerHTML).toBe(snapshot);
  });
});
