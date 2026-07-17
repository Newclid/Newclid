import { Scene } from '../scene/scene';
import type { ToolName } from '../geometry/types-object';
import { svgEl, iconWrap } from './icon-helpers';
import { el } from './dom';
import { createJgexInput } from './jgexInput';
import { CONSTRUCTION_CATALOG } from '../construction/catalog';
import { TOOL_GROUPS } from '../tools/groups';
import { getTool } from '../tools/registry';
import type { CatalogEntry } from '../construction/catalog-types';
import { AppStore } from '../store/appStore';
import { createProofPanel } from './proofPanel';
import { createProofsList } from './proofsList';
import { createProofByPointsPanel } from './proofByPointsPanel';
import { createTheoremManager } from './theoremManager';
import { theoremStore } from '../store/theoremStore';

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

function theoremIcon(): SVGSVGElement {
  return iconWrap([
    svgEl('path', {
      d: 'M5 4 L5 18 M5 4 Q5 3 6 3 L16 3 Q17 3 17 4 L17 14 Q17 15 16 15 L5 15',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '1.4',
      'stroke-linejoin': 'round',
      'stroke-linecap': 'round',
    }),
    svgEl('path', {
      d: 'M8 7 L13 7 M8 10 L13 10',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '1.4',
      'stroke-linecap': 'round',
    }),
  ]);
}

// Target/crosshair glyph for the "Define Goal" primary action.
function goalIcon(): SVGSVGElement {
  return iconWrap([
    svgEl('circle', {
      cx: '11', cy: '11', r: '7',
      fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5',
    }),
    svgEl('circle', {
      cx: '11', cy: '11', r: '2.5',
      fill: 'currentColor',
    }),
    svgEl('path', {
      d: 'M11 4 L11 6 M11 16 L11 18 M4 11 L6 11 M16 11 L18 11',
      stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linecap': 'round',
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


export interface ToolbarHandle {
  root: HTMLElement;
  destroy(): void;
}

export function createToolbar(
  scene: Scene,
  onCanvasProofSubmit?: (jgex: string) => Promise<void>,
  appStore?: AppStore,
  onJgexTextSubmit?: (jgex: string) => Promise<void>,
): ToolbarHandle {
  const aside = el('aside', { class: 'toolbar' });

  // ---------- brand block ----------
  const brand = el('div', { class: 'toolbar-brand' }, [
    el('span', { class: 'toolbar-brand-mark' }, ['N']),
    el('span', { class: 'toolbar-brand-name' }, ['Newclid']),
  ]);

  // ---------- tool group (grouped / filtered) ----------
  const group = el('div', { class: 'toolbar-group' });

  // Cleared on every render — only holds buttons currently in the DOM.
  const buttons = new Map<ToolName, HTMLButtonElement>();
  // Empty in filtered view, so updateActive skips the has-active pass then.
  let groupBtns = new Map<string, HTMLButtonElement>();

  let activeGroup: string | null = null;

  function makeToolBtn(entry: CatalogEntry): HTMLButtonElement {
    const btn = el('button', {
      type: 'button',
      class: 'tool-btn',
      title: `${entry.label} (${entry.shortcut})`,
      'aria-pressed': 'false',
    }) as HTMLButtonElement;
    btn.appendChild(entry.icon());
    btn.appendChild(el('span', { class: 'tool-btn-label' }, [entry.label]));
    btn.addEventListener('click', () => { getTool(scene.tool)?.onDeactivate?.({ scene }); scene.setTool(entry.name); });
    buttons.set(entry.name, btn);
    return btn;
  }

  function renderGroupedView(): void {
    group.innerHTML = '';
    buttons.clear();
    groupBtns = new Map();

    // Select lives outside any group — it never navigates to a sublist.
    const selectEntry = CONSTRUCTION_CATALOG['select'];
    if (selectEntry) group.appendChild(makeToolBtn(selectEntry));

    group.appendChild(el('div', { class: 'toolbar-sep' }));

    for (const g of TOOL_GROUPS) {
      const btn = el('button', {
        type: 'button',
        class: 'tool-btn tool-group-btn',
        title: g.label,
        'aria-pressed': 'false',
      }) as HTMLButtonElement;
      btn.appendChild(el('span', { class: 'tool-btn-label' }, [g.label]));
      btn.appendChild(el('span', { class: 'tool-group-arrow' }, ['›']));
      btn.addEventListener('click', () => { activeGroup = g.id; appStore?.setLastToolGroup(g.id); appStore?.setActiveToolGroup(g.id); refresh(); });
      group.appendChild(btn);
      groupBtns.set(g.id, btn);
    }
  }

  function renderFilteredView(groupId: string): void {
    group.innerHTML = '';
    buttons.clear();
    groupBtns = new Map();

    const g = TOOL_GROUPS.find((grp) => grp.id === groupId);
    if (!g) { activeGroup = null; renderGroupedView(); return; }

    const back = el('button', {
      type: 'button',
      class: 'tool-btn tool-group-back',
      title: 'Back to all tools',
    }) as HTMLButtonElement;
    back.appendChild(el('span', { class: 'tool-btn-label' }, ['← All tools']));
    back.addEventListener('click', () => { activeGroup = null; appStore?.setLastToolGroup(null); appStore?.setActiveToolGroup(null); refresh(); getTool(scene.tool)?.onDeactivate?.({ scene }); scene.setTool('select'); });
    group.appendChild(back);

    group.appendChild(el('div', { class: 'toolbar-sep' }));

    for (const toolName of g.tools) {
      const entry = CONSTRUCTION_CATALOG[toolName];
      if (!entry) continue;
      group.appendChild(makeToolBtn(entry));
    }
  }

  function refresh(): void {
    if (activeGroup === null) renderGroupedView();
    else renderFilteredView(activeGroup);
    updateActive();
  }

  // ---------- spacer ----------
  const spacer = el('div', { class: 'toolbar-spacer' });

  // ---------- create proof ----------
  const jgex = createJgexInput(onJgexTextSubmit ?? onCanvasProofSubmit);
  const createProofBtn = el('button', {
    type: 'button',
    class: 'tool-btn tool-btn-primary',
    title: 'Define goal visually',
  }) as HTMLButtonElement;
  createProofBtn.appendChild(goalIcon());
  createProofBtn.appendChild(el('span', { class: 'tool-btn-label' }, ['Define Goal']));
  createProofBtn.addEventListener('click', () => appStore?.enterProofByPoints());

  // ---------- advanced options (JGEX + theorems) ----------
  const advancedSection = el('div', { class: 'advanced-section' });
  const advancedToggle = el('button', {
    type: 'button',
    class: 'tool-btn advanced-toggle',
    title: 'Advanced Options',
  }) as HTMLButtonElement;
  advancedToggle.appendChild(el('span', { class: 'tool-btn-label' }, ['Advanced Options']));
  advancedToggle.appendChild(el('span', { class: 'advanced-arrow' }, ['›']));

  const advancedItems = el('div', { class: 'advanced-items' });
  advancedItems.style.display = 'none';

  const jgexAdvBtn = el('button', {
    type: 'button',
    class: 'tool-btn',
    title: 'Define problem using JGEX',
  }) as HTMLButtonElement;
  jgexAdvBtn.appendChild(jgexIcon());
  jgexAdvBtn.appendChild(el('span', { class: 'tool-btn-label' }, ['Define Problem Using JGEX']));
  jgexAdvBtn.addEventListener('click', () => jgex.open());

  const theoremsAdvBtn = el('button', {
    type: 'button',
    class: 'tool-btn',
    title: 'Manage custom theorems',
  }) as HTMLButtonElement;
  theoremsAdvBtn.appendChild(theoremIcon());
  theoremsAdvBtn.appendChild(el('span', { class: 'tool-btn-label' }, ['User-Defined Theorems']));
  theoremsAdvBtn.addEventListener('click', () => appStore?.enterTheoremManager());

  advancedItems.appendChild(jgexAdvBtn);
  advancedItems.appendChild(theoremsAdvBtn);

  advancedToggle.addEventListener('click', () => {
    const isOpen = advancedItems.style.display !== 'none';
    advancedItems.style.display = isOpen ? 'none' : 'flex';
    advancedSection.classList.toggle('is-open', !isOpen);
  });

  advancedSection.appendChild(advancedToggle);
  advancedSection.appendChild(advancedItems);

  // ---------- clear (with confirmation dialog) ----------
  const clearConfirmBackdrop = el('div', { class: 'jgex-backdrop' });
  const clearConfirmDialog = el('div', {
    class: 'jgex-dialog',
    role: 'dialog',
    'aria-modal': 'true',
  }, [
    el('div', { class: 'jgex-title' }, ['Clear canvas?']),
    el('p', { class: 'clear-confirm-msg' }, [
      'This will remove all points, lines, and shapes from the canvas. This action cannot be undone.',
    ]),
    el('div', { class: 'jgex-actions' }, [
      (() => {
        const cancelClear = el('button', { type: 'button', class: 'jgex-btn jgex-btn-quiet' }, ['Cancel']) as HTMLButtonElement;
        cancelClear.addEventListener('click', () => clearConfirmBackdrop.classList.remove('is-open'));
        return cancelClear;
      })(),
      (() => {
        const confirmClear = el('button', { type: 'button', class: 'jgex-btn jgex-btn-danger' }, ['Clear everything']) as HTMLButtonElement;
        confirmClear.addEventListener('click', () => {
          clearConfirmBackdrop.classList.remove('is-open');
          getTool(scene.tool)?.onDeactivate?.({ scene });
          scene.clear();
          const entry = CONSTRUCTION_CATALOG[scene.tool];
          scene.setSlotHint(entry?.slots[0]?.label ?? null);
        });
        return confirmClear;
      })(),
    ]),
  ]);
  clearConfirmBackdrop.appendChild(clearConfirmDialog);
  clearConfirmBackdrop.addEventListener('mousedown', (e) => {
    if (e.target === clearConfirmBackdrop) clearConfirmBackdrop.classList.remove('is-open');
  });
  document.body.appendChild(clearConfirmBackdrop);

  const clearBtn = el('button', {
    type: 'button',
    class: 'tool-btn tool-btn-danger',
    title: 'Clear all',
  }) as HTMLButtonElement;
  clearBtn.appendChild(trashIcon());
  clearBtn.appendChild(el('span', { class: 'tool-btn-label' }, ['Clear']));
  clearBtn.addEventListener('click', () => clearConfirmBackdrop.classList.add('is-open'));

  // ---------- proof panel ----------
  const proofPanel = appStore ? createProofPanel(appStore) : null;

  // ---------- proof-by-points plane ----------
  const proofByPointsPanel = appStore
    ? createProofByPointsPanel(appStore, scene, onCanvasProofSubmit)
    : null;

  // ---------- theorem manager panel ----------
  const theoremManagerPanel = appStore
    ? createTheoremManager(appStore, theoremStore)
    : null;

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
  }, ['My Solutions']) as HTMLButtonElement;
  panelTabSwitch.appendChild(toolbarTabBtn);
  panelTabSwitch.appendChild(proofsTabBtn);
  toolbarTabBtn.addEventListener('click', () => {
    if (appStore?.lastToolGroup) {
      activeGroup = appStore.lastToolGroup;
      refresh();
    }
    appStore?.setActiveToolGroup(activeGroup);
    appStore?.setPanelTab('toolbar');
  });
  proofsTabBtn.addEventListener('click', () => {
    appStore?.setActiveToolGroup(null);
    appStore?.setPanelTab('proofs');
  });

  // Proofs-tab history list.
  const proofsContent = el('section', { class: 'panel-proofs' });
  const proofsList = appStore ? createProofsList(appStore) : null;
  if (proofsList) {
    proofsContent.appendChild(proofsList.root);
  }

  // Separator between primary action and the tool navigation tabs.
  const primarySep = el('div', { class: 'toolbar-sep' });
  // Separator above the tab switch at the bottom.
  const tabSep = el('div', { class: 'toolbar-sep' });

  const toolElements = [
    createProofBtn, primarySep,
    group, proofsContent, spacer, tabSep, panelTabSwitch,
    advancedSection, clearBtn,
  ];

  const syncPanelState = () => {
    if (!appStore) return;
    const showProof = appStore.proofMode;
    const showPoints = appStore.proofByPointsMode;
    const showTheorems = appStore.theoremManagerMode;
    const anyFullPanel = showProof || showPoints || showTheorems;
    const inToolbarTab = appStore.panelTab === 'toolbar';

    // Tool elements hide whenever any full-panel mode is active.
    for (const node of toolElements) {
      node.style.display = anyFullPanel ? 'none' : '';
    }
    if (proofPanel) {
      proofPanel.root.style.display = showProof ? '' : 'none';
    }
    if (proofByPointsPanel) {
      proofByPointsPanel.root.style.display = showPoints ? '' : 'none';
    }
    if (theoremManagerPanel) {
      theoremManagerPanel.root.style.display = showTheorems ? '' : 'none';
    }
    if (!anyFullPanel) {
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
  aside.appendChild(createProofBtn);
  aside.appendChild(primarySep);
  aside.appendChild(group);
  aside.appendChild(proofsContent);
  aside.appendChild(spacer);
  aside.appendChild(tabSep);
  aside.appendChild(panelTabSwitch);
  aside.appendChild(advancedSection);
  aside.appendChild(clearBtn);
  if (proofPanel) {
    proofPanel.root.style.display = 'none';
    aside.appendChild(proofPanel.root);
  }
  if (proofByPointsPanel) {
    proofByPointsPanel.root.style.display = 'none';
    aside.appendChild(proofByPointsPanel.root);
  }
  if (theoremManagerPanel) {
    theoremManagerPanel.root.style.display = 'none';
    aside.appendChild(theoremManagerPanel.root);
  }

  // ---------- subscription ----------
  let lastToolSeen = '';
  const updateActive = () => {
    for (const [name, btn] of buttons) {
      const active = name === scene.tool;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-pressed', active ? 'true' : 'false');
    }

    for (const [groupId, btn] of groupBtns) {
      const g = TOOL_GROUPS.find((grp) => grp.id === groupId);
      const containsActive = g ? g.tools.includes(scene.tool) : false;
      btn.classList.toggle('has-active', containsActive);
    }

    if (scene.tool !== lastToolSeen) {
      lastToolSeen = scene.tool;
      const entry = CONSTRUCTION_CATALOG[scene.tool];
      scene.setSlotHint(entry?.slots[0]?.label ?? null);
    }
  };
  refresh();
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
      theoremManagerPanel?.destroy();
      proofsList?.destroy();
      jgex.destroy();
      clearConfirmBackdrop.remove();
    },
  };
}
