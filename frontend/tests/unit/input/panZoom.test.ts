import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { attachPanZoom } from '../../../src/input/panZoom';
import { screen } from '../../../src/geometry/coords';
import type { Viewport } from '../../../src/geometry/viewport';

// Minimal mock SVGSVGElement with event listener capture.
function makeMockTarget() {
  const listeners: Record<string, EventListener[]> = {};
  const target = {
    getBoundingClientRect: () => ({ left: 0, top: 0 }),
    setPointerCapture: vi.fn(),
    releasePointerCapture: vi.fn(),
    style: { cursor: '' },
    addEventListener(type: string, fn: EventListener) {
      listeners[type] = listeners[type] ?? [];
      listeners[type].push(fn);
    },
    removeEventListener(type: string, fn: EventListener) {
      listeners[type] = (listeners[type] ?? []).filter(f => f !== fn);
    },
    dispatch(type: string, event: Partial<Event>) {
      for (const fn of listeners[type] ?? []) fn(event as Event);
    },
    listenerCount(type: string) {
      return (listeners[type] ?? []).length;
    },
  };
  return target;
}

function makeViewport(): Viewport {
  return {
    pan: vi.fn(),
    zoomAt: vi.fn(),
    screenToWorld: vi.fn().mockReturnValue({ x: 0, y: 0 }),
    worldToScreen: vi.fn(),
    scale: 50,
  } as unknown as Viewport;
}

function makePointerEvent(type: string, overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    type,
    button: 0,
    pointerId: 1,
    clientX: 10,
    clientY: 20,
    deltaX: 0,
    deltaY: 0,
    ctrlKey: false,
    preventDefault: vi.fn(),
    ...overrides,
  };
}

describe('attachPanZoom', () => {
  let target: ReturnType<typeof makeMockTarget>;
  let viewport: Viewport;
  let onChange: ReturnType<typeof vi.fn<() => void>>;

  beforeEach(() => {
    vi.useFakeTimers();
    target = makeMockTarget();
    viewport = makeViewport();
    onChange = vi.fn<() => void>();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('returns a handle with destroy()', () => {
    const handle = attachPanZoom(target as never, viewport, onChange);
    expect(typeof handle.destroy).toBe('function');
  });

  it('registers 6 event listeners on attach', () => {
    attachPanZoom(target as never, viewport, onChange);
    for (const type of ['pointerdown', 'pointermove', 'pointerup', 'pointercancel', 'wheel', 'contextmenu']) {
      expect(target.listenerCount(type)).toBe(1);
    }
  });

  it('destroy removes all 6 event listeners', () => {
    const handle = attachPanZoom(target as never, viewport, onChange);
    handle.destroy();
    for (const type of ['pointerdown', 'pointermove', 'pointerup', 'pointercancel', 'wheel', 'contextmenu']) {
      expect(target.listenerCount(type)).toBe(0);
    }
  });

  it('left-click (button 0) does not start pan', () => {
    attachPanZoom(target as never, viewport, onChange);
    target.dispatch('pointerdown', makePointerEvent('pointerdown', { button: 0 }));
    target.dispatch('pointermove', makePointerEvent('pointermove', { clientX: 50, clientY: 70 }));
    expect(viewport.pan).not.toHaveBeenCalled();
  });

  it('middle-click (button 1) starts panning', () => {
    attachPanZoom(target as never, viewport, onChange);
    target.dispatch('pointerdown', makePointerEvent('pointerdown', { button: 1, clientX: 10, clientY: 20 }));
    expect(target.setPointerCapture).toHaveBeenCalledWith(1);
    expect(target.style.cursor).toBe('grabbing');
  });

  it('right-click (button 2) starts panning', () => {
    attachPanZoom(target as never, viewport, onChange);
    target.dispatch('pointerdown', makePointerEvent('pointerdown', { button: 2, clientX: 10, clientY: 20 }));
    expect(target.setPointerCapture).toHaveBeenCalledWith(1);
  });

  it('pointermove while panning calls viewport.pan and schedules redraw', () => {
    attachPanZoom(target as never, viewport, onChange);
    target.dispatch('pointerdown', makePointerEvent('pointerdown', { button: 2, clientX: 0, clientY: 0, pointerId: 1 }));
    target.dispatch('pointermove', makePointerEvent('pointermove', { clientX: 30, clientY: 40, pointerId: 1 }));
    expect(viewport.pan).toHaveBeenCalledWith(30, 40);
    // onChange hasn't fired yet — rAF pending
    expect(onChange).not.toHaveBeenCalled();
    vi.runAllTimers();
    expect(onChange).toHaveBeenCalledOnce();
  });

  it('pointermove with wrong pointerId is ignored', () => {
    attachPanZoom(target as never, viewport, onChange);
    target.dispatch('pointerdown', makePointerEvent('pointerdown', { button: 2, pointerId: 1 }));
    target.dispatch('pointermove', makePointerEvent('pointermove', { pointerId: 99, clientX: 50, clientY: 50 }));
    expect(viewport.pan).not.toHaveBeenCalled();
  });

  it('pointermove without active pan is ignored', () => {
    attachPanZoom(target as never, viewport, onChange);
    target.dispatch('pointermove', makePointerEvent('pointermove', { clientX: 50, clientY: 50 }));
    expect(viewport.pan).not.toHaveBeenCalled();
  });

  it('pointerup ends pan and releases pointer capture', () => {
    attachPanZoom(target as never, viewport, onChange);
    target.dispatch('pointerdown', makePointerEvent('pointerdown', { button: 2, pointerId: 1 }));
    target.dispatch('pointerup', makePointerEvent('pointerup', { pointerId: 1 }));
    expect(target.releasePointerCapture).toHaveBeenCalledWith(1);
    expect(target.style.cursor).toBe('');
  });

  it('pointerup with wrong pointerId is ignored', () => {
    attachPanZoom(target as never, viewport, onChange);
    target.dispatch('pointerdown', makePointerEvent('pointerdown', { button: 2, pointerId: 1 }));
    target.dispatch('pointerup', makePointerEvent('pointerup', { pointerId: 99 }));
    expect(target.releasePointerCapture).not.toHaveBeenCalled();
  });

  it('pointercancel ends pan and releases capture', () => {
    attachPanZoom(target as never, viewport, onChange);
    target.dispatch('pointerdown', makePointerEvent('pointerdown', { button: 2, pointerId: 1 }));
    target.dispatch('pointercancel', makePointerEvent('pointercancel', { pointerId: 1 }));
    expect(target.releasePointerCapture).toHaveBeenCalledWith(1);
  });

  it('pointercancel without active pan is ignored', () => {
    attachPanZoom(target as never, viewport, onChange);
    target.dispatch('pointercancel', makePointerEvent('pointercancel', { pointerId: 1 }));
    expect(target.releasePointerCapture).not.toHaveBeenCalled();
  });

  it('Ctrl+wheel calls viewport.zoomAt', () => {
    attachPanZoom(target as never, viewport, onChange);
    const event = { deltaY: 10, deltaX: 0, clientX: 100, clientY: 200, ctrlKey: true, preventDefault: vi.fn() };
    target.dispatch('wheel', event);
    expect(viewport.zoomAt).toHaveBeenCalledOnce();
    const [anchor, factor] = (viewport.zoomAt as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(anchor).toBeDefined();
    expect(factor).toBeCloseTo(Math.exp(-10 * 0.0015));
    vi.runAllTimers();
    expect(onChange).toHaveBeenCalledOnce();
  });

  it('plain wheel (no ctrlKey) calls viewport.pan with negated deltas', () => {
    attachPanZoom(target as never, viewport, onChange);
    const event = { deltaY: 30, deltaX: -10, clientX: 0, clientY: 0, ctrlKey: false, preventDefault: vi.fn() };
    target.dispatch('wheel', event);
    expect(viewport.pan).toHaveBeenCalledWith(10, -30);
    vi.runAllTimers();
    expect(onChange).toHaveBeenCalledOnce();
  });

  it('contextmenu calls preventDefault', () => {
    attachPanZoom(target as never, viewport, onChange);
    const preventDefault = vi.fn();
    target.dispatch('contextmenu', { preventDefault });
    expect(preventDefault).toHaveBeenCalledOnce();
  });

  it('requestRedraw is debounced: second call within same frame is a no-op', () => {
    attachPanZoom(target as never, viewport, onChange);
    // Two wheel events in same frame → onChange should only fire once
    const ev = { deltaY: 10, deltaX: 0, clientX: 0, clientY: 0, ctrlKey: false, preventDefault: vi.fn() };
    target.dispatch('wheel', ev);
    target.dispatch('wheel', ev);
    vi.runAllTimers();
    expect(onChange).toHaveBeenCalledOnce();
  });

  it('requestRedraw fires again after the frame completes', () => {
    attachPanZoom(target as never, viewport, onChange);
    const ev = { deltaY: 5, deltaX: 0, clientX: 0, clientY: 0, ctrlKey: false, preventDefault: vi.fn() };
    target.dispatch('wheel', ev);
    vi.runAllTimers(); // first frame
    expect(onChange).toHaveBeenCalledTimes(1);

    target.dispatch('wheel', ev);
    vi.runAllTimers(); // second frame
    expect(onChange).toHaveBeenCalledTimes(2);
  });

  it('WHEEL_ZOOM_SENSITIVITY is ~0.0015 (equal-and-opposite deltas cancel)', () => {
    attachPanZoom(target as never, viewport, onChange);
    const zoomIn = { deltaY: -100, deltaX: 0, clientX: 0, clientY: 0, ctrlKey: true, preventDefault: vi.fn() };
    const zoomOut = { deltaY: 100, deltaX: 0, clientX: 0, clientY: 0, ctrlKey: true, preventDefault: vi.fn() };
    target.dispatch('wheel', zoomIn);
    target.dispatch('wheel', zoomOut);
    const calls = (viewport.zoomAt as ReturnType<typeof vi.fn>).mock.calls;
    // product of opposite factors should be ~1
    const product = calls[0][1] * calls[1][1];
    expect(product).toBeCloseTo(1);
  });

  // Verify screen coord is used: toLocal offsets by getBoundingClientRect().
  it('toLocal correctly offsets clientX/Y by the bounding rect', () => {
    const offsetTarget = {
      ...target,
      getBoundingClientRect: () => ({ left: 100, top: 50 }),
    };
    attachPanZoom(offsetTarget as never, viewport, onChange);
    // pan start at clientX=120, clientY=80 → local (20, 30)
    offsetTarget.dispatch('pointerdown', makePointerEvent('pointerdown', { button: 2, clientX: 120, clientY: 80, pointerId: 1 }));
    // move to clientX=140, clientY=100 → local (40, 50) → dx=20, dy=20
    offsetTarget.dispatch('pointermove', makePointerEvent('pointermove', { clientX: 140, clientY: 100, pointerId: 1 }));
    expect(viewport.pan).toHaveBeenCalledWith(20, 20);
  });

  // Verify screen is used in zoomAt
  it('toLocal is used for zoom anchor', () => {
    const offsetTarget = {
      ...target,
      getBoundingClientRect: () => ({ left: 50, top: 25 }),
    };
    attachPanZoom(offsetTarget as never, viewport, onChange);
    const event = { deltaY: -10, deltaX: 0, clientX: 150, clientY: 125, ctrlKey: true, preventDefault: vi.fn() };
    offsetTarget.dispatch('wheel', event);
    const [anchor] = (viewport.zoomAt as ReturnType<typeof vi.fn>).mock.calls[0];
    // screen(100, 100) after subtracting left=50, top=25
    expect(anchor).toEqual(screen(100, 100));
  });
});
