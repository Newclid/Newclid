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

  describe('proofSketch setter', () => {
    // hiding the canvas when there is no sketch keeps it from blocking pointer events on the SVG
    it('hides the canvas when set to null', () => {
      const canvas = container.querySelector('canvas') as HTMLCanvasElement;
      renderer.proofSketch = null;
      expect(canvas.style.display).toBe('none');
    });

    // the canvas must become visible so the proof sketch overlay is actually rendered
    it('shows the canvas when a sketch is assigned', () => {
      const canvas = container.querySelector('canvas') as HTMLCanvasElement;
      renderer.proofSketch = { points: [], geometry: [] };
      expect(canvas.style.display).toBe('block');
    });

    // drawing the same segment twice would render it twice on top of itself, wasting work
    it('deduplicates duplicate entries in sketch.geometry', () => {
      const seg = { kind: 'segment' as const, p1: 'A', p2: 'B' };
      renderer.proofSketch = { points: [], geometry: [seg, seg] };
      expect(renderer.proofSketch!.geometry).toHaveLength(1);
    });

    // canvasGeometry and canvasMarkers look up point coords by name so ptMap must be built
    it('builds ptMap keyed by point name from sketch.points', () => {
      const pt = { name: 'A', x: 1, y: 2 };
      renderer.proofSketch = { points: [pt], geometry: [] };
      expect(renderer.proofSketch!.ptMap!.get('A')).toBe(pt);
    });

    // perp markers precompute their world intersection so draw does not recompute it every frame
    it('caches the intersection point for perp markers when all four named points exist', () => {
      const sketch: ProofSketch = {
        points: [
          { name: 'A', x: 0, y: 1 },
          { name: 'B', x: 0, y: -1 },
          { name: 'C', x: -1, y: 0 },
          { name: 'D', x: 1, y: 0 },
        ],
        geometry: [],
        markers: [{ kind: 'perp', args: ['A', 'B', 'C', 'D'] }],
      };
      renderer.proofSketch = sketch;
      const marker = sketch.markers![0] as any;
      expect(marker._worldPos).not.toBeNull();
      expect(marker._worldPos.x).toBeCloseTo(0);
      expect(marker._worldPos.y).toBeCloseTo(0);
    });

    // missing points mean no intersection can be computed and the marker should be safely skipped
    it('sets _worldPos to null for perp markers with missing point references', () => {
      const sketch: ProofSketch = {
        points: [{ name: 'A', x: 0, y: 1 }],
        geometry: [],
        markers: [{ kind: 'perp', args: ['A', 'B', 'C', 'D'] }],
      };
      renderer.proofSketch = sketch;
      const marker = sketch.markers![0] as any;
      expect(marker._worldPos).toBeNull();
    });
  });

  describe('draw() SVG management', () => {
    // stale elements from a prior draw must be cleared or they accumulate with every redraw
    it('clears all SVG children before redrawing', () => {
      renderer.draw();
      const countAfterFirst = renderer.svg.childNodes.length;
      renderer.draw();
      expect(renderer.svg.childNodes.length).toBe(countAfterFirst);
    });

    // grid lines are the background scaffolding that always exists regardless of scene content
    it('adds SVG line elements for the grid on draw', () => {
      renderer.draw();
      expect(renderer.svg.querySelectorAll('line').length).toBeGreaterThan(0);
    });

    // the vertical axis must appear at the world origin x when that column is on screen
    it('draws a vertical axis line when the origin is horizontally within the viewport', () => {
      renderer.draw();
      const originX = viewport.worldToScreen(world(0, 0)).x;
      const lines = Array.from(renderer.svg.querySelectorAll('line'));
      const axisLine = lines.find(
        (l) =>
          l.getAttribute('x1') === String(originX) &&
          l.getAttribute('x2') === String(originX) &&
          l.getAttribute('stroke') === '#333',
      );
      expect(axisLine).toBeTruthy();
    });

    // the horizontal axis must appear at the world origin y when that row is on screen
    it('draws a horizontal axis line when the origin is vertically within the viewport', () => {
      renderer.draw();
      const originY = viewport.worldToScreen(world(0, 0)).y;
      const lines = Array.from(renderer.svg.querySelectorAll('line'));
      const axisLine = lines.find(
        (l) =>
          l.getAttribute('y1') === String(originY) &&
          l.getAttribute('y2') === String(originY) &&
          l.getAttribute('stroke') === '#333',
      );
      expect(axisLine).toBeTruthy();
    });
  });

  it.skip('placeholder', () => {
    // Tests will be added in subsequent tasks
  });
});
