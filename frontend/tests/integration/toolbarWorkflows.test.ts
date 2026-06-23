import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Scene } from '../../src/scene/scene';
import { AppStore } from '../../src/store/appStore';
import { attachShortcuts } from '../../src/input/shortcuts';
import { getTool } from '../../src/tools/registry';
import { ConstructionTool } from '../../src/tools/construction-tool';
import { TheoremStore } from '../../src/store/theoremStore';
import { createToolbar } from '../../src/ui/toolbar';

// Mock child panel factories so the toolbar can be created without side effects
// from proof/theorem panel DOM setup.
vi.mock('../../src/ui/proofPanel', () => ({
  createProofPanel: vi.fn(() => ({ root: document.createElement('div'), destroy: vi.fn() })),
}));
vi.mock('../../src/ui/proofsList', () => ({
  createProofsList: vi.fn(() => ({ root: document.createElement('div'), destroy: vi.fn() })),
}));
vi.mock('../../src/ui/proofByPointsPanel', () => ({
  createProofByPointsPanel: vi.fn(() => ({ root: document.createElement('div'), destroy: vi.fn() })),
}));
vi.mock('../../src/ui/theoremManager', () => ({
  createTheoremManager: vi.fn(() => ({ root: document.createElement('div'), destroy: vi.fn() })),
}));
vi.mock('../../src/ui/jgexInput', () => ({
  createJgexInput: vi.fn(() => ({
    root: document.createElement('div'),
    open: vi.fn(),
    close: vi.fn(),
    destroy: vi.fn(),
  })),
}));

function fireKey(key: string, extra: Partial<KeyboardEventInit> = {}): void {
  window.dispatchEvent(new KeyboardEvent('keydown', { key, bubbles: true, ...extra }));
}

describe('toolbar and editing workflows', () => {
  describe('select a construction tool through the toolbar', () => {
    let scene: Scene;
    let appStore: AppStore;

    beforeEach(() => {
      scene = new Scene();
      appStore = new AppStore();
    });

    afterEach(() => {
      document.body.innerHTML = '';
    });

    it('clicking the Point button sets scene.tool to point', () => {
      const toolbar = createToolbar(scene, undefined, appStore);
      document.body.appendChild(toolbar.root);

      // The toolbar renders group buttons initially; click "Points" group to expand it
      const groupBtn = toolbar.root.querySelector<HTMLButtonElement>('[title="Points"]');
      expect(groupBtn).not.toBeNull();
      groupBtn!.click();

      // Filtered view now shows individual tool buttons
      const btn = toolbar.root.querySelector<HTMLButtonElement>('[title="Point (P)"]');
      expect(btn).not.toBeNull();
      btn!.click();

      expect(scene.tool).toBe('point');
      toolbar.destroy();
    });
  });

  describe('select a tool via keyboard shortcut', () => {
    let scene: Scene;
    let appStore: AppStore;

    beforeEach(() => {
      scene = new Scene();
      appStore = new AppStore();
    });

    it('pressing P switches scene.tool to point', () => {
      const handle = attachShortcuts(scene, appStore);
      scene.setTool('select');

      fireKey('p');

      expect(scene.tool).toBe('point');
      handle.destroy();
    });
  });

  describe('ignore shortcuts while typing in an input', () => {
    let scene: Scene;
    let appStore: AppStore;

    beforeEach(() => {
      scene = new Scene();
      appStore = new AppStore();
    });

    afterEach(() => {
      document.body.innerHTML = '';
    });

    it('does not change tool when a keydown fires from an INPUT element', () => {
      const handle = attachShortcuts(scene, appStore);
      scene.setTool('select');

      const input = document.createElement('input');
      document.body.appendChild(input);
      // Dispatch on the input so e.target is the input; shortcuts.ts guards on tagName
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'p', bubbles: true }));

      expect(scene.tool).toBe('select');
      handle.destroy();
    });
  });

  describe('cancel a tool with Escape', () => {
    let scene: Scene;
    let appStore: AppStore;

    beforeEach(() => {
      scene = new Scene();
      appStore = new AppStore();
    });

    it('Escape undoes the filled slot and resets the tool state', () => {
      const handle = attachShortcuts(scene, appStore);
      scene.setTool('line');

      const tool = getTool('line') as ConstructionTool;
      const slotZero = tool.captureState();

      // Simulate one slot filled: add a point and push an undo entry that
      // restores the tool to its pre-fill state when popped.
      const before = scene.snapshot();
      scene.addPoint(0, 0);
      tool.restoreState({ ...slotZero, currentSlotIndex: 1 });
      scene.pushUndo(before, () => tool.restoreState(slotZero));

      expect(tool.captureState().currentSlotIndex).toBe(1);
      expect(scene.objects.size).toBe(1);

      fireKey('Escape');

      expect(scene.objects.size).toBe(0);
      expect(tool.captureState().currentSlotIndex).toBe(0);
      handle.destroy();
    });
  });

  describe('switch between editing, proof, and theorem modes', () => {
    let scene: Scene;
    let appStore: AppStore;

    beforeEach(() => {
      scene = new Scene();
      appStore = new AppStore();
    });

    it('enterProofMode sets proofMode and clears activeToolGroup', () => {
      appStore.setActiveToolGroup('lines');
      appStore.enterProofMode();

      expect(appStore.proofMode).toBe(true);
      expect(appStore.theoremManagerMode).toBe(false);
      expect(appStore.activeToolGroup).toBeNull();
    });

    it('exitProofMode clears proofMode and sets panelTab to proofs', () => {
      appStore.enterProofMode();
      appStore.exitProofMode();

      expect(appStore.proofMode).toBe(false);
      expect(appStore.panelTab).toBe('proofs');
    });

    it('enterTheoremManager is exclusive with proof mode', () => {
      appStore.enterProofMode();
      appStore.enterTheoremManager();

      expect(appStore.theoremManagerMode).toBe(true);
      expect(appStore.proofMode).toBe(false);
    });

    it('shortcuts are suppressed while in theorem manager mode', () => {
      const handle = attachShortcuts(scene, appStore);
      scene.setTool('select');
      appStore.enterTheoremManager();

      fireKey('p');

      expect(scene.tool).toBe('select');
      handle.destroy();
    });

    it('shortcuts are suppressed while in proof mode', () => {
      const handle = attachShortcuts(scene, appStore);
      scene.setTool('select');
      appStore.enterProofMode();

      fireKey('p');

      expect(scene.tool).toBe('select');
      handle.destroy();
    });
  });

  describe('custom theorem lifecycle', () => {
    const THEOREM_BASE = {
      id: 'th1',
      name: 'MyTheorem',
      description: 'test theorem',
      premises: [{ predicateId: 'coll', args: ['A', 'B', 'C'] }],
      conclusions: [{ predicateId: 'perp', args: ['A', 'B', 'C', 'D'] }],
    };

    it('save creates a new theorem retrievable by id', () => {
      const store = new TheoremStore();
      store.save(THEOREM_BASE);

      expect(store.has('th1')).toBe(true);
      expect(store.getById('th1')?.name).toBe('MyTheorem');
    });

    it('save with same id updates the theorem', () => {
      const store = new TheoremStore();
      store.save(THEOREM_BASE);
      store.save({ ...THEOREM_BASE, name: 'Updated' });

      expect(store.getAll()).toHaveLength(1);
      expect(store.getById('th1')?.name).toBe('Updated');
    });

    it('remove deletes the theorem from the store', () => {
      const store = new TheoremStore();
      store.save(THEOREM_BASE);
      store.remove('th1');

      expect(store.has('th1')).toBe(false);
      expect(store.getAll()).toHaveLength(0);
    });

    it('subscribe listener fires on save and remove', () => {
      const store = new TheoremStore();
      const listener = vi.fn();
      const unsub = store.subscribe(listener);

      store.save(THEOREM_BASE);
      expect(listener).toHaveBeenCalledTimes(1);

      store.remove('th1');
      expect(listener).toHaveBeenCalledTimes(2);

      unsub();
      store.save(THEOREM_BASE);
      expect(listener).toHaveBeenCalledTimes(2); // no more calls after unsub
    });
  });

  describe('reload saved theorems from localStorage', () => {
    const THEOREM = {
      id: 'persisted',
      name: 'Persisted',
      description: '',
      premises: [{ predicateId: 'coll', args: ['A', 'B', 'C'] }],
      conclusions: [{ predicateId: 'perp', args: ['A', 'B', 'C', 'D'] }],
    };

    it('a new TheoremStore instance loads theorems persisted by a prior instance', () => {
      const store1 = new TheoremStore();
      store1.save(THEOREM);

      // Simulate app restart: create a fresh TheoremStore that reads from localStorage
      const store2 = new TheoremStore();
      expect(store2.has('persisted')).toBe(true);
      expect(store2.getById('persisted')?.name).toBe('Persisted');
    });

    it('localStorage contains the theorem under the expected key', () => {
      const store = new TheoremStore();
      store.save(THEOREM);

      const raw = localStorage.getItem('newclid_custom_theorems_v1');
      expect(raw).not.toBeNull();
      const parsed = JSON.parse(raw!) as { id: string }[];
      expect(parsed.some(t => t.id === 'persisted')).toBe(true);
    });
  });

  describe('clear the scene and return to initial editing state', () => {
    it('scene.clear() removes all objects and resets undo history', () => {
      const scene = new Scene();
      scene.addPoint(0, 0);
      scene.addPoint(1, 0);
      expect(scene.objects.size).toBe(2);

      const before = scene.snapshot();
      scene.pushUndo(before);
      scene.clear();

      expect(scene.objects.size).toBe(0);
      // Undo stack is cleared; a further undo is a no-op
      scene.undo();
      expect(scene.objects.size).toBe(0);
    });
  });
});
