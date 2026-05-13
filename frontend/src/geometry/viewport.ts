import { WorldPoint, ScreenPoint, world, screen } from './coords';

const MIN_SCALE = 0.01;
const MAX_SCALE = 1000;

/**
The Viewport knows: where the camera is in world space, how zoomed in it is,
and how big the screen is. From that it can convert between coordinate systems.
**/
export class Viewport {
  center: WorldPoint = world(0, 0);

  // Pixels per world unit. Bigger = more zoomed in.
  scale: number = 50;

  width: number = 0;
  height: number = 0;

  worldToScreen(p: WorldPoint): ScreenPoint {
    const px = (p.x - this.center.x) * this.scale + this.width / 2;
    // Math y points up, screen y points down — flip.
    const py = this.height / 2 - (p.y - this.center.y) * this.scale;
    return screen(px, py);
  }

  screenToWorld(p: ScreenPoint): WorldPoint {
    const wx = (p.x - this.width / 2) / this.scale + this.center.x;
    const wy = (this.height / 2 - p.y) / this.scale + this.center.y;
    return world(wx, wy);
  }

  /**
  Pan by a screen-pixel delta, convert via /scale and flip dy because
  screen y grows down while world y grows up.
  **/
  pan(dxScreenPx: number, dyScreenPx: number): void {
    this.center = world(
      this.center.x - dxScreenPx / this.scale,
      this.center.y + dyScreenPx / this.scale,
    );
  }

  
  // Zoom by `factor` keeping the world point under `anchor` pinned.
  zoomAt(anchor: ScreenPoint, factor: number): void {
    const newScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, this.scale * factor));
    if (newScale === this.scale) return;
    // Capture the world point under the anchor before the rescale.
    const w = this.screenToWorld(anchor);
    this.scale = newScale;
    // Solve worldToScreen(w) = anchor for center at the new scale.
    this.center = world(
      w.x - (anchor.x - this.width / 2) / this.scale,
      w.y + (anchor.y - this.height / 2) / this.scale,
    );
  }
}