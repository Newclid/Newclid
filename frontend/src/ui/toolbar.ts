import { Scene } from '../scene/scene';
import type { ToolName } from '../geometry/types-object';
import { svgEl, iconWrap } from './icon-helpers';
import { el } from './dom';
import { createJgexInput } from './jgexInput';
import { CONSTRUCTION_CATALOG } from '../construction/catalog';
import { AppStore } from '../store/appStore';
import { createProofPanel } from './proofPanel';
import { createProofsList } from './proofsList';
import { createProofChoice } from './proofChoice';
import { createProofByPointsPanel } from './proofByPointsPanel';

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

function circleIcon(): SVGSVGElement {
  return iconWrap([
    svgEl('circle', {
      cx: '11',
      cy: '11',
      r: '8',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '1.6',
    }),
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

// Angle-brackets glyph, so the button reads as "type code".
function jgexIcon(): SVGSVGElement {
  return iconWrap([
    svgEl('path', {
      d: 'M8 6 L3.5 11 L8 16 M14 6 L18.5 11 L14 16',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '1.5',
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
  { name: 'circle', label: 'Circle', shortcut: 'C', icon: circleIcon },
];

for (const entry of Object.values(CONSTRUCTION_CATALOG)) {
  tools.push({
    name: entry.name,
    label: entry.label,
    shortcut: entry.shortcut,
    icon: entry.icon,
  });
}

export interface ToolbarHandle {
  root: HTMLElement;
  destroy(): void;
}

export function createToolbar(
  scene: Scene,
  onJgexSubmit?: (jgex: string) => Promise<void>,
  appStore?: AppStore,
): ToolbarHandle {
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

  // ---------- create proof ----------
  // The JGEX input still exists; it is now reached through the choice modal.
  const jgex = createJgexInput(onJgexSubmit);
  const proofChoice = createProofChoice({
    onJgex: () => jgex.open(),
    onPoints: () => appStore?.enterProofByPoints(),
  });
  const createProofBtn = el('button', {
    type: 'button',
    class: 'tool-btn',
    title: 'Create a proof',
  }) as HTMLButtonElement;
  createProofBtn.appendChild(jgexIcon());
  createProofBtn.appendChild(el('span', { class: 'tool-btn-label' }, ['Create proof']));
  createProofBtn.addEventListener('click', () => proofChoice.open());

  // ---------- clear ----------
  const clearBtn = el('button', {
    type: 'button',
    class: 'tool-btn tool-btn-danger',
    title: 'Clear all',
  }) as HTMLButtonElement;
  clearBtn.appendChild(trashIcon());
  clearBtn.appendChild(el('span', { class: 'tool-btn-label' }, ['Clear']));
  clearBtn.addEventListener('click', () => scene.clear());

  // ---------- proof panel ----------
  const proofPanel = appStore ? createProofPanel(appStore) : null;

  // ---------- proof-by-points plane (placeholder) ----------
  const proofByPointsPanel = appStore ? createProofByPointsPanel(appStore) : null;

  // Shown in the tools panel when a result exists but proof view is closed.
  const viewProofBtn = el('button', {
    type: 'button',
    class: 'tool-btn',
    title: 'View proof results',
  }) as HTMLButtonElement;
  viewProofBtn.appendChild(el('span', { class: 'tool-btn-label' }, ['View proof']));
  viewProofBtn.addEventListener('click', () => appStore?.enterProofMode());

  // ---------- panel tab switch (Toolbar | Proofs) ----------
  const panelTabSwitch = el('div', {
    class: 'panel-tab-switch',
    role: 'tablist',
  });
  const toolbarTabBtn = el('button', {
    type: 'button',
    class: 'panel-tab-btn',
    role: 'tab',
    'aria-selected': 'true',
  }, ['Toolbar']) as HTMLButtonElement;
  const proofsTabBtn = el('button', {
    type: 'button',
    class: 'panel-tab-btn',
    role: 'tab',
    'aria-selected': 'false',
  }, ['Proofs']) as HTMLButtonElement;
  panelTabSwitch.appendChild(toolbarTabBtn);
  panelTabSwitch.appendChild(proofsTabBtn);
  toolbarTabBtn.addEventListener('click', () => appStore?.setPanelTab('toolbar'));
  proofsTabBtn.addEventListener('click', () => appStore?.setPanelTab('proofs'));

  // Proofs-tab history list.
  const proofsContent = el('section', { class: 'panel-proofs' });
  const proofsList = appStore ? createProofsList(appStore) : null;
  if (proofsList) {
    proofsContent.appendChild(proofsList.root);
  }

  const toolElements = [group, proofsContent, spacer, panelTabSwitch, createProofBtn, clearBtn];

  const syncPanelState = () => {
    if (!appStore) return;
    const showProof = appStore.proofMode;
    const showPoints = appStore.proofByPointsMode;
    const inToolbarTab = appStore.panelTab === 'toolbar';

    // Tool elements hide whenever either full-panel mode is active.
    for (const node of toolElements) {
      node.style.display = showProof || showPoints ? 'none' : '';
    }
    if (proofPanel) {
      proofPanel.root.style.display = showProof ? '' : 'none';
    }
    if (proofByPointsPanel) {
      proofByPointsPanel.root.style.display = showPoints ? '' : 'none';
    }
    // Show "View proof" only when editing and there's a result to return to.
    viewProofBtn.style.display =
      !showProof && !showPoints && appStore.activeJobId !== null ? '' : 'none';

    if (!showProof && !showPoints) {
      group.style.display = inToolbarTab ? '' : 'none';
      proofsContent.style.display = inToolbarTab ? 'none' : '';
      // In the Proofs tab the list fills the space, so the spacer is not needed.
      spacer.style.display = inToolbarTab ? '' : 'none';
    }

    toolbarTabBtn.classList.toggle('is-active', inToolbarTab);
    proofsTabBtn.classList.toggle('is-active', !inToolbarTab);
    toolbarTabBtn.setAttribute('aria-selected', inToolbarTab ? 'true' : 'false');
    proofsTabBtn.setAttribute('aria-selected', inToolbarTab ? 'false' : 'true');
  };

  // ---------- assemble ----------
  aside.appendChild(brand);
  aside.appendChild(viewProofBtn);
  aside.appendChild(group);
  aside.appendChild(proofsContent);
  aside.appendChild(spacer);
  aside.appendChild(panelTabSwitch);
  aside.appendChild(createProofBtn);
  aside.appendChild(clearBtn);
  if (proofPanel) {
    proofPanel.root.style.display = 'none';
    aside.appendChild(proofPanel.root);
  }
  if (proofByPointsPanel) {
    proofByPointsPanel.root.style.display = 'none';
    aside.appendChild(proofByPointsPanel.root);
  }

  // ---------- subscription ----------
  const updateActive = () => {
    for (const [name, btn] of buttons) {
      const active = name === scene.tool;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-pressed', active ? 'true' : 'false');
    }
  };
  updateActive();
  const unsubscribeScene = scene.subscribe(updateActive);
  const unsubscribeStore = appStore ? appStore.subscribe(syncPanelState) : undefined;

  syncPanelState();

  return {
    root: aside,
    destroy() {
      unsubscribeScene();
      unsubscribeStore?.();
      proofPanel?.destroy();
      proofByPointsPanel?.destroy();
      proofsList?.destroy();
      proofChoice.destroy();
      jgex.destroy();
    },
  };
}
