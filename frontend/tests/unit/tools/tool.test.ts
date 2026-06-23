import { describe, it, expect } from 'vitest';
import type { Tool, ToolContext, ToolSnapshot, ToolPreview } from '../../../src/tools/tool';

describe('tool types', () => {
  it('ToolSnapshot shape is usable', () => {
    const snap: ToolSnapshot = { bindings: { a: 'p1' as never }, currentSlotIndex: 1, createdInSlots: ['p2' as never] };
    expect(snap.currentSlotIndex).toBe(1);
  });

  it('ToolPreview union discriminates on kind', () => {
    const previews: ToolPreview[] = [
      { kind: 'highlightPoint', pos: { x: 0, y: 0 } },
      { kind: 'rubberCircle', center: { x: 0, y: 0 }, radiusVec: { x: 1, y: 0 } },
      { kind: 'auxLine', from: { x: 0, y: 0 }, to: { x: 1, y: 1 } },
      { kind: 'partialEdge', from: { x: 0, y: 0 }, to: { x: 1, y: 1 } },
      { kind: 'selectHoverPoint', pos: { x: 0, y: 0 }, pointId: 'p1' },
    ];
    expect(previews.map(p => p.kind)).toEqual([
      'highlightPoint', 'rubberCircle', 'auxLine', 'partialEdge', 'selectHoverPoint',
    ]);
  });

  it('Tool interface is structurally satisfied', () => {
    const tool: Tool = {
      name: 'point' as never,
      onClick: (_ctx: ToolContext) => {},
      onMove: (_ctx: ToolContext) => [],
      onDeactivate: (_ctx) => {},
    };
    expect(tool.name).toBe('point');
  });
});
