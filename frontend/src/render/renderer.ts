import { Viewport } from '../geometry/viewport';
import { world } from '../geometry/coords';

const SVG_NS = 'http://www.w3.org/2000/svg';

const STYLE = {
  background: '#fafafa',
  gridMinor: '#ececec',  // small grid lines
  gridMajor: '#d0d0d0',  // every 5th line, slightly darker
  axis: '#333',
  axisLabel: '#555',     // numbers next to ticks
  tickLength: 4,         // pixels of tick mark on each side of axis
  fontSize: 11,
};

export class Renderer {
  // Exposed (readonly) so the input layer can attach pointer/wheel
  // listeners. Renderer still owns the element's lifecycle and contents.
  readonly svg: SVGSVGElement;

  constructor(private container: HTMLElement, private viewport: Viewport) {
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

    // Order matters in SVG: later elements draw on top of earlier ones.
    // So we draw grid first, then axes, then labels.
    this.drawGrid();
    this.drawAxes();
    this.drawAxisLabels();
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