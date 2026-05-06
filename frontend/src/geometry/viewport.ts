import { WorldPoint, ScreenPoint, world, screen } from './coords';

// Zoom clamps, in pixels per world unit. Below MIN, gridlines collapse
// onto each other and individual world units stop being distinguishable.
// Above MAX, world coords near the visible area get large enough that
// floating-point error in worldToScreen starts to show.
const MIN_SCALE = 0.01;
const MAX_SCALE = 1000;

// The Viewport knows: where the camera is in world space, how zoomed in it is,
// and how big the screen is. From that it can convert between coordinate systems.
export class Viewport {
  center: WorldPoint = world(0, 0);

  // Pixels per world unit. Bigger = more zoomed in.
  scale: number = 50;

  width: number = 0;
  height: number = 0;

  worldToScreen(p: WorldPoint): ScreenPoint {
    const px = (p.x - this.center.x) * this.scale + this.width / 2;
    // Note the minus: math y points up, screen y points down, so we flip.
    const py = this.height / 2 - (p.y - this.center.y) * this.scale;
    return screen(px, py);
  }

  screenToWorld(p: ScreenPoint): WorldPoint {
    const wx = (p.x - this.width / 2) / this.scale + this.center.x;
    const wy = (this.height / 2 - p.y) / this.scale + this.center.y;
    return world(wx, wy);
  }

  // Pan by a screen-pixel delta (the cursor's incremental motion during
  // a drag). We convert pixels -> world units by dividing by scale, and
  // flip dy because screen y grows down while world y grows up.
  pan(dxScreenPx: number, dyScreenPx: number): void {
    this.center = world(
      this.center.x - dxScreenPx / this.scale,
      this.center.y + dyScreenPx / this.scale,
    );
  }

  // Multiply zoom by `factor` while keeping the world point currently under
  // `anchor` pinned at the same screen position (so wheel-zoom feels like
  // it pulls toward the cursor). Clamps to MIN/MAX_SCALE; if clamping
  // makes the new scale equal to the old we no-op, otherwise repeated
  // wheel events at the limit would still shift center.
  // TODO: trackpad pinch gestures — they fire as ctrl+wheel today and
  // flow through here, but the sensitivity isn't tuned for pinch.
  zoomAt(anchor: ScreenPoint, factor: number): void {
    const newScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, this.scale * factor));
    if (newScale === this.scale) return;
    // Capture the world point under the anchor *before* the rescale.
    const w = this.screenToWorld(anchor);
    this.scale = newScale;
    // Solve worldToScreen(w) = anchor for center, at the new scale. Same
    // y-flip as worldToScreen.
    this.center = world(
      w.x - (anchor.x - this.width / 2) / this.scale,
      w.y + (anchor.y - this.height / 2) / this.scale,
    );
  }
}