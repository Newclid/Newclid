import { Viewport } from '../geometry/viewport';
import { world, type WorldPoint } from '../geometry/coords';
import { Scene } from '../scene/scene';
import { distance } from '../geometry/primitives';

const SVG_NS = 'http://www.w3.org/2000/svg';

const STYLE = {
  background: '#fafafa',
  gridMinor: '#ececec',  // small grid lines
  gridMajor: '#d0d0d0',  // every 5th line, slightly darker
  axis: '#333',
  axisLabel: '#555',     // numbers next to ticks
  tickLength: 4,         // pixels of tick mark on each side of axis
  fontSize: 11,
  // Stored circles — solid stroke, ink graphite to match points.
  circleStroke: '#1A1816',
  circleStrokeWidth: 1.75,
  // Snap-target ring (drawn around an existing point under the cursor).
  snapStroke: '#2A4A7F',
  // Rubber-band preview circle — dashed, soft grey.
  previewStroke: '#8C887F',
  previewStrokeWidth: 1.5,
  previewDash: '5 4',
};

export class Renderer {
  // Exposed (readonly) so the input layer can attach pointer/wheel
  // listeners. Renderer still owns the element's lifecycle and contents.
  readonly svg: SVGSVGElement;

  constructor(private container: HTMLElement, private viewport: Viewport, private scene: Scene) {
    this.svg = document.createElementNS(SVG_NS, 'svg');
    this.svg.style.background = STYLE.background;
    this.svg.style.display = 'block';
    this.container.appendChild(this.svg);
    this.resize();
  }

  resize(): void {
    this.svg.setAttribute('width', String(this.viewport.width));
    this.svg.setAttribute('height', String(this.viewport.height));
  }

  draw(): void {
    // Clear everything from the previous frame.
    while (this.svg.firstChild) this.svg.removeChild(this.svg.firstChild);

    // SVG paints later elements on top of earlier ones. Order:
    // grid → axes → labels → circles → points → previews.
    // Points stay above circles so the user can grab them through any
    // circle that intersects them; previews float on top so the snap
    // ring is visible even when it's centred on a point.
    this.drawGrid();
    this.drawAxes();
    this.drawAxisLabels();
    this.drawCircles();
    this.drawConstructions();
    this.drawPoints();
    this.drawPreviews();
  }

  // -------- grid --------

  private drawGrid(): void {
    const vp = this.viewport;

    // Grid spacing in *world units* chosen to land near 50px on screen.
    // niceStep snaps that to a 1/2/5 multiple so labels stay readable.
    const targetPx = 50;
    const spacing = niceStep(targetPx / vp.scale);

    // Figure out which world-coord range is currently visible on screen.
    // Top-left of screen = pixel (0, 0). Bottom-right = (width, height).
    const tl = vp.screenToWorld({ x: 0, y: 0, _kind: 'screen' } as any);
    const br = vp.screenToWorld({ x: vp.width, y: vp.height, _kind: 'screen' } as any);

    const minX = Math.floor(tl.x / spacing) * spacing;
    const maxX = Math.ceil(br.x / spacing) * spacing;
    // Note: br has smaller y than tl in world coords (screen y flipped).
    const minY = Math.floor(br.y / spacing) * spacing;
    const maxY = Math.ceil(tl.y / spacing) * spacing;

    // Vertical grid lines (constant x).
    for (let x = minX; x <= maxX; x += spacing) {
      const isMajor = isCloseToMultiple(x, spacing * 5);
      const a = vp.worldToScreen(world(x, minY));
      const b = vp.worldToScreen(world(x, maxY));
      this.line(a.x, a.y, b.x, b.y, isMajor ? STYLE.gridMajor : STYLE.gridMinor, 1);
    }

    // Horizontal grid lines (constant y).
    for (let y = minY; y <= maxY; y += spacing) {
      const isMajor = isCloseToMultiple(y, spacing * 5);
      const a = vp.worldToScreen(world(minX, y));
      const b = vp.worldToScreen(world(maxX, y));
      this.line(a.x, a.y, b.x, b.y, isMajor ? STYLE.gridMajor : STYLE.gridMinor, 1);
    }
  }

  // -------- axes --------

  private drawAxes(): void {
    const vp = this.viewport;
    const origin = vp.worldToScreen(world(0, 0));

    // Vertical axis (the y-axis): only draw if it's actually on screen.
    if (origin.x >= 0 && origin.x <= vp.width) {
      this.line(origin.x, 0, origin.x, vp.height, STYLE.axis, 1.5);
    }
    // Horizontal axis (the x-axis).
    if (origin.y >= 0 && origin.y <= vp.height) {
      this.line(0, origin.y, vp.width, origin.y, STYLE.axis, 1.5);
    }
  }

  // -------- axis number labels --------

  private drawAxisLabels(): void {
    const vp = this.viewport;
    const spacing = niceStep(50 / vp.scale);
    const origin = vp.worldToScreen(world(0, 0));

    // Find visible world range again (small duplication, fine for now).
    const tl = vp.screenToWorld({ x: 0, y: 0, _kind: 'screen' } as any);
    const br = vp.screenToWorld({ x: vp.width, y: vp.height, _kind: 'screen' } as any);

    // Numbers on the x-axis. Skip 0 because the y-axis already marks it.
    const minX = Math.floor(tl.x / spacing) * spacing;
    const maxX = Math.ceil(br.x / spacing) * spacing;
    for (let x = minX; x <= maxX; x += spacing) {
      if (Math.abs(x) < spacing / 2) continue; // skip 0
      const s = vp.worldToScreen(world(x, 0));
      // Tick mark crossing the axis.
      this.line(s.x, origin.y - STYLE.tickLength, s.x, origin.y + STYLE.tickLength, STYLE.axis, 1);
      // Number, just below the axis.
      this.text(s.x, origin.y + STYLE.tickLength + STYLE.fontSize, formatNumber(x), 'middle');
    }

    // Numbers on the y-axis.
    const minY = Math.floor(br.y / spacing) * spacing;
    const maxY = Math.ceil(tl.y / spacing) * spacing;
    for (let y = minY; y <= maxY; y += spacing) {
      if (Math.abs(y) < spacing / 2) continue;
      const s = vp.worldToScreen(world(0, y));
      this.line(origin.x - STYLE.tickLength, s.y, origin.x + STYLE.tickLength, s.y, STYLE.axis, 1);
      // Number, just to the left of the axis.
      this.text(origin.x - STYLE.tickLength - 3, s.y + STYLE.fontSize / 3, formatNumber(y), 'end');
    }

    // Origin label "0" tucked into the corner of the axes.
    this.text(origin.x - STYLE.tickLength - 3, origin.y + STYLE.fontSize + 2, '0', 'end');
  }

  // -------- tiny helpers for making SVG elements --------

  private drawConstructions(): void {
  for (const o of this.scene.objects.values()) {
    if (o.kind !== 'construction') continue;
    // Draw edges
    for (const [p1Id, p2Id] of o.edges) {
      const p1 = this.scene.objects.get(p1Id);
      const p2 = this.scene.objects.get(p2Id);
      if (p1?.kind !== 'point' || p2?.kind !== 'point') continue;
      const s1 = this.viewport.worldToScreen(world(p1.x, p1.y));
      const s2 = this.viewport.worldToScreen(world(p2.x, p2.y));
      this.line(s1.x, s1.y, s2.x, s2.y, '#888', 1.5);  // construction color
    }
    // Draw circles
    for (const circ of o.circles) {
      const c = this.scene.objects.get(circ.center);
      if (c?.kind !== 'point') continue;
      const sc = this.viewport.worldToScreen(world(c.x, c.y));
      const r = circ.radius * this.viewport.scale;
      const el = document.createElementNS(SVG_NS, 'circle');
      el.setAttribute('cx', String(sc.x));
      el.setAttribute('cy', String(sc.y));
      el.setAttribute('r', String(r));
      el.setAttribute('fill', 'none');
      el.setAttribute('stroke', '#888');
      el.setAttribute('stroke-width', '1.5');
      this.svg.appendChild(el);
    }
  }
}

  private line(x1: number, y1: number, x2: number, y2: number, stroke: string, width: number): void {
    const el = document.createElementNS(SVG_NS, 'line');
    el.setAttribute('x1', String(x1));
    el.setAttribute('y1', String(y1));
    el.setAttribute('x2', String(x2));
    el.setAttribute('y2', String(y2));
    el.setAttribute('stroke', stroke);
    el.setAttribute('stroke-width', String(width));
    this.svg.appendChild(el);
  }

  private text(x: number, y: number, content: string, anchor: 'start' | 'middle' | 'end'): void {
    const el = document.createElementNS(SVG_NS, 'text');
    el.setAttribute('x', String(x));
    el.setAttribute('y', String(y));
    el.setAttribute('text-anchor', anchor);
    el.setAttribute('font-family', 'system-ui, sans-serif');
    el.setAttribute('font-size', String(STYLE.fontSize));
    el.setAttribute('fill', STYLE.axisLabel);
    el.textContent = content;
    this.svg.appendChild(el);
  }

  private drawCircles(): void {
    for (const o of this.scene.objects.values()) {
      if (o.kind !== 'circle') continue;
      if (o.mode === 'center-through') {
        const c = this.scene.objects.get(o.center);
        const t = this.scene.objects.get(o.through);
        // Skip silently: a frame between cascade-delete and re-render
        // can briefly reference a stale ID.
        if (c?.kind !== 'point' || t?.kind !== 'point') continue;
        const radiusWorld = distance(
          c as unknown as WorldPoint,
          t as unknown as WorldPoint,
        );
        const sc = this.viewport.worldToScreen(world(c.x, c.y));
        const r = radiusWorld * this.viewport.scale;
        const el = document.createElementNS(SVG_NS, 'circle');
        el.setAttribute('cx', String(sc.x));
        el.setAttribute('cy', String(sc.y));
        el.setAttribute('r', String(r));
        el.setAttribute('fill', 'none');
        el.setAttribute('stroke', STYLE.circleStroke);
        el.setAttribute('stroke-width', String(STYLE.circleStrokeWidth));
        this.svg.appendChild(el);
      }
      // o.mode === 'three-points': render branch lands when 3-point
      // tool ships. Type-completeness only — no current producer.
    }
  }

  private drawPreviews(): void {
    for (const p of this.scene.previews) {
      if (p.kind === 'highlightPoint') {
        const s = this.viewport.worldToScreen(world(p.pos.x, p.pos.y));
        const el = document.createElementNS(SVG_NS, 'circle');
        el.setAttribute('cx', String(s.x));
        el.setAttribute('cy', String(s.y));
        el.setAttribute('r', '9');
        el.setAttribute('fill', 'none');
        el.setAttribute('stroke', STYLE.snapStroke);
        el.setAttribute('stroke-width', '1.5');
        this.svg.appendChild(el);
      } else if (p.kind === 'rubberCircle') {
        const sc = this.viewport.worldToScreen(world(p.center.x, p.center.y));
        const r = Math.hypot(p.radiusVec.x - p.center.x, p.radiusVec.y - p.center.y) * this.viewport.scale;
        const el = document.createElementNS(SVG_NS, 'circle');
        el.setAttribute('cx', String(sc.x));
        el.setAttribute('cy', String(sc.y));
        el.setAttribute('r', String(r));
        el.setAttribute('fill', 'none');
        el.setAttribute('stroke', STYLE.previewStroke);
        el.setAttribute('stroke-width', String(STYLE.previewStrokeWidth));
        el.setAttribute('stroke-dasharray', STYLE.previewDash);
        this.svg.appendChild(el);
      }
    }
  }

  private drawPoints(): void {
    for (const p of this.scene.points()) {
      const s = this.viewport.worldToScreen(world(p.x, p.y));

      const dot = document.createElementNS(SVG_NS, 'circle');
      dot.setAttribute('cx', String(s.x));
      dot.setAttribute('cy', String(s.y));
      dot.setAttribute('r', '4.25');
      dot.setAttribute('fill', '#1a1a1a');
      this.svg.appendChild(dot);

      const label = document.createElementNS(SVG_NS, 'text');
      label.setAttribute('x', String(s.x + 9));
      label.setAttribute('y', String(s.y - 9));
      label.setAttribute('font-family', 'system-ui, sans-serif');
      label.setAttribute('font-size', '14');
      label.setAttribute('font-style', 'italic');
      label.setAttribute('fill', '#1a1a1a');
      label.textContent = p.label;
      this.svg.appendChild(label);
    }
  }
}

// -------- pure helpers, no SVG, no class --------

// Pick a "nice" round number >= raw: 1, 2, 5, 10, 20, 50, 100, 0.1, 0.2, ...
// This is the trick that makes grid spacing look natural at any zoom level.
function niceStep(raw: number): number {
  if (raw <= 0) return 1;
  const exp = Math.floor(Math.log10(raw));
  const base = Math.pow(10, exp);
  const mantissa = raw / base;
  if (mantissa < 1.5) return 1 * base;
  if (mantissa < 3.5) return 2 * base;
  if (mantissa < 7.5) return 5 * base;
  return 10 * base;
}

// Floating point is annoying — "is x a multiple of step" needs a tolerance.
function isCloseToMultiple(x: number, step: number): boolean {
  const ratio = x / step;
  return Math.abs(ratio - Math.round(ratio)) < 1e-9;
}

// Don't show "1.0000000002" — round to a sensible number of decimals.
function formatNumber(n: number): string {
  if (Math.abs(n) < 1e-9) return '0';
  // Show up to 3 decimal places, strip trailing zeros.
  return parseFloat(n.toFixed(3)).toString();
}