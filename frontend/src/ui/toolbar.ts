// Left-side toolbar. The `tools` array is the single source of truth
// for the button list; the toolbar subscribes to the scene and updates
// the active-state styling when `scene.tool` changes.

import { Scene } from '../scene/scene';
import type { ToolName } from '../geometry/types-object';

// Tiny declarative element factory.
function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  attrs: Partial<Record<string, string>> = {},
  children: (Node | string)[] = [],
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined) continue;
    if (k === 'class') node.className = v;
    else node.setAttribute(k, v);
  }
  for (const c of children) {
    node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  }
  return node;
}

const SVG_NS = 'http://www.w3.org/2000/svg';

function svgEl(tag: string, attrs: Record<string, string>, text?: string): SVGElement {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  if (text !== undefined) node.textContent = text;
  return node;
}

// Each icon is a function returning a fresh <svg> element. SVG nodes
// can't be reused in two places in the DOM, so a cached node would
// break the moment a second button referenced it.
function iconWrap(children: SVGElement[]): SVGSVGElement {
  const svg = document.createElementNS(SVG_NS, 'svg') as SVGSVGElement;
  svg.setAttribute('viewBox', '0 0 22 22');
  svg.setAttribute('width', '22');
  svg.setAttribute('height', '22');
  svg.setAttribute('aria-hidden', 'true');
  for (const c of children) svg.appendChild(c);
  return svg;
}

function cursorIcon(): SVGSVGElement {
  return iconWrap([
    svgEl('path', {
      d: 'M5 4 L5 18 L9 14 L11.5 19 L13.5 18 L11 13 L16 13 Z',
      fill: 'currentColor',
      stroke: 'currentColor',
      'stroke-width': '1',
      'stroke-linejoin': 'round',
    }),
  ]);
}

function pointIcon(): SVGSVGElement {
  return iconWrap([
    svgEl('circle', { cx: '11', cy: '11', r: '3', fill: 'currentColor' }),
    svgEl(
      'text',
      {
        x: '15',
        y: '9',
        'font-family': 'var(--font-display)',
        'font-style': 'italic',
        'font-size': '9',
        fill: 'currentColor',
      },
      'A',
    ),
  ]);
}

function trashIcon(): SVGSVGElement {
  return iconWrap([
    svgEl('path', {
      d:
        'M6 7 L6 17 Q6 18.5 7.5 18.5 L14.5 18.5 Q16 18.5 16 17 L16 7 ' +
        'M4.5 7 L17.5 7 ' +
        'M9 5 L13 5 Q13.5 5 13.5 5.5 L13.5 7 L8.5 7 L8.5 5.5 Q8.5 5 9 5 Z',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '1.4',
      'stroke-linejoin': 'round',
      'stroke-linecap': 'round',
    }),
  ]);
}

interface ToolEntry {
  name: ToolName;
  label: string;
  shortcut: string;
  icon: () => SVGSVGElement;
}

const tools: ToolEntry[] = [
  { name: 'select', label: 'Select', shortcut: 'V', icon: cursorIcon },
  { name: 'point', label: 'Point', shortcut: 'P', icon: pointIcon },
];

export interface ToolbarHandle {
  root: HTMLElement;
  destroy(): void;
}

export function createToolbar(scene: Scene): ToolbarHandle {
  const aside = el('aside', { class: 'toolbar' });

  // ---------- brand block ----------
  const brand = el('div', { class: 'toolbar-brand' }, [
    el('span', { class: 'toolbar-brand-mark' }, ['N']),
    el('span', { class: 'toolbar-brand-name' }, ['Newclid']),
  ]);

  // ---------- tool group ----------
  const group = el('div', { class: 'toolbar-group' });
  // Map from tool name to button so updateActive() doesn't query the DOM.
  const buttons = new Map<ToolName, HTMLButtonElement>();
  for (const t of tools) {
    const btn = el('button', {
      type: 'button',
      class: 'tool-btn',
      title: `${t.label} (${t.shortcut})`,
      'aria-pressed': 'false',
    }) as HTMLButtonElement;
    btn.appendChild(t.icon());
    btn.appendChild(el('span', { class: 'tool-btn-label' }, [t.label]));
    btn.appendChild(el('span', { class: 'tool-btn-key' }, [t.shortcut]));
    btn.addEventListener('click', () => scene.setTool(t.name));
    group.appendChild(btn);
    buttons.set(t.name, btn);
  }

  // ---------- spacer ----------
  const spacer = el('div', { class: 'toolbar-spacer' });

  // ---------- clear ----------
  const clearBtn = el('button', {
    type: 'button',
    class: 'tool-btn tool-btn-danger',
    title: 'Clear all',
  }) as HTMLButtonElement;
  clearBtn.appendChild(trashIcon());
  clearBtn.appendChild(el('span', { class: 'tool-btn-label' }, ['Clear']));
  clearBtn.addEventListener('click', () => scene.clear());

  // ---------- assemble ----------
  aside.appendChild(brand);
  aside.appendChild(group);
  aside.appendChild(spacer);
  aside.appendChild(clearBtn);

  // ---------- subscription ----------
  const updateActive = () => {
    for (const [name, btn] of buttons) {
      const active = name === scene.tool;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-pressed', active ? 'true' : 'false');
    }
  };
  updateActive();
  const unsubscribe = scene.subscribe(updateActive);

  return {
    root: aside,
    destroy() {
      unsubscribe();
    },
  };
}
