import type { ToolName } from '../geometry/types-object';

export interface ToolGroup {
  id: string;
  label: string;
  tools: ToolName[];
}

/**
 * A tool can appear in more than one group — intersection_lc is intentionally
 * in both Lines and Circles because it belongs to both categories.
 * To add a new entry: register it in catalog.ts, then drop its name here.
 */
export const TOOL_GROUPS: ToolGroup[] = [
  {
    id: 'points',
    label: 'Points',
    tools: ['point', 'midpoint', 'foot', 'on_circle', 'on_line'],
  },
  {
    id: 'lines',
    label: 'Lines',
    tools: ['line', 'segment', 'parallel', 'perpendicular', 'angle_bisector', 'eqdistance', 'foot', 'intersection_ll', 'intersection_lc'],
  },
  {
    id: 'circles',
    label: 'Circles',
    tools: ['circle', 'circumcircle', 'lc_tangent', 'intersection_cc', 'intersection_lc'],
  },
  {
    id: 'triangles',
    label: 'Triangles',
    tools: ['eq_triangle', 'iso_triangle'],
  },
  {
    id: 'quads',
    label: 'Quads',
    tools: ['parallelogram', 'rectangle'],
  },
  {
    id: 'transforms',
    label: 'Transforms',
    tools: ['mirror', 'angle_mirror', 'on_aline'],
  },
];
