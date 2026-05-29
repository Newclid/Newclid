import { Viewport } from '../geometry/viewport';
import { world, type WorldPoint } from '../geometry/coords';
import { Scene } from '../scene/scene';
import { distance } from '../geometry/primitives';

import type { SketchPoint } from '../api/types';
import type { ConstructionMarker, SketchGeom } from '../emit/jgexParser';

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
  // Construction markers on the proof sketch (midpoint ticks, right-angle squares, etc.).
  markerColor: '#2266cc',
  markerSize: 8,
};

export interface ProofSketch {
  points: SketchPoint[];
  geometry: SketchGeom[];
  extraGeometry?: SketchGeom[];
  markers?: ConstructionMarker[];
}

export class Renderer {
  readonly svg: SVGSVGElement;
  proofSketch: ProofSketch | null = null;

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

    this.drawGrid();
    this.drawAxes();
    this.drawAxisLabels();
    this.drawCircles();
    this.drawConstructions();
    this.drawPoints();
    this.drawPreviews();
    if (this.proofSketch) {
      this.drawProofSketch(this.proofSketch);
    }
  }

  // -------- grid --------

  private drawGrid(): void {
    const vp = this.viewport;

    const targetPx = 50;
    const spacing = niceStep(targetPx / vp.scale);

    // Visible world range. Top-left of screen = (0,0), bottom-right = (w,h).
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
    // Draw lines: through both points, extended in both directions.
    for (const [p1Id, p2Id] of o.lines ?? []) {
      const p1 = this.scene.objects.get(p1Id);
      const p2 = this.scene.objects.get(p2Id);
      if (p1?.kind !== 'point' || p2?.kind !== 'point') continue;
      const s1 = this.viewport.worldToScreen(world(p1.x, p1.y));
      const s2 = this.viewport.worldToScreen(world(p2.x, p2.y));
      const dx = s2.x - s1.x, dy = s2.y - s1.y;
      const len = Math.hypot(dx, dy);
      if (len < 1e-6) continue;
      const ext = 10000;
      const nx = (dx / len) * ext, ny = (dy / len) * ext;
      this.line(s1.x - nx, s1.y - ny, s1.x + nx, s1.y + ny, '#888', 1.5);
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

  private drawProofSketch(sketch: ProofSketch): void {
    const ptMap = new Map(sketch.points.map(p => [p.name, p]));
    this.drawSketchGeometry(sketch.geometry, ptMap);
    if (sketch.extraGeometry?.length) {
      this.drawSketchGeometry(sketch.extraGeometry, ptMap, '4 3');
    }
    if (sketch.markers?.length) {
      this.drawConstructionMarkers(sketch.markers, ptMap);
    }
    this.drawSketchPoints(sketch.points);
  }

  private drawSketchGeometry(geometry: SketchGeom[], ptMap: Map<string, SketchPoint>, dash?: string): void {
    for (const g of geometry) {
      if (g.kind === 'segment') {
        const pa = ptMap.get(g.p1), pb = ptMap.get(g.p2);
        if (!pa || !pb) continue;
        const sa = this.viewport.worldToScreen(world(pa.x, pa.y));
        const sb = this.viewport.worldToScreen(world(pb.x, pb.y));
        this.line(sa.x, sa.y, sb.x, sb.y, '#888', 1.5, dash);

      } else if (g.kind === 'line') {
        const pa = ptMap.get(g.p1), pb = ptMap.get(g.p2);
        if (!pa || !pb) continue;
        const sa = this.viewport.worldToScreen(world(pa.x, pa.y));
        const sb = this.viewport.worldToScreen(world(pb.x, pb.y));
        const dx = sb.x - sa.x, dy = sb.y - sa.y;
        const len = Math.hypot(dx, dy);
        if (len < 1e-6) continue;
        const ext = 10000;
        const nx = (dx / len) * ext, ny = (dy / len) * ext;
        this.line(sa.x - nx, sa.y - ny, sa.x + nx, sa.y + ny, '#888', 1.5, dash);

      } else if (g.kind === 'circle') {
        const pc = ptMap.get(g.center), pt = ptMap.get(g.through);
        if (!pc || !pt) continue;
        const radiusWorld = Math.hypot(pt.x - pc.x, pt.y - pc.y);
        const sc = this.viewport.worldToScreen(world(pc.x, pc.y));
        const r = radiusWorld * this.viewport.scale;
        this.svgCircle(sc.x, sc.y, r, dash);

      } else if (g.kind === 'circumcircle') {
        const pa = ptMap.get(g.p1), pb = ptMap.get(g.p2), pc = ptMap.get(g.p3);
        if (!pa || !pb || !pc) continue;
        const cc = circumcenter(pa, pb, pc);
        if (!cc) continue;
        const radiusWorld = Math.hypot(pa.x - cc.x, pa.y - cc.y);
        const sc = this.viewport.worldToScreen(world(cc.x, cc.y));
        const r = radiusWorld * this.viewport.scale;
        this.svgCircle(sc.x, sc.y, r, dash);
      }
    }
  }

  private drawSketchPoints(points: SketchPoint[]): void {
    for (const p of points) {
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
      label.textContent = displayPointName(p.name);
      this.svg.appendChild(label);
    }
  }

  private drawConstructionMarkers(
    markers: ConstructionMarker[],
    ptMap: Map<string, SketchPoint>,
  ): void {
    for (const marker of markers) {
      switch (marker.kind) {
        case 'midp': {
          const [m, a, b] = marker.args;
          const pm = ptMap.get(m), pa = ptMap.get(a), pb = ptMap.get(b);
          if (!pm || !pa || !pb) break;
          this.drawTickMark(pm, pa, STYLE.markerColor, 6);
          this.drawTickMark(pm, pb, STYLE.markerColor, 6);
          break;
        }
        case 'perp': {
          const [a, b, c, d] = marker.args;
          const pa = ptMap.get(a), pb = ptMap.get(b), pc = ptMap.get(c), pd = ptMap.get(d);
          if (!pa || !pb || !pc || !pd) break;
          const ix = lineIntersect(pa.x, pa.y, pb.x, pb.y, pc.x, pc.y, pd.x, pd.y);
          if (!ix) break;
          const si = this.viewport.worldToScreen(world(ix.x, ix.y));
          const sa = this.viewport.worldToScreen(world(pa.x, pa.y));
          const sb = this.viewport.worldToScreen(world(pb.x, pb.y));
          const sc = this.viewport.worldToScreen(world(pc.x, pc.y));
          const sd = this.viewport.worldToScreen(world(pd.x, pd.y));
          const lenAB = Math.hypot(sb.x - sa.x, sb.y - sa.y);
          const lenCD = Math.hypot(sd.x - sc.x, sd.y - sc.y);
          if (lenAB < 1e-6 || lenCD < 1e-6) break;
          const uABx = (sb.x - sa.x) / lenAB, uABy = (sb.y - sa.y) / lenAB;
          const uCDx = (sd.x - sc.x) / lenCD, uCDy = (sd.y - sc.y) / lenCD;
          const s = STYLE.markerSize;
          const c1x = si.x + s * uABx, c1y = si.y + s * uABy;
          const c2x = c1x + s * uCDx, c2y = c1y + s * uCDy;
          const c3x = si.x + s * uCDx, c3y = si.y + s * uCDy;
          this.line(c1x, c1y, c2x, c2y, STYLE.markerColor, 1.5);
          this.line(c3x, c3y, c2x, c2y, STYLE.markerColor, 1.5);
          break;
        }
        case 'cong': {
          const [a, b, c, d] = marker.args;
          const pa = ptMap.get(a), pb = ptMap.get(b), pc = ptMap.get(c), pd = ptMap.get(d);
          if (!pa || !pb || !pc || !pd) break;
          this.drawTickMark(pa, pb, STYLE.markerColor, 6);
          this.drawTickMark(pc, pd, STYLE.markerColor, 6);
          break;
        }
        case 'para': {
          const [a, b, c, d] = marker.args;
          const pa = ptMap.get(a), pb = ptMap.get(b), pc = ptMap.get(c), pd = ptMap.get(d);
          if (!pa || !pb || !pc || !pd) break;
          this.drawChevron(pa, pb, STYLE.markerColor);
          this.drawChevron(pc, pd, STYLE.markerColor);
          break;
        }
        default:
          break;
      }
    }
  }

  private drawTickMark(
    pa: { x: number; y: number },
    pb: { x: number; y: number },
    color: string,
    halfLen: number,
  ): void {
    const sa = this.viewport.worldToScreen(world(pa.x, pa.y));
    const sb = this.viewport.worldToScreen(world(pb.x, pb.y));
    const mx = (sa.x + sb.x) / 2, my = (sa.y + sb.y) / 2;
    const dx = sb.x - sa.x, dy = sb.y - sa.y;
    const len = Math.hypot(dx, dy);
    if (len < 1e-6) return;
    const px = -dy / len, py = dx / len;
    this.line(mx - halfLen * px, my - halfLen * py, mx + halfLen * px, my + halfLen * py, color, 1.5);
  }

  private drawChevron(
    pa: { x: number; y: number },
    pb: { x: number; y: number },
    color: string,
  ): void {
    const sa = this.viewport.worldToScreen(world(pa.x, pa.y));
    const sb = this.viewport.worldToScreen(world(pb.x, pb.y));
    const mx = (sa.x + sb.x) / 2, my = (sa.y + sb.y) / 2;
    const dx = sb.x - sa.x, dy = sb.y - sa.y;
    const len = Math.hypot(dx, dy);
    if (len < 1e-6) return;
    const ux = dx / len, uy = dy / len;
    const vx = -uy, vy = ux;
    const arm = 6;
    const tx = mx + arm * ux, ty = my + arm * uy;
    const l1x = mx - arm * ux + arm * vx, l1y = my - arm * uy + arm * vy;
    const l2x = mx - arm * ux - arm * vx, l2y = my - arm * uy - arm * vy;
    this.line(l1x, l1y, tx, ty, color, 1.5);
    this.line(l2x, l2y, tx, ty, color, 1.5);
  }

  private svgCircle(cx: number, cy: number, r: number, dash?: string): void {
    const el = document.createElementNS(SVG_NS, 'circle');
    el.setAttribute('cx', String(cx));
    el.setAttribute('cy', String(cy));
    el.setAttribute('r', String(r));
    el.setAttribute('fill', 'none');
    el.setAttribute('stroke', '#888');
    el.setAttribute('stroke-width', '1.5');
    if (dash) el.setAttribute('stroke-dasharray', dash);
    this.svg.appendChild(el);
  }

  private line(x1: number, y1: number, x2: number, y2: number, stroke: string, width: number, dash?: string): void {
    const el = document.createElementNS(SVG_NS, 'line');
    el.setAttribute('x1', String(x1));
    el.setAttribute('y1', String(y1));
    el.setAttribute('x2', String(x2));
    el.setAttribute('y2', String(y2));
    el.setAttribute('stroke', stroke);
    el.setAttribute('stroke-width', String(width));
    if (dash) el.setAttribute('stroke-dasharray', dash);
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
        /**
        Skip silently: a frame between cascade-delete and re-render
        can briefly reference a stale ID.
        **/
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
      } else if (p.kind === 'auxLine') {
        // Dashed parallel/perpendicular guide drawn while a derive slot is active.
        const a = this.viewport.worldToScreen(world(p.from.x, p.from.y));
        const b = this.viewport.worldToScreen(world(p.to.x, p.to.y));
        const el = document.createElementNS(SVG_NS, 'line');
        el.setAttribute('x1', String(a.x));
        el.setAttribute('y1', String(a.y));
        el.setAttribute('x2', String(b.x));
        el.setAttribute('y2', String(b.y));
        el.setAttribute('stroke', STYLE.previewStroke);
        el.setAttribute('stroke-width', String(STYLE.previewStrokeWidth));
        el.setAttribute('stroke-dasharray', STYLE.previewDash);
        this.svg.appendChild(el);
      } else if (p.kind === 'partialEdge') {
        // Already-bound edge of an in-progress construction.
        const a = this.viewport.worldToScreen(world(p.from.x, p.from.y));
        const b = this.viewport.worldToScreen(world(p.to.x, p.to.y));
        this.line(a.x, a.y, b.x, b.y, '#888', 1.5);
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
      dot.setAttribute('fill', p.color ?? '#1a1a1a');
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

function displayPointName(name: string): string {
  if (!name) return name;
  let out = name[0].toUpperCase();
  for (let i = 1; i < name.length; i++) {
    const c = name[i];
    if (c >= '0' && c <= '9') {
      out += String.fromCharCode(0x2080 + c.charCodeAt(0) - 0x30);
    } else {
      out += c;
    }
  }
  return out;
}

function circumcenter(
  p1: { x: number; y: number },
  p2: { x: number; y: number },
  p3: { x: number; y: number },
): { x: number; y: number } | null {
  const D = 2 * (p1.x * (p2.y - p3.y) + p2.x * (p3.y - p1.y) + p3.x * (p1.y - p2.y));
  if (Math.abs(D) < 1e-10) return null;
  const s1 = p1.x * p1.x + p1.y * p1.y;
  const s2 = p2.x * p2.x + p2.y * p2.y;
  const s3 = p3.x * p3.x + p3.y * p3.y;
  return {
    x: (s1 * (p2.y - p3.y) + s2 * (p3.y - p1.y) + s3 * (p1.y - p2.y)) / D,
    y: (s1 * (p3.x - p2.x) + s2 * (p1.x - p3.x) + s3 * (p2.x - p1.x)) / D,
  };
}

/**
Pick a "nice" round number >= raw: 1, 2, 5, 10, 20, 50, 100, 0.1, ...
Makes grid spacing look natural at any zoom level.
**/
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

function lineIntersect(
  ax: number, ay: number, bx: number, by: number,
  cx: number, cy: number, dx: number, dy: number,
): { x: number; y: number } | null {
  const dxAB = bx - ax, dyAB = by - ay;
  const dxCD = dx - cx, dyCD = dy - cy;
  const denom = dxAB * dyCD - dyAB * dxCD;
  if (Math.abs(denom) < 1e-9) return null;
  const t = ((cx - ax) * dyCD - (cy - ay) * dxCD) / denom;
  return { x: ax + t * dxAB, y: ay + t * dyAB };
}