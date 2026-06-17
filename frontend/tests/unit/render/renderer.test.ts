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

  describe('resize()', () => {
    // SVG attributes must always reflect the current viewport so layout changes take effect
    it('updates SVG width and height attributes when viewport changes', () => {
      viewport.width = 1024;
      viewport.height = 768;
      renderer.resize();
      expect(renderer.svg.getAttribute('width')).toBe('1024');
      expect(renderer.svg.getAttribute('height')).toBe('768');
    });

    // the canvas pixel buffer must be DPR-scaled so it stays sharp on high-DPI screens
    it('sets canvas pixel dimensions as round(viewport times dpr)', () => {
      vi.stubGlobal('devicePixelRatio', 2);
      viewport.width = 400;
      viewport.height = 300;
      renderer.resize();
      const canvas = container.querySelector('canvas') as HTMLCanvasElement;
      expect(canvas.width).toBe(800);
      expect(canvas.height).toBe(600);
    });

    // the CSS size must match the logical viewport so the canvas does not appear stretched
    it('sets canvas style width and height in px matching viewport logical size', () => {
      viewport.width = 500;
      viewport.height = 400;
      renderer.resize();
      const canvas = container.querySelector('canvas') as HTMLCanvasElement;
      expect(canvas.style.width).toBe('500px');
      expect(canvas.style.height).toBe('400px');
    });
  });

  it.skip('placeholder', () => {
    // Tests will be added in subsequent tasks
  });
});
