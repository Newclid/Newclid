import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Renderer, type ProofSketch } from '../../../src/render/renderer';
import { Viewport } from '../../../src/geometry/viewport';
import { Scene } from '../../../src/scene/scene';
import { world } from '../../../src/geometry/coords';

function makeFakeCtx() {
  return {
    setTransform: vi.fn(),
    clearRect: vi.fn(),
    beginPath: vi.fn(),
    stroke: vi.fn(),
    fill: vi.fn(),
    closePath: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    arc: vi.fn(),
    fillText: vi.fn(),
    save: vi.fn(),
    restore: vi.fn(),
    setLineDash: vi.fn(),
    strokeStyle: '',
    lineWidth: 0,
    fillStyle: '',
    font: '',
    globalAlpha: 1,
  };
}

describe('Renderer', () => {
  let container: HTMLDivElement;
  let viewport: Viewport;
  let scene: Scene;
  let renderer: Renderer;
  let fakeCtx: ReturnType<typeof makeFakeCtx>;

  beforeEach(() => {
    container = document.createElement('div');
    viewport = new Viewport();
    viewport.width = 800;
    viewport.height = 600;
    viewport.scale = 50;
    scene = new Scene();
    fakeCtx = makeFakeCtx();
    vi.stubGlobal('devicePixelRatio', 1);
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(fakeCtx as any);
    renderer = new Renderer(container, viewport, scene);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it.skip('placeholder', () => {
    // Tests will be added in subsequent tasks
  });
});
