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

  describe('draw() points', () => {
    // scene points must appear as dots at their world coordinates so users see where they placed them
    it('renders a point as an SVG circle at the correct screen position', () => {
      scene.addPoint(2, 3);
      renderer.draw();
      const expected = viewport.worldToScreen(world(2, 3));
      const circles = Array.from(renderer.svg.querySelectorAll('circle'));
      const dot = circles.find(
        (c) =>
          c.getAttribute('cx') === String(expected.x) &&
          c.getAttribute('cy') === String(expected.y) &&
          c.getAttribute('r') === '4.25',
      );
      expect(dot).toBeTruthy();
    });

    // point labels are how the user identifies geometry during a proof, so they must render
    it('renders a text label for each scene point', () => {
      scene.addPoint(0, 0);
      renderer.draw();
      const labelEl = Array.from(renderer.svg.querySelectorAll('text')).find(
        (t) => t.textContent === 'A',
      );
      expect(labelEl).toBeTruthy();
    });

    // the color prop lets tools highlight individual points so it must flow through to SVG fill
    it('uses point.color for the dot fill when the color is set', () => {
      const id = scene.addPoint(1, 1);
      scene.setPointColor(id, '#ff0000');
      renderer.draw();
      const expected = viewport.worldToScreen(world(1, 1));
      const dot = Array.from(renderer.svg.querySelectorAll('circle')).find(
        (c) => c.getAttribute('cx') === String(expected.x) && c.getAttribute('fill') === '#ff0000',
      );
      expect(dot).toBeTruthy();
    });

    // without an explicit color the dot should fall back to the renderer default dark ink
    it('uses the default dark fill when point.color is not set', () => {
      scene.addPoint(1, 1);
      renderer.draw();
      const expected = viewport.worldToScreen(world(1, 1));
      const dot = Array.from(renderer.svg.querySelectorAll('circle')).find(
        (c) => c.getAttribute('cx') === String(expected.x) && c.getAttribute('fill') === '#1a1a1a',
      );
      expect(dot).toBeTruthy();
    });
  });

  describe('draw() circle objects', () => {
    // a center-through circle is the primary user-placed circle and must show with the correct stroke
    it('renders a center-through circle as an SVG circle with the correct stroke color', () => {
      const centerId = scene.addPoint(0, 0);
      const throughId = scene.addPoint(3, 0);
      scene.addObject({ kind: 'circle', mode: 'center-through', center: centerId, through: throughId });
      renderer.draw();
      // 3 world units at scale 50 gives 150px radius
      const circleEl = Array.from(renderer.svg.querySelectorAll('circle')).find(
        (c) => c.getAttribute('r') === '150' && c.getAttribute('fill') === 'none',
      );
      expect(circleEl).toBeTruthy();
      expect(circleEl!.getAttribute('stroke')).toBe('#1A1816');
    });

    // a circle referencing deleted or nonexistent points must not crash draw
    it('skips center-through circles when the center or through point is missing', () => {
      scene.addObject({ kind: 'circle', mode: 'center-through', center: 'gone1', through: 'gone2' });
      expect(() => renderer.draw()).not.toThrow();
    });
  });

  describe('draw() construction objects', () => {
    // construction edges are the finite segments that visually define the built shape
    it('renders each construction edge as an SVG line between the two endpoint screen positions', () => {
      const p1 = scene.addPoint(0, 0);
      const p2 = scene.addPoint(1, 0);
      scene.addObject({
        kind: 'construction',
        name: 'test',
        bindings: { a: p1, b: p2 },
        edges: [[p1, p2]],
        circles: [],
      });
      renderer.draw();
      const s1 = viewport.worldToScreen(world(0, 0));
      const s2 = viewport.worldToScreen(world(1, 0));
      const edgeLine = Array.from(renderer.svg.querySelectorAll('line')).find(
        (l) =>
          l.getAttribute('x1') === String(s1.x) &&
          l.getAttribute('y1') === String(s1.y) &&
          l.getAttribute('x2') === String(s2.x) &&
          l.getAttribute('y2') === String(s2.y),
      );
      expect(edgeLine).toBeTruthy();
    });

    // construction circles are drawn with the center point and a precomputed world-space radius
    it('renders construction circles as SVG circle elements with the correct pixel radius', () => {
      const centerId = scene.addPoint(0, 0);
      scene.addObject({
        kind: 'construction',
        name: 'test',
        bindings: { c: centerId },
        edges: [],
        circles: [{ center: centerId, radius: 2 }],
      });
      renderer.draw();
      // 2 world units at scale 50 gives 100px radius
      const circleEl = Array.from(renderer.svg.querySelectorAll('circle')).find(
        (c) => c.getAttribute('r') === '100' && c.getAttribute('fill') === 'none',
      );
      expect(circleEl).toBeTruthy();
    });

    // circumcircles pass through three named points and the renderer must derive the center and radius
    it('renders circumcircles derived from three points as SVG circle elements', () => {
      const p1 = scene.addPoint(0, 1);
      const p2 = scene.addPoint(-1, 0);
      const p3 = scene.addPoint(1, 0);
      scene.addObject({
        kind: 'construction',
        name: 'test',
        bindings: {},
        edges: [],
        circles: [],
        circumcircles: [[p1, p2, p3]],
      });
      renderer.draw();
      const circleEl = Array.from(renderer.svg.querySelectorAll('circle')).find(
        (c) => c.getAttribute('fill') === 'none' && c.getAttribute('stroke') === '#888',
      );
      expect(circleEl).toBeTruthy();
    });
  });

  describe('draw() previews', () => {
    // the snap ring shows which existing point the cursor would snap to on the next click
    it('renders a highlightPoint preview as a circle with the snap stroke color', () => {
      scene.setPreviews([{ kind: 'highlightPoint', pos: { x: 1, y: 1 } }]);
      renderer.draw();
      const expected = viewport.worldToScreen(world(1, 1));
      const ring = Array.from(renderer.svg.querySelectorAll('circle')).find(
        (c) =>
          c.getAttribute('cx') === String(expected.x) &&
          c.getAttribute('r') === '9' &&
          c.getAttribute('stroke') === '#2A4A7F',
      );
      expect(ring).toBeTruthy();
    });

    // the rubber circle shows the circle being sized before the user releases the pointer
    it('renders a rubberCircle preview as a dashed SVG circle with the preview stroke color', () => {
      scene.setPreviews([{ kind: 'rubberCircle', center: { x: 0, y: 0 }, radiusVec: { x: 2, y: 0 } }]);
      renderer.draw();
      // distance from center to radiusVec is 2 world units, 2 * 50 = 100px
      const dashed = Array.from(renderer.svg.querySelectorAll('circle')).find(
        (c) => c.getAttribute('r') === '100' && c.getAttribute('stroke-dasharray') === '5 4',
      );
      expect(dashed).toBeTruthy();
    });

    // an aux line is a helper guide drawn while the tool is computing its next anchor point
    it('renders an auxLine preview as a dashed SVG line element', () => {
      scene.setPreviews([{ kind: 'auxLine', from: { x: 0, y: 0 }, to: { x: 1, y: 0 } }]);
      renderer.draw();
      const dashed = Array.from(renderer.svg.querySelectorAll('line')).find(
        (l) => l.getAttribute('stroke-dasharray') === '5 4',
      );
      expect(dashed).toBeTruthy();
    });

    // a partial edge shows the first confirmed segment of a multi-click construction in progress
    it('renders a partialEdge preview as a solid SVG line at the correct screen coordinates', () => {
      scene.setPreviews([{ kind: 'partialEdge', from: { x: 0, y: 0 }, to: { x: 1, y: 0 } }]);
      renderer.draw();
      const s1 = viewport.worldToScreen(world(0, 0));
      const s2 = viewport.worldToScreen(world(1, 0));
      const solidLine = Array.from(renderer.svg.querySelectorAll('line')).find(
        (l) =>
          l.getAttribute('x1') === String(s1.x) &&
          l.getAttribute('y1') === String(s1.y) &&
          l.getAttribute('x2') === String(s2.x) &&
          l.getAttribute('y2') === String(s2.y) &&
          l.getAttribute('stroke') === '#888' &&
          !l.hasAttribute('stroke-dasharray'),
      );
      expect(solidLine).toBeTruthy();
    });
  });

  it.skip('placeholder', () => {
    // Tests will be added in subsequent tasks
  });
});
