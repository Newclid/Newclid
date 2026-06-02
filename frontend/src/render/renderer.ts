import { Viewport } from '../geometry/viewport';
import { world, type WorldPoint } from '../geometry/coords';
import { Scene } from '../scene/scene';
import { distance } from '../geometry/primitives';

import type { SketchPoint } from '../api/types';
import type { ConstructionMarker, SketchGeom } from '../emit/jgexParser';

const SVG_NS = 'http://www.w3.org/2000/svg';

const STYLE = {
  background: '#fafafa',
  gridMinor: '#ececec',
  gridMajor: '#d0d0d0',
  axis: '#333',
  axisLabel: '#555',
  tickLength: 4,
  fontSize: 11,
  circleStroke: '#1A1816',
  circleStrokeWidth: 1.75,
  snapStroke: '#2A4A7F',
  previewStroke: '#8C887F',
  previewStrokeWidth: 1.5,
  previewDash: '5 4',
  markerColor: '#2266cc',
  markerSize: 8,
};

export interface ProofSketch {
  points: SketchPoint[];
  geometry: SketchGeom[];
  extraGeometry?: SketchGeom[];
  markers?: ConstructionMarker[];
  ptMap?: Map<string, SketchPoint>;
}

type CachedPerp = ConstructionMarker & { _worldPos?: { x: number; y: number } | null };

export class Renderer {
  readonly svg: SVGSVGElement;
  private readonly _proofCanvas: HTMLCanvasElement;
  private _proofSketch: ProofSketch | null = null;

  get proofSketch(): ProofSketch | null { return this._proofSketch; }
  set proofSketch(sketch: ProofSketch | null) {
    if (sketch) {
      sketch.ptMap = new Map(sketch.points.map(p => [p.name, p]));
      for (const marker of sketch.markers ?? []) {
        if (marker.kind === 'perp') {
          const [a, b, c, d] = marker.args;
          const pa = sketch.ptMap.get(a), pb = sketch.ptMap.get(b);
          const pc = sketch.ptMap.get(c), pd = sketch.ptMap.get(d);
          (marker as CachedPerp)._worldPos = (pa && pb && pc && pd)
            ? lineIntersect(pa.x, pa.y, pb.x, pb.y, pc.x, pc.y, pd.x, pd.y)
            : null;
        }
      }
    }
    this._proofSketch = sketch;
    this._proofCanvas.style.display = sketch ? 'block' : 'none';
  }

  constructor(private container: HTMLElement, private viewport: Viewport, private scene: Scene) {
    this.svg = document.createElementNS(SVG_NS, 'svg');
    this.svg.style.background = STYLE.background;
    this.svg.style.display = 'block';
    this.container.appendChild(this.svg);
    this._proofCanvas = document.createElement('canvas');
    this._proofCanvas.style.cssText = 'position:absolute;top:0;left:0;pointer-events:none;display:none';
    this.container.appendChild(this._proofCanvas);
    this.resize();
  }

  resize(): void {
    const w = this.viewport.width, h = this.viewport.height;
    const dpr = window.devicePixelRatio || 1;
    this.svg.setAttribute('width', String(w));
    this.svg.setAttribute('height', String(h));
    this._proofCanvas.width = Math.round(w * dpr);
    this._proofCanvas.height = Math.round(h * dpr);
    this._proofCanvas.style.width = `${w}px`;
    this._proofCanvas.style.height = `${h}px`;
  }

  draw(): void {
    while (this.svg.firstChild) this.svg.removeChild(this.svg.firstChild);
    this.drawGrid();
    this.drawAxes();
    this.drawAxisLabels();
    this.drawCircles();
    this.drawConstructions();
    this.drawPoints();
    this.drawPreviews();
    if (this._proofSketch) this.drawProofSketchCanvas();
  }

  // -------- grid --------

  private drawGrid(): void {
    const vp = this.viewport;

    const targetPx = 50;
    const spacing = niceStep(targetPx / vp.scale);

    const tl = vp.screenToWorld({ x: 0, y: 0, _kind: 'screen' } as any);
    const br = vp.screenToWorld({ x: vp.width, y: vp.height, _kind: 'screen' } as any);

    const minX = Math.floor(tl.x / spacing) * spacing;
    const maxX = Math.ceil(br.x / spacing) * spacing;
    const minY = Math.floor(br.y / spacing) * spacing;
    const maxY = Math.ceil(tl.y / spacing) * spacing;

    for (let x = minX; x <= maxX; x += spacing) {
      const isMajor = isCloseToMultiple(x, spacing * 5);
      const a = vp.worldToScreen(world(x, minY));
      const b = vp.worldToScreen(world(x, maxY));
      this.line(a.x, a.y, b.x, b.y, isMajor ? STYLE.gridMajor : STYLE.gridMinor, 1);
    }

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

    if (origin.x >= 0 && origin.x <= vp.width) {
      this.line(origin.x, 0, origin.x, vp.height, STYLE.axis, 1.5);
    }
    if (origin.y >= 0 && origin.y <= vp.height) {
      this.line(0, origin.y, vp.width, origin.y, STYLE.axis, 1.5);
    }
  }

  // -------- axis number labels --------

  private drawAxisLabels(): void {
    const vp = this.viewport;
    const spacing = niceStep(50 / vp.scale);
    const origin = vp.worldToScreen(world(0, 0));

    const tl = vp.screenToWorld({ x: 0, y: 0, _kind: 'screen' } as any);
    const br = vp.screenToWorld({ x: vp.width, y: vp.height, _kind: 'screen' } as any);

    const minX = Math.floor(tl.x / spacing) * spacing;
    const maxX = Math.ceil(br.x / spacing) * spacing;
    for (let x = minX; x <= maxX; x += spacing) {
      if (Math.abs(x) < spacing / 2) continue;
      const s = vp.worldToScreen(world(x, 0));
      this.line(s.x, origin.y - STYLE.tickLength, s.x, origin.y + STYLE.tickLength, STYLE.axis, 1);
      this.text(s.x, origin.y + STYLE.tickLength + STYLE.fontSize, formatNumber(x), 'middle');
    }

    const minY = Math.floor(br.y / spacing) * spacing;
    const maxY = Math.ceil(tl.y / spacing) * spacing;
    for (let y = minY; y <= maxY; y += spacing) {
      if (Math.abs(y) < spacing / 2) continue;
      const s = vp.worldToScreen(world(0, y));
      this.line(origin.x - STYLE.tickLength, s.y, origin.x + STYLE.tickLength, s.y, STYLE.axis, 1);
      this.text(origin.x - STYLE.tickLength - 3, s.y + STYLE.fontSize / 3, formatNumber(y), 'end');
    }

    this.text(origin.x - STYLE.tickLength - 3, origin.y + STYLE.fontSize + 2, '0', 'end');
  }

  private drawConstructions(): void {
    for (const o of this.scene.objects.values()) {
      if (o.kind !== 'construction') continue;
      for (const [p1Id, p2Id] of o.edges) {
        const p1 = this.scene.objects.get(p1Id);
        const p2 = this.scene.objects.get(p2Id);
        if (p1?.kind !== 'point' || p2?.kind !== 'point') continue;
        const s1 = this.viewport.worldToScreen(world(p1.x, p1.y));
        const s2 = this.viewport.worldToScreen(world(p2.x, p2.y));
        this.line(s1.x, s1.y, s2.x, s2.y, '#888', 1.5);
      }
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

  private drawCircles(): void {
    for (const o of this.scene.objects.values()) {
      if (o.kind !== 'circle') continue;
      if (o.mode === 'center-through') {
        const c = this.scene.objects.get(o.center);
        const t = this.scene.objects.get(o.through);
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

  // -------- proof sketch via Canvas 2D --------

  private drawProofSketchCanvas(): void {
    const sketch = this._proofSketch!;
    const dpr = window.devicePixelRatio || 1;
    const ctx = this._proofCanvas.getContext('2d')!;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, this.viewport.width, this.viewport.height);

    const ptMap = sketch.ptMap!;

    ctx.strokeStyle = '#888';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([]);
    this.canvasGeometry(ctx, sketch.geometry, ptMap);

    ctx.setLineDash([4, 3]);
    this.canvasGeometry(ctx, sketch.extraGeometry ?? [], ptMap);
    ctx.setLineDash([]);

    if (sketch.markers?.length) this.canvasMarkers(ctx, sketch.markers, ptMap);
    this.canvasPoints(ctx, sketch.points);
  }

  private canvasGeometry(
    ctx: CanvasRenderingContext2D,
    geometry: SketchGeom[],
    ptMap: Map<string, SketchPoint>,
  ): void {
    for (const g of geometry) {
      if (g.kind === 'segment') {
        const pa = ptMap.get(g.p1), pb = ptMap.get(g.p2);
        if (!pa || !pb) continue;
        const sa = this.viewport.worldToScreen(world(pa.x, pa.y));
        const sb = this.viewport.worldToScreen(world(pb.x, pb.y));
        ctx.beginPath();
        ctx.moveTo(sa.x, sa.y);
        ctx.lineTo(sb.x, sb.y);
        ctx.stroke();

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
        ctx.beginPath();
        ctx.moveTo(sa.x - nx, sa.y - ny);
        ctx.lineTo(sa.x + nx, sa.y + ny);
        ctx.stroke();

      } else if (g.kind === 'circle') {
        const pc = ptMap.get(g.center), pt = ptMap.get(g.through);
        if (!pc || !pt) continue;
        const radiusWorld = Math.hypot(pt.x - pc.x, pt.y - pc.y);
        const sc = this.viewport.worldToScreen(world(pc.x, pc.y));
        const r = radiusWorld * this.viewport.scale;
        ctx.beginPath();
        ctx.arc(sc.x, sc.y, r, 0, 2 * Math.PI);
        ctx.stroke();

      } else if (g.kind === 'circumcircle') {
        const pa = ptMap.get(g.p1), pb = ptMap.get(g.p2), pc = ptMap.get(g.p3);
        if (!pa || !pb || !pc) continue;
        const cc = circumcenter(pa, pb, pc);
        if (!cc) continue;
        const radiusWorld = Math.hypot(pa.x - cc.x, pa.y - cc.y);
        const sc = this.viewport.worldToScreen(world(cc.x, cc.y));
        const r = radiusWorld * this.viewport.scale;
        ctx.beginPath();
        ctx.arc(sc.x, sc.y, r, 0, 2 * Math.PI);
        ctx.stroke();
      }
    }
  }

  private canvasMarkers(
    ctx: CanvasRenderingContext2D,
    markers: ConstructionMarker[],
    ptMap: Map<string, SketchPoint>,
  ): void {
    ctx.strokeStyle = STYLE.markerColor;
    ctx.lineWidth = 1.5;
    for (const marker of markers) {
      switch (marker.kind) {
        case 'midp': {
          const [m, a, b] = marker.args;
          const pm = ptMap.get(m), pa = ptMap.get(a), pb = ptMap.get(b);
          if (!pm || !pa || !pb) break;
          canvasTickMark(ctx, this.viewport, pm, pa, 6);
          canvasTickMark(ctx, this.viewport, pm, pb, 6);
          break;
        }
        case 'perp': {
          const ix = (marker as CachedPerp)._worldPos;
          if (!ix) break;
          const [a, b, c, d] = marker.args;
          const pa = ptMap.get(a), pb = ptMap.get(b), pc = ptMap.get(c), pd = ptMap.get(d);
          if (!pa || !pb || !pc || !pd) break;
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
          ctx.beginPath();
          ctx.moveTo(c1x, c1y);
          ctx.lineTo(c2x, c2y);
          ctx.lineTo(c3x, c3y);
          ctx.stroke();
          break;
        }
        case 'cong': {
          const [a, b, c, d] = marker.args;
          const pa = ptMap.get(a), pb = ptMap.get(b), pc = ptMap.get(c), pd = ptMap.get(d);
          if (!pa || !pb || !pc || !pd) break;
          canvasTickMark(ctx, this.viewport, pa, pb, 6);
          canvasTickMark(ctx, this.viewport, pc, pd, 6);
          break;
        }
        case 'para': {
          const [a, b, c, d] = marker.args;
          const pa = ptMap.get(a), pb = ptMap.get(b), pc = ptMap.get(c), pd = ptMap.get(d);
          if (!pa || !pb || !pc || !pd) break;
          canvasChevron(ctx, this.viewport, pa, pb);
          canvasChevron(ctx, this.viewport, pc, pd);
          break;
        }
        default:
          break;
      }
    }
  }

  private canvasPoints(ctx: CanvasRenderingContext2D, points: SketchPoint[]): void {
    ctx.fillStyle = '#1a1a1a';
    ctx.font = 'italic 14px system-ui, sans-serif';
    for (const p of points) {
      const s = this.viewport.worldToScreen(world(p.x, p.y));
      ctx.beginPath();
      ctx.arc(s.x, s.y, 4.25, 0, 2 * Math.PI);
      ctx.fill();
      ctx.fillText(displayPointName(p.name), s.x + 9, s.y - 9);
    }
  }

  // -------- SVG helpers --------

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
}

// -------- canvas helpers --------

function canvasTickMark(
  ctx: CanvasRenderingContext2D,
  vp: Viewport,
  pa: { x: number; y: number },
  pb: { x: number; y: number },
  halfLen: number,
): void {
  const sa = vp.worldToScreen(world(pa.x, pa.y));
  const sb = vp.worldToScreen(world(pb.x, pb.y));
  const mx = (sa.x + sb.x) / 2, my = (sa.y + sb.y) / 2;
  const dx = sb.x - sa.x, dy = sb.y - sa.y;
  const len = Math.hypot(dx, dy);
  if (len < 1e-6) return;
  const px = -dy / len, py = dx / len;
  ctx.beginPath();
  ctx.moveTo(mx - halfLen * px, my - halfLen * py);
  ctx.lineTo(mx + halfLen * px, my + halfLen * py);
  ctx.stroke();
}

function canvasChevron(
  ctx: CanvasRenderingContext2D,
  vp: Viewport,
  pa: { x: number; y: number },
  pb: { x: number; y: number },
): void {
  const sa = vp.worldToScreen(world(pa.x, pa.y));
  const sb = vp.worldToScreen(world(pb.x, pb.y));
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
  ctx.beginPath();
  ctx.moveTo(l1x, l1y);
  ctx.lineTo(tx, ty);
  ctx.moveTo(l2x, l2y);
  ctx.lineTo(tx, ty);
  ctx.stroke();
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

function isCloseToMultiple(x: number, step: number): boolean {
  const ratio = x / step;
  return Math.abs(ratio - Math.round(ratio)) < 1e-9;
}

function formatNumber(n: number): string {
  if (Math.abs(n) < 1e-9) return '0';
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
