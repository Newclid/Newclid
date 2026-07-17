import { describe, it, expect, beforeEach } from 'vitest';
import { Viewport } from '../../../src/geometry/viewport';
import { world, screen } from '../../../src/geometry/coords';

describe('Viewport', () => {
  let vp: Viewport;

  beforeEach(() => {
    vp = new Viewport();
    vp.width = 800;
    vp.height = 600;
  });

  describe('worldToScreen', () => {
    it('maps the camera center to the middle of the screen', () => {
      const p = vp.worldToScreen(vp.center);
      expect(p.x).toBeCloseTo(400);
      expect(p.y).toBeCloseTo(300);
    });

    it('flips the y axis since world y points up and screen y points down', () => {
      const p = vp.worldToScreen(world(0, 1));
      expect(p.y).toBeLessThan(300);
    });

    it('scales world distance by the current scale', () => {
      const p = vp.worldToScreen(world(1, 0));
      expect(p.x - 400).toBeCloseTo(vp.scale);
    });
  });

  describe('screenToWorld', () => {
    it('maps the screen center to the camera center', () => {
      const p = vp.screenToWorld(screen(400, 300));
      expect(p.x).toBeCloseTo(vp.center.x);
      expect(p.y).toBeCloseTo(vp.center.y);
    });

    it('is the inverse of worldToScreen', () => {
      const original = world(3.5, -2.25);
      const roundTripped = vp.screenToWorld(vp.worldToScreen(original));
      expect(roundTripped.x).toBeCloseTo(original.x);
      expect(roundTripped.y).toBeCloseTo(original.y);
    });
  });

  describe('pan', () => {
    it('moves the center opposite to a rightward screen drag', () => {
      const before = vp.center.x;
      vp.pan(100, 0);
      expect(vp.center.x).toBeLessThan(before);
    });

    it('moves the center by the delta divided by scale', () => {
      const before = { ...vp.center };
      vp.pan(vp.scale, 0);
      expect(vp.center.x).toBeCloseTo(before.x - 1);
      expect(vp.center.y).toBeCloseTo(before.y);
    });

    it('flips the y delta since screen y grows down', () => {
      const before = vp.center.y;
      vp.pan(0, vp.scale);
      expect(vp.center.y).toBeCloseTo(before + 1);
    });
  });

  describe('fitPoints', () => {
    it('does nothing when there are no points', () => {
      const before = { ...vp };
      vp.fitPoints([]);
      expect(vp.center.x).toBe(before.center.x);
      expect(vp.center.y).toBe(before.center.y);
      expect(vp.scale).toBe(before.scale);
    });

    it('centers the camera on the bounding box of the points', () => {
      vp.fitPoints([{ x: 0, y: 0 }, { x: 10, y: 20 }]);
      expect(vp.center.x).toBeCloseTo(5);
      expect(vp.center.y).toBeCloseTo(10);
    });

    it('falls back to a fixed scale when all points coincide', () => {
      vp.fitPoints([{ x: 4, y: 4 }, { x: 4, y: 4 }]);
      expect(vp.center.x).toBeCloseTo(4);
      expect(vp.center.y).toBeCloseTo(4);
      expect(vp.scale).toBe(200);
    });

    it('shrinks scale to fit a wider bounding box into the same screen', () => {
      vp.fitPoints([{ x: -50, y: 0 }, { x: 50, y: 0 }]);
      const narrowScale = vp.scale;
      vp.fitPoints([{ x: -500, y: 0 }, { x: 500, y: 0 }]);
      expect(vp.scale).toBeLessThan(narrowScale);
    });

    it('fits purely on the vertical range when points share an x coordinate', () => {
      vp.fitPoints([{ x: 3, y: -10 }, { x: 3, y: 10 }]);
      expect(vp.center.x).toBeCloseTo(3);
      expect(vp.scale).toBeCloseTo(vp.height / (20 * 1.3));
    });
  });

  describe('zoomAt', () => {
    it('increases scale by the given factor', () => {
      const before = vp.scale;
      vp.zoomAt(screen(400, 300), 2);
      expect(vp.scale).toBeCloseTo(before * 2);
    });

    it('keeps the world point under the anchor fixed', () => {
      const anchor = screen(150, 450);
      const worldUnderAnchorBefore = vp.screenToWorld(anchor);
      vp.zoomAt(anchor, 3);
      const worldUnderAnchorAfter = vp.screenToWorld(anchor);
      expect(worldUnderAnchorAfter.x).toBeCloseTo(worldUnderAnchorBefore.x);
      expect(worldUnderAnchorAfter.y).toBeCloseTo(worldUnderAnchorBefore.y);
    });

    it('clamps scale to the maximum', () => {
      vp.zoomAt(screen(400, 300), 1e9);
      expect(vp.scale).toBe(1000);
    });

    it('clamps scale to the minimum', () => {
      vp.zoomAt(screen(400, 300), 1e-9);
      expect(vp.scale).toBe(0.01);
    });

    it('is a no-op once already clamped at the maximum', () => {
      vp.zoomAt(screen(400, 300), 1e9);
      const centerBefore = { ...vp.center };
      vp.zoomAt(screen(400, 300), 1e9);
      expect(vp.center.x).toBe(centerBefore.x);
      expect(vp.center.y).toBe(centerBefore.y);
    });
  });
});
