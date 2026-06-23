import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('../../../src/tools/registry', () => ({
  getTool: vi.fn(() => undefined),
}));

describe('shortcuts module init – collision warning', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it('warns when two entries share the same shortcut key', async () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.doMock('../../../src/construction/catalog', () => ({
      CONSTRUCTION_CATALOG: {
        tool_a: { name: 'tool_a', shortcut: 'x' },
        tool_b: { name: 'tool_b', shortcut: 'x' },
      },
    }));
    await import('../../../src/input/shortcuts');
    expect(warn).toHaveBeenCalledWith(expect.stringContaining('Shortcut collision'));
    warn.mockRestore();
  });
});
