import { describe, it, expect, beforeEach } from 'vitest';

// Each test re-imports the module fresh so the module-level cache is empty.
// vi.resetModules() is called before each test to ensure isolation.
import { vi } from 'vitest';

describe('getTool', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('returns undefined for an unknown tool name', async () => {
    const { getTool } = await import('../../../src/tools/registry');
    expect(getTool('__nonexistent__')).toBeUndefined();
  });

  it('returns a ConstructionTool instance for a known tool name', async () => {
    const { getTool } = await import('../../../src/tools/registry');
    const { ConstructionTool } = await import('../../../src/tools/construction-tool');
    const tool = getTool('point');
    expect(tool).toBeInstanceOf(ConstructionTool);
  });

  it('returns the same instance on repeated calls (cache hit)', async () => {
    const { getTool } = await import('../../../src/tools/registry');
    const first = getTool('point');
    const second = getTool('point');
    expect(first).toBe(second);
  });

  it('caches different tools independently', async () => {
    const { getTool } = await import('../../../src/tools/registry');
    const pointTool = getTool('point');
    const circleTool = getTool('circle');
    expect(pointTool).not.toBe(circleTool);
    expect(getTool('point')).toBe(pointTool);
    expect(getTool('circle')).toBe(circleTool);
  });
});
