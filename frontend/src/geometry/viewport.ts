import { WorldPoint, ScreenPoint, world, screen } from './coords';

// The Viewport knows: where the camera is in world space, how zoomed in it is,
// and how big the screen is. From that it can convert between coordinate systems.
export class Viewport {
  // Center of the view in world coords. Starts at the math origin.
  center: WorldPoint = world(0, 0);

  // How many pixels equal 1 world unit. Bigger = more zoomed in.
  scale: number = 50;

  // Size of the drawing area in pixels. Set by the renderer when it boots.
  width: number = 0;
  height: number = 0;

  // Math coords -> pixel coords.
  worldToScreen(p: WorldPoint): ScreenPoint {
    const px = (p.x - this.center.x) * this.scale + this.width / 2;
    // Note the minus: math y points up, screen y points down, so we flip.
    const py = this.height / 2 - (p.y - this.center.y) * this.scale;
    return screen(px, py);
  }

  // Pixel coords -> math coords. Just the inverse of the above.
  screenToWorld(p: ScreenPoint): WorldPoint {
    const wx = (p.x - this.width / 2) / this.scale + this.center.x;
    const wy = (this.height / 2 - p.y) / this.scale + this.center.y;
    return world(wx, wy);
  }
}