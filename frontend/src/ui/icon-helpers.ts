// SVG-icon helpers shared by toolbar.ts and catalog entries.
// Extracted from toolbar.ts so construction entries can build icons
// in the same style as built-in tools.

export const SVG_NS = 'http://www.w3.org/2000/svg';

export function svgEl(tag: string, attrs: Record<string, string>, text?: string): SVGElement {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  if (text !== undefined) node.textContent = text;
  return node;
}

/**
Icons are functions returning a fresh <svg>: SVG nodes can't be reused
in two DOM places, so a cached node would break on the second button.
**/
export function iconWrap(children: SVGElement[]): SVGSVGElement {
  const svg = document.createElementNS(SVG_NS, 'svg') as SVGSVGElement;
  svg.setAttribute('viewBox', '0 0 22 22');
  svg.setAttribute('width', '22');
  svg.setAttribute('height', '22');
  svg.setAttribute('aria-hidden', 'true');
  for (const c of children) svg.appendChild(c);
  return svg;
}
