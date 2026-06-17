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

  describe('constructor', () => {
    // the SVG element is the vector layer where all scene geometry gets painted
    it('appends an SVG element to the container', () => {
      expect(container.querySelector('svg')).toBeTruthy();
    });

    // the SVG must be visible so the geometry is actually seen on screen
    it('sets the SVG to display block', () => {
      const svg = container.querySelector('svg') as SVGSVGElement;
      expect(svg.style.display).toBe('block');
    });

    // the canvas overlay is for proof sketches and must start hidden so it does not block the SVG
    it('appends a canvas element to the container with display none', () => {
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeTruthy();
      expect(canvas!.style.display).toBe('none');
    });

    // resize() is called during construction so the SVG dimensions match the viewport immediately
    it('sets SVG width and height attributes on construction via resize', () => {
      expect(renderer.svg.getAttribute('width')).toBe('800');
      expect(renderer.svg.getAttribute('height')).toBe('600');
    });
  });

  it.skip('placeholder', () => {
    // Tests will be added in subsequent tasks
  });
});
