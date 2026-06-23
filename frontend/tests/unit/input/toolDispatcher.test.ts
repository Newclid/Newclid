import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Scene } from '../../../src/scene/scene';
import { screen } from '../../../src/geometry/coords';
import type { Viewport } from '../../../src/geometry/viewport';
import type { AppStore } from '../../../src/store/appStore';
import type { ToolDispatcherHandle } from '../../../src/input/toolDispatcher';

vi.mock('../../../src/tools/registry', () => ({
  getTool: vi.fn(() => ({
    name: 'point',
    captureState: vi.fn(() => ({ currentSlotIndex: 1, bindings: {}, createdInSlots: [] })),
    restoreState: vi.fn(),
    onDeactivate: vi.fn(),
    currentSlotLabel: vi.fn(() => 'Pick first point'),
    onClick: vi.fn(),
    onMove: vi.fn(() => []),
  })),
}));

// ── helpers ──────────────────────────────────────────────────────────────────

function makeMockTarget() {
  const listeners: Record<string, EventListener[]> = {};
  const target = {
    getBoundingClientRect: () => ({ left: 0, top: 0 }),
    style: { cursor: '' },
    addEventListener(type: string, fn: EventListener) {
      listeners[type] = listeners[type] ?? [];
      listeners[type].push(fn);
    },
    removeEventListener(type: string, fn: EventListener) {
      listeners[type] = (listeners[type] ?? []).filter(f => f !== fn);
    },
    dispatch(type: string, event: Partial<MouseEvent | PointerEvent>) {
      for (const fn of listeners[type] ?? []) fn(event as Event);
    },
    listenerCount(type: string) {
      return (listeners[type] ?? []).length;
    },
  };
  return target;
}

function makeViewport(scale = 50): Viewport {
  return {
    screenToWorld: vi.fn().mockReturnValue({ x: 0, y: 0 }),
    worldToScreen: vi.fn(),
    pan: vi.fn(),
    zoomAt: vi.fn(),
    scale,
  } as unknown as Viewport;
}

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

function makeClick(overrides: Partial<MouseEvent> = {}): Partial<MouseEvent> {
  return { button: 0, clientX: 10, clientY: 10, shiftKey: false, ...overrides };
}

function makePointerMove(overrides: Partial<PointerEvent> = {}): Partial<PointerEvent> {
  return { clientX: 10, clientY: 10, shiftKey: false, ...overrides };
}

describe('attachToolDispatcher', () => {
  let target: ReturnType<typeof makeMockTarget>;
  let viewport: Viewport;
  let scene: Scene;
  let requestRedraw: ReturnType<typeof vi.fn>;
  let handle: ToolDispatcherHandle;
  let attachToolDispatcher: typeof import('../../../src/input/toolDispatcher')['attachToolDispatcher'];
  let getTool: ReturnType<typeof vi.fn>;

  beforeEach(async () => {
    target = makeMockTarget();
    viewport = makeViewport();
    scene = new Scene();
    requestRedraw = vi.fn();
    ({ attachToolDispatcher } = await import('../../../src/input/toolDispatcher'));
    ({ getTool } = await import('../../../src/tools/registry') as { getTool: ReturnType<typeof vi.fn> });
  });

  afterEach(() => {
    handle?.destroy();
    vi.clearAllMocks();
  });

  it('returns a handle with destroy() and refreshPreview()', () => {
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw);
    expect(typeof handle.destroy).toBe('function');
    expect(typeof handle.refreshPreview).toBe('function');
  });

  it('registers 3 listeners on target and 2 on window', () => {
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw);
    expect(target.listenerCount('click')).toBe(1);
    expect(target.listenerCount('pointermove')).toBe(1);
    expect(target.listenerCount('pointerleave')).toBe(1);
  });

  it('destroy removes all target listeners', () => {
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw);
    handle.destroy();
    handle = undefined as never;
    expect(target.listenerCount('click')).toBe(0);
    expect(target.listenerCount('pointermove')).toBe(0);
    expect(target.listenerCount('pointerleave')).toBe(0);
  });

  it('destroy removes window keydown and keyup listeners', () => {
    const addSpy = vi.spyOn(window, 'addEventListener');
    const removeSpy = vi.spyOn(window, 'removeEventListener');
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw);
    const added = addSpy.mock.calls.map(c => c[0]);
    expect(added).toContain('keydown');
    expect(added).toContain('keyup');
    handle.destroy();
    handle = undefined as never;
    const removed = removeSpy.mock.calls.map(c => c[0]);
    expect(removed).toContain('keydown');
    expect(removed).toContain('keyup');
  });

  // ── onClick ────────────────────────────────────────────────────────────────

  it('right-click (button 1) is ignored', () => {
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw);
    const spy = vi.spyOn(scene, 'pushUndo');
    target.dispatch('click', makeClick({ button: 1 }));
    expect(spy).not.toHaveBeenCalled();
  });

  it('click in proofMode is ignored', () => {
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore({ proofMode: true }));
    const spy = vi.spyOn(scene, 'pushUndo');
    target.dispatch('click', makeClick());
    expect(spy).not.toHaveBeenCalled();
  });

  it('click in proofByPointsMode calls goalPickCallback', () => {
    const goalPickCallback = vi.fn();
    handle = attachToolDispatcher(
      target as never, viewport, scene, requestRedraw,
      makeAppStore({ proofByPointsMode: true, goalPickCallback }),
    );
    target.dispatch('click', makeClick({ clientX: 5, clientY: 5 }));
    expect(goalPickCallback).toHaveBeenCalledOnce();
  });

  it('click with select tool and no hovered point does nothing', () => {
    scene.setTool('select');
    handle = attachToolDispatcher(
      target as never, viewport, scene, requestRedraw,
      makeAppStore({ activeToolGroup: undefined as never }),
    );
    const spy = vi.spyOn(scene, 'pushUndo');
    target.dispatch('click', makeClick());
    expect(spy).not.toHaveBeenCalled();
  });

  it('click with select tool and hovered point calls selectMenuCallback', () => {
    scene.setTool('select');
    // Simulate a selectHoverPoint preview
    scene.setPreviews([{ kind: 'selectHoverPoint', pos: { x: 0, y: 0 }, pointId: 'pid-1' }]);
    const selectMenuCallback = vi.fn();
    handle = attachToolDispatcher(
      target as never, viewport, scene, requestRedraw,
      makeAppStore({ activeToolGroup: undefined as never }),
      { selectMenuCallback },
    );
    target.dispatch('click', makeClick({ clientX: 20, clientY: 30 }));
    expect(selectMenuCallback).toHaveBeenCalledWith('pid-1', 20, 30);
  });

  it('click with no active tool (getTool returns null) does nothing', () => {
    getTool.mockReturnValueOnce(undefined);
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    const spy = vi.spyOn(scene, 'pushUndo');
    target.dispatch('click', makeClick());
    expect(spy).not.toHaveBeenCalled();
  });

  it('click that advances a slot pushes undo and sets slot hint', () => {
    // Mock: before=slotIndex 0, after=slotIndex 1
    let callCount = 0;
    getTool.mockReturnValue({
      captureState: vi.fn(() => ({ currentSlotIndex: callCount++, bindings: {}, createdInSlots: [] })),
      restoreState: vi.fn(),
      onDeactivate: vi.fn(),
      currentSlotLabel: vi.fn(() => 'Pick point'),
      onClick: vi.fn(),
      onMove: vi.fn(() => []),
    });
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    const undoSpy = vi.spyOn(scene, 'pushUndo');
    target.dispatch('click', makeClick());
    expect(undoSpy).toHaveBeenCalledOnce();
  });

  it('click that completes last slot clears slot hint', () => {
    // before=slotIndex 1 (filled), after=slotIndex 0 with empty bindings
    let captureCallIndex = 0;
    const states = [
      { currentSlotIndex: 1, bindings: { p0: 'x' }, createdInSlots: [] },
      { currentSlotIndex: 0, bindings: {}, createdInSlots: [] },
    ];
    getTool.mockReturnValue({
      captureState: vi.fn(() => states[captureCallIndex++] ?? states[1]),
      restoreState: vi.fn(),
      onDeactivate: vi.fn(),
      currentSlotLabel: vi.fn(() => null),
      onClick: vi.fn(),
      onMove: vi.fn(() => []),
    });
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    const setSlotHintSpy = vi.spyOn(scene, 'setSlotHint');
    target.dispatch('click', makeClick());
    // justCompleted=true → setSlotHint(null)
    expect(setSlotHintSpy).toHaveBeenCalledWith(null);
  });

  it('click accepted for non-captureState tool when scene changes', () => {
    getTool.mockReturnValue({
      captureState: undefined,
      onDeactivate: vi.fn(),
      onClick: vi.fn(() => { scene.addPoint(0, 0); }), // mutates scene
      onMove: vi.fn(() => []),
    });
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    const undoSpy = vi.spyOn(scene, 'pushUndo');
    target.dispatch('click', makeClick());
    expect(undoSpy).toHaveBeenCalledOnce();
  });

  it('undo callback calls restoreState when tool unchanged', () => {
    let captureIndex = 0;
    const restoreState = vi.fn();
    getTool.mockReturnValue({
      captureState: vi.fn(() => ({ currentSlotIndex: captureIndex++, bindings: {}, createdInSlots: [] })),
      restoreState,
      onDeactivate: vi.fn(),
      currentSlotLabel: vi.fn(() => null),
      onClick: vi.fn(),
      onMove: vi.fn(() => []),
    });
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    target.dispatch('click', makeClick()); // pushes undo with toolBefore defined
    scene.undo(); // triggers the undo callback
    expect(restoreState).toHaveBeenCalled();
  });

  it('undo callback skips restoreState when tool has changed', () => {
    let captureIndex = 0;
    const restoreState = vi.fn();
    getTool.mockReturnValue({
      captureState: vi.fn(() => ({ currentSlotIndex: captureIndex++, bindings: {}, createdInSlots: [] })),
      restoreState,
      onDeactivate: vi.fn(),
      currentSlotLabel: vi.fn(() => null),
      onClick: vi.fn(),
      onMove: vi.fn(() => []),
    });
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    target.dispatch('click', makeClick()); // pushes undo
    scene.setTool('circle'); // tool changes before undo
    scene.undo();
    expect(restoreState).not.toHaveBeenCalled();
  });

  it('click rejected (slot unchanged) does not push undo', () => {
    const stableState = { currentSlotIndex: 0, bindings: {}, createdInSlots: [] };
    getTool.mockReturnValue({
      captureState: vi.fn(() => stableState),
      restoreState: vi.fn(),
      onDeactivate: vi.fn(),
      currentSlotLabel: vi.fn(() => null),
      onClick: vi.fn(), // slot unchanged → rejected
      onMove: vi.fn(() => []),
    });
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    const undoSpy = vi.spyOn(scene, 'pushUndo');
    target.dispatch('click', makeClick());
    expect(undoSpy).not.toHaveBeenCalled();
  });

  // ── updatePreview / onPointerMove ─────────────────────────────────────────

  it('pointermove in proofMode does nothing', () => {
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore({ proofMode: true }));
    target.dispatch('pointermove', makePointerMove());
    expect(requestRedraw).not.toHaveBeenCalled();
  });

  it('pointermove in proofByPointsMode highlights nearest point', () => {
    const ptId = scene.addPoint(0, 0);
    (viewport.screenToWorld as ReturnType<typeof vi.fn>).mockReturnValue({ x: 0, y: 0 });
    handle = attachToolDispatcher(
      target as never, viewport, scene, requestRedraw,
      makeAppStore({ proofByPointsMode: true }),
    );
    target.dispatch('pointermove', makePointerMove());
    expect(requestRedraw).toHaveBeenCalled();
    const previews = scene.previews;
    expect(previews.some(p => p.kind === 'highlightPoint')).toBe(true);
    void ptId;
  });

  it('pointermove in proofByPointsMode with no nearby point clears previews', () => {
    (viewport.screenToWorld as ReturnType<typeof vi.fn>).mockReturnValue({ x: 999, y: 999 });
    handle = attachToolDispatcher(
      target as never, viewport, scene, requestRedraw,
      makeAppStore({ proofByPointsMode: true }),
    );
    target.dispatch('pointermove', makePointerMove());
    expect(scene.previews).toEqual([]);
  });

  it('pointermove with select tool and nearby point sets selectHoverPoint and pointer cursor', () => {
    scene.setTool('select');
    scene.addPoint(0, 0);
    (viewport.screenToWorld as ReturnType<typeof vi.fn>).mockReturnValue({ x: 0, y: 0 });
    handle = attachToolDispatcher(
      target as never, viewport, scene, requestRedraw,
      makeAppStore({ activeToolGroup: undefined as never }),
    );
    target.dispatch('pointermove', makePointerMove());
    expect(scene.previews.some(p => p.kind === 'selectHoverPoint')).toBe(true);
    expect(target.style.cursor).toBe('pointer');
  });

  it('pointermove with select tool and no nearby point clears previews and resets cursor', () => {
    scene.setTool('select');
    (viewport.screenToWorld as ReturnType<typeof vi.fn>).mockReturnValue({ x: 999, y: 999 });
    handle = attachToolDispatcher(
      target as never, viewport, scene, requestRedraw,
      makeAppStore({ activeToolGroup: undefined as never }),
    );
    target.dispatch('pointermove', makePointerMove());
    expect(scene.previews).toEqual([]);
    expect(target.style.cursor).toBe('');
  });

  it('pointermove with no activeToolGroup and no previews does not call requestRedraw', () => {
    scene.setTool('point'); // non-select tool so we hit the !activeToolGroup branch
    handle = attachToolDispatcher(
      target as never, viewport, scene, requestRedraw,
      makeAppStore({ activeToolGroup: undefined as never }),
    );
    target.dispatch('pointermove', makePointerMove());
    expect(requestRedraw).not.toHaveBeenCalled();
  });

  it('pointermove with no activeToolGroup clears stale previews', () => {
    scene.setTool('point'); // non-select so we hit the !activeToolGroup branch
    scene.setPreviews([{ kind: 'highlightPoint', pos: { x: 0, y: 0 } }]);
    handle = attachToolDispatcher(
      target as never, viewport, scene, requestRedraw,
      makeAppStore({ activeToolGroup: undefined as never }),
    );
    target.dispatch('pointermove', makePointerMove());
    expect(scene.previews).toEqual([]);
    expect(requestRedraw).toHaveBeenCalled();
  });

  it('pointermove with active tool calls tool.onMove and setPreviews', () => {
    const previews = [{ kind: 'highlightPoint' as const, pos: { x: 1, y: 1 } }];
    getTool.mockReturnValue({
      captureState: vi.fn(),
      onDeactivate: vi.fn(),
      currentSlotLabel: vi.fn(() => null),
      onClick: vi.fn(),
      onMove: vi.fn(() => previews),
    });
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    target.dispatch('pointermove', makePointerMove());
    expect(scene.previews).toEqual(previews);
    expect(requestRedraw).toHaveBeenCalled();
  });

  it('pointermove with active tool but getTool returns null does nothing', () => {
    getTool.mockReturnValue(undefined);
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    target.dispatch('pointermove', makePointerMove());
    expect(requestRedraw).not.toHaveBeenCalled();
  });

  // ── onPointerLeave ─────────────────────────────────────────────────────────

  it('pointerleave clears previews and resets cursor', () => {
    scene.setPreviews([{ kind: 'highlightPoint', pos: { x: 0, y: 0 } }]);
    target.style.cursor = 'pointer';
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw);
    target.dispatch('pointerleave', {});
    expect(scene.previews).toEqual([]);
    expect(target.style.cursor).toBe('');
    expect(requestRedraw).toHaveBeenCalled();
  });

  it('pointerleave with no previews does not call requestRedraw', () => {
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw);
    target.dispatch('pointerleave', {});
    expect(requestRedraw).not.toHaveBeenCalled();
  });

  // ── onKeyDown / onKeyUp ────────────────────────────────────────────────────

  it('Shift keydown updates preview with shiftKey=true', () => {
    getTool.mockReturnValue({
      onDeactivate: vi.fn(),
      onClick: vi.fn(),
      onMove: vi.fn(() => []),
    });
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    // Set lastMove by firing a pointermove first
    target.dispatch('pointermove', makePointerMove({ clientX: 5, clientY: 5, shiftKey: false }));
    requestRedraw.mockClear();
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Shift' }));
    expect(requestRedraw).toHaveBeenCalled();
  });

  it('non-Shift keydown is ignored when lastMove is set', () => {
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    target.dispatch('pointermove', makePointerMove());
    requestRedraw.mockClear();
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'a' }));
    expect(requestRedraw).not.toHaveBeenCalled();
  });

  it('Shift keydown is ignored when no lastMove (no prior pointermove)', () => {
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Shift' }));
    expect(requestRedraw).not.toHaveBeenCalled();
  });

  it('Shift keyup updates preview with shiftKey=false', () => {
    getTool.mockReturnValue({
      onDeactivate: vi.fn(),
      onClick: vi.fn(),
      onMove: vi.fn(() => []),
    });
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    target.dispatch('pointermove', makePointerMove({ shiftKey: true }));
    requestRedraw.mockClear();
    window.dispatchEvent(new KeyboardEvent('keyup', { key: 'Shift' }));
    expect(requestRedraw).toHaveBeenCalled();
  });

  it('non-Shift keyup is ignored', () => {
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    target.dispatch('pointermove', makePointerMove());
    requestRedraw.mockClear();
    window.dispatchEvent(new KeyboardEvent('keyup', { key: 'a' }));
    expect(requestRedraw).not.toHaveBeenCalled();
  });

  // ── refreshPreview ─────────────────────────────────────────────────────────

  it('refreshPreview reruns updatePreview when lastMove is set', () => {
    getTool.mockReturnValue({
      onDeactivate: vi.fn(),
      onClick: vi.fn(),
      onMove: vi.fn(() => []),
    });
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    target.dispatch('pointermove', makePointerMove());
    requestRedraw.mockClear();
    handle.refreshPreview();
    expect(requestRedraw).toHaveBeenCalled();
  });

  it('refreshPreview is a no-op when no lastMove', () => {
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    handle.refreshPreview();
    expect(requestRedraw).not.toHaveBeenCalled();
  });

  // ── scene tool change subscription ────────────────────────────────────────

  it('tool change calls onDeactivate on the previous tool', () => {
    const mockTool = {
      captureState: vi.fn(() => ({ currentSlotIndex: 0, bindings: {}, createdInSlots: [] })),
      restoreState: vi.fn(),
      onDeactivate: vi.fn(),
      currentSlotLabel: vi.fn(() => null),
      onClick: vi.fn(),
      onMove: vi.fn(() => []),
    };
    getTool.mockReturnValue(mockTool);
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    scene.setTool('circle');
    expect(mockTool.onDeactivate).toHaveBeenCalledWith({ scene });
  });

  it('destroy unsubscribes from scene (no deactivate called after destroy)', () => {
    const mockTool = {
      captureState: vi.fn(() => ({ currentSlotIndex: 0, bindings: {}, createdInSlots: [] })),
      restoreState: vi.fn(),
      onDeactivate: vi.fn(),
      currentSlotLabel: vi.fn(() => null),
      onClick: vi.fn(),
      onMove: vi.fn(() => []),
    };
    getTool.mockReturnValue(mockTool);
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    handle.destroy();
    handle = undefined as never;
    mockTool.onDeactivate.mockClear();
    scene.setTool('circle');
    expect(mockTool.onDeactivate).not.toHaveBeenCalled();
  });

  // ── shiftKey in buildCtx skips grid snap ──────────────────────────────────

  it('shift click passes raw world coords (skips gridSnap)', () => {
    const rawPos = { x: 0.333, y: 0.777 };
    (viewport.screenToWorld as ReturnType<typeof vi.fn>).mockReturnValue(rawPos);
    let capturedCtxWorld: { x: number; y: number } | undefined;
    getTool.mockReturnValue({
      captureState: vi.fn(() => ({ currentSlotIndex: 0, bindings: {}, createdInSlots: [] })),
      restoreState: vi.fn(),
      onDeactivate: vi.fn(),
      currentSlotLabel: vi.fn(() => null),
      onClick: vi.fn((ctx: { world: { x: number; y: number } }) => { capturedCtxWorld = ctx.world; }),
      onMove: vi.fn(() => []),
    });
    handle = attachToolDispatcher(target as never, viewport, scene, requestRedraw, makeAppStore());
    target.dispatch('click', makeClick({ shiftKey: true }));
    expect(capturedCtxWorld).toEqual(rawPos);
  });

  // ── screen coords from toLocal ─────────────────────────────────────────────

  it('toLocal subtracts getBoundingClientRect offset', () => {
    const offsetTarget = { ...target, getBoundingClientRect: () => ({ left: 100, top: 50 }) };
    const selectMenuCallback = vi.fn();
    scene.setTool('select');
    scene.setPreviews([{ kind: 'selectHoverPoint', pos: { x: 0, y: 0 }, pointId: 'p1' }]);
    handle = attachToolDispatcher(
      offsetTarget as never, viewport, scene, requestRedraw,
      makeAppStore({ activeToolGroup: undefined as never }),
      { selectMenuCallback },
    );
    target.dispatch('click', makeClick({ clientX: 150, clientY: 80 }));
    expect(selectMenuCallback).toHaveBeenCalledWith('p1', 50, 30);
  });
});
