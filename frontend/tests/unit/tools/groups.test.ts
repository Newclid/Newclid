import { describe, it, expect } from 'vitest';
import { TOOL_GROUPS } from '../../../src/tools/groups';

describe('TOOL_GROUPS', () => {
  it('is non-empty', () => {
    expect(TOOL_GROUPS.length).toBeGreaterThan(0);
  });

  it('every group has id, label, and at least one tool', () => {
    for (const g of TOOL_GROUPS) {
      expect(typeof g.id).toBe('string');
      expect(typeof g.label).toBe('string');
      expect(g.tools.length).toBeGreaterThan(0);
    }
  });

  it('contains expected top-level group ids', () => {
    const ids = TOOL_GROUPS.map(g => g.id);
    expect(ids).toContain('points');
    expect(ids).toContain('lines');
    expect(ids).toContain('circles');
    expect(ids).toContain('triangles');
    expect(ids).toContain('quads');
    expect(ids).toContain('transforms');
  });

  it('intersection_lc appears in both lines and circles groups', () => {
    const lines = TOOL_GROUPS.find(g => g.id === 'lines')!;
    const circles = TOOL_GROUPS.find(g => g.id === 'circles')!;
    expect(lines.tools).toContain('intersection_lc');
    expect(circles.tools).toContain('intersection_lc');
  });
});
