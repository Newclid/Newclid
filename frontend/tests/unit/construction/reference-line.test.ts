import { describe, it, expect } from 'vitest';
import { Scene } from '../../../src/scene/scene';
import { addPoints } from '../../helpers/scene';
import { lineExists, ensureReferenceLine, drawReferenceLineOnSlotB } from '../../../src/construction/reference-line';

describe('lineExists', () => {
  it('is false when there are no constructions', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(lineExists(scene, a, b)).toBe(false);
  });

  it('is true when a construction already has a line through a and b', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    scene.addObject({
      kind: 'construction', name: 'line', bindings: { a, b }, edges: [], lines: [[a, b]], circles: [],
    });
    expect(lineExists(scene, a, b)).toBe(true);
  });

  it('is true regardless of point order', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    scene.addObject({
      kind: 'construction', name: 'line', bindings: { a, b }, edges: [], lines: [[a, b]], circles: [],
    });
    expect(lineExists(scene, b, a)).toBe(true);
  });

  it('ignores constructions without a lines array', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    scene.addObject({
      kind: 'construction', name: 'segment', bindings: { a, b }, edges: [[a, b]], circles: [],
    });
    expect(lineExists(scene, a, b)).toBe(false);
  });

  it('ignores non-construction objects', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    scene.addObject({ kind: 'circle', mode: 'center-through', center: a, through: b });
    expect(lineExists(scene, a, b)).toBe(false);
  });
});

describe('ensureReferenceLine', () => {
  it('adds a line construction through a and b when none exists', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    ensureReferenceLine(scene, a, b);
    expect(lineExists(scene, a, b)).toBe(true);
  });

  it('does nothing when a line through a and b already exists', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    ensureReferenceLine(scene, a, b);
    const before = scene.objects.size;
    ensureReferenceLine(scene, a, b);
    expect(scene.objects.size).toBe(before);
  });

  it('does nothing when the two ids are the same point', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    const before = scene.objects.size;
    ensureReferenceLine(scene, a, a);
    expect(scene.objects.size).toBe(before);
  });
});

describe('drawReferenceLineOnSlotB', () => {
  it('does nothing when the filled slot is not b', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    const before = scene.objects.size;
    drawReferenceLineOnSlotB('a', { a, b }, scene);
    expect(scene.objects.size).toBe(before);
  });

  it('draws the reference line through bindings a and b once slot b is filled', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    drawReferenceLineOnSlotB('b', { a, b }, scene);
    expect(lineExists(scene, a, b)).toBe(true);
  });
});
