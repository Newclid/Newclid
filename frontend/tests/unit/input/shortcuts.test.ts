import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Scene } from '../../../src/scene/scene';
import type { AppStore } from '../../../src/store/appStore';
import type { ShortcutsHandle } from '../../../src/input/shortcuts';

// ── static mocks ──────────────────────────────────────────────────────────────

vi.mock('../../../src/tools/registry', () => ({
  getTool: vi.fn(() => ({
    name: 'point',
    captureState: vi.fn(() => ({ currentSlotIndex: 2, bindings: {}, createdInSlots: [] })),
    restoreState: vi.fn(),
    onDeactivate: vi.fn(),
    currentSlotLabel: vi.fn(() => null),
    onClick: vi.fn(),
    onMove: vi.fn(() => []),
  })),
}));

// ── helpers ──────────────────────────────────────────────────────────────────

function makeAppStore(overrides: Partial<AppStore> = {}): AppStore {
  return {
    proofMode: false,
    proofByPointsMode: false,
    theoremManagerMode: false,
    panelTab: 'toolbar',
    activeToolGroup: 'points',
    goalPickCallback: null,
    ...overrides,
  } as unknown as AppStore;
}

function fireKey(key: string, extra: Partial<KeyboardEvent> = {}) {
  window.dispatchEvent(new KeyboardEvent('keydown', { key, bubbles: true, ...extra }));
}

// ── attachShortcuts behaviour ─────────────────────────────────────────────────

describe('attachShortcuts', () => {
  let scene: Scene;
  let handle: ShortcutsHandle;

  // Fresh imports after the collision test's resetModules may have cleared the cache.
  let attachShortcuts: (typeof import('../../../src/input/shortcuts'))['attachShortcuts'];

  beforeEach(async () => {
    scene = new Scene();
    ({ attachShortcuts } = await import('../../../src/input/shortcuts'));
  });

  afterEach(() => {
    handle?.destroy();
    vi.clearAllMocks();
  });

  it('returns a handle with destroy()', () => {
    handle = attachShortcuts(scene);
    expect(typeof handle.destroy).toBe('function');
  });

  it('destroy removes the keydown listener', () => {
    handle = attachShortcuts(scene);
    const undoSpy = vi.spyOn(scene, 'undo');
    handle.destroy();
    handle = undefined as never; // already destroyed
    fireKey('z', { ctrlKey: true });
    expect(undoSpy).not.toHaveBeenCalled();
  });

  it('ignores keydown from INPUT elements', () => {
    handle = attachShortcuts(scene);
    const undoSpy = vi.spyOn(scene, 'undo');
    const input = document.createElement('input');
    document.body.appendChild(input);
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'z', ctrlKey: true, bubbles: true }));
    expect(undoSpy).not.toHaveBeenCalled();
    document.body.removeChild(input);
  });

  it('ignores keydown from TEXTAREA elements', () => {
    handle = attachShortcuts(scene);
    const undoSpy = vi.spyOn(scene, 'undo');
    const ta = document.createElement('textarea');
    document.body.appendChild(ta);
    ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'z', ctrlKey: true, bubbles: true }));
    expect(undoSpy).not.toHaveBeenCalled();
    document.body.removeChild(ta);
  });

  it('Ctrl+Z calls scene.undo() and clears slot hint', () => {
    handle = attachShortcuts(scene);
    const undoSpy = vi.spyOn(scene, 'undo');
    const setSlotHintSpy = vi.spyOn(scene, 'setSlotHint');
    fireKey('z', { ctrlKey: true });
    expect(undoSpy).toHaveBeenCalledOnce();
    expect(setSlotHintSpy).toHaveBeenCalled();
  });

  it('Meta+Z (macOS) calls scene.undo()', () => {
    handle = attachShortcuts(scene);
    const undoSpy = vi.spyOn(scene, 'undo');
    fireKey('z', { metaKey: true });
    expect(undoSpy).toHaveBeenCalledOnce();
  });

  it('Ctrl+Z is ignored in proofMode', () => {
    handle = attachShortcuts(scene, makeAppStore({ proofMode: true }));
    const undoSpy = vi.spyOn(scene, 'undo');
    fireKey('z', { ctrlKey: true });
    expect(undoSpy).not.toHaveBeenCalled();
  });

  it('Escape calls scene.undo() once per filled slot', () => {
    handle = attachShortcuts(scene);
    const undoSpy = vi.spyOn(scene, 'undo');
    const setSlotErrorSpy = vi.spyOn(scene, 'setSlotError');
    fireKey('Escape');
    // getTool mock returns captureState.currentSlotIndex = 2 → undo called twice
    expect(undoSpy).toHaveBeenCalledTimes(2);
    expect(setSlotErrorSpy).toHaveBeenCalledWith(null);
  });

  it('Escape is ignored in proofMode', () => {
    handle = attachShortcuts(scene, makeAppStore({ proofMode: true }));
    const undoSpy = vi.spyOn(scene, 'undo');
    fireKey('Escape');
    expect(undoSpy).not.toHaveBeenCalled();
  });

  it('modifier-only key (ctrlKey + non-Z) falls through to modifier guard and is ignored', () => {
    handle = attachShortcuts(scene);
    const setToolSpy = vi.spyOn(scene, 'setTool');
    fireKey('s', { ctrlKey: true });
    expect(setToolSpy).not.toHaveBeenCalled();
  });

  it('altKey causes early return before tool switching', () => {
    handle = attachShortcuts(scene, makeAppStore());
    const setToolSpy = vi.spyOn(scene, 'setTool');
    fireKey('p', { altKey: true });
    expect(setToolSpy).not.toHaveBeenCalled();
  });

  it('proofMode blocks tool switching shortcuts', () => {
    handle = attachShortcuts(scene, makeAppStore({ proofMode: true }));
    const setToolSpy = vi.spyOn(scene, 'setTool');
    fireKey('p');
    expect(setToolSpy).not.toHaveBeenCalled();
  });

  it('theoremManagerMode blocks tool switching shortcuts', () => {
    handle = attachShortcuts(scene, makeAppStore({ theoremManagerMode: true }));
    const setToolSpy = vi.spyOn(scene, 'setTool');
    fireKey('p');
    expect(setToolSpy).not.toHaveBeenCalled();
  });

  it('panelTab !== toolbar blocks tool switching shortcuts', () => {
    handle = attachShortcuts(scene, makeAppStore({ panelTab: 'proofs' as never }));
    const setToolSpy = vi.spyOn(scene, 'setTool');
    fireKey('p');
    expect(setToolSpy).not.toHaveBeenCalled();
  });

  it('valid shortcut key switches the tool and deactivates the previous one', async () => {
    const { getTool } = await import('../../../src/tools/registry');
    // Capture the mock tool that getTool returns so we can assert on its methods
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const capturedTools: any[] = [];
    (getTool as ReturnType<typeof vi.fn>).mockImplementation(() => {
      const t = {
        name: 'point',
        captureState: vi.fn(() => ({ currentSlotIndex: 2, bindings: {}, createdInSlots: [] })),
        restoreState: vi.fn(),
        onDeactivate: vi.fn(),
        currentSlotLabel: vi.fn(() => null),
        onClick: vi.fn(),
        onMove: vi.fn(() => []),
      };
      capturedTools.push(t);
      return t;
    });
    handle = attachShortcuts(scene, makeAppStore());
    const setToolSpy = vi.spyOn(scene, 'setTool');
    fireKey('p'); // 'p' → point tool
    expect(setToolSpy).toHaveBeenCalledWith('point');
    // The first getTool call is to get the current tool (to deactivate it)
    expect(capturedTools[0]?.onDeactivate).toHaveBeenCalled();
  });

  it('unknown key does nothing', () => {
    handle = attachShortcuts(scene, makeAppStore());
    const setToolSpy = vi.spyOn(scene, 'setTool');
    fireKey('~'); // no tool has this shortcut
    expect(setToolSpy).not.toHaveBeenCalled();
  });

  it('no appStore passed: Escape still works (no proofMode check crashes)', () => {
    handle = attachShortcuts(scene); // no appStore
    const undoSpy = vi.spyOn(scene, 'undo');
    fireKey('Escape');
    expect(undoSpy).toHaveBeenCalled();
  });

  it('Escape with tool returning undefined currentSlotIndex falls back to 0 (no undo)', async () => {
    const { getTool } = await import('../../../src/tools/registry');
    (getTool as ReturnType<typeof vi.fn>).mockReturnValueOnce({
      captureState: () => ({ currentSlotIndex: undefined }),
      onDeactivate: vi.fn(),
      currentSlotLabel: vi.fn(() => null),
    });
    handle = attachShortcuts(scene);
    const undoSpy = vi.spyOn(scene, 'undo');
    fireKey('Escape');
    expect(undoSpy).not.toHaveBeenCalled();
  });

  it('no appStore passed: tool switching works without crashing', () => {
    handle = attachShortcuts(scene); // no appStore
    // appStore?.panelTab is undefined, which !== 'toolbar' → returns early (no switch)
    // but should not throw
    expect(() => fireKey('p')).not.toThrow();
  });
});
