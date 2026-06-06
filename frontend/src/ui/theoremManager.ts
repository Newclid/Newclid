import type { AppStore } from '../store/appStore';
import type { TheoremStore } from '../store/theoremStore';
import { el } from './dom';
import { predicateToJgex } from '../types/theorem';
import type { CustomTheorem, TheoremPredicate } from '../types/theorem';

export interface TheoremManagerHandle {
  root: HTMLElement;
  destroy(): void;
}

export function createTheoremManager(
  appStore: AppStore,
  store: TheoremStore,
): TheoremManagerHandle {
  const root = el('div', { class: 'proof-panel' });

  // ---- Render: list view ----

  function renderList(): void {
    root.innerHTML = '';

    const backBtn = el('button', { class: 'proof-back-btn', type: 'button' }, ['← Back to toolbar']);
    backBtn.addEventListener('click', () => appStore.exitTheoremManager());
    root.appendChild(backBtn);

    const content = el('div', { class: 'proof-panel-content' });

    const listHeader = el('div', { class: 'theorem-list-header' });
    listHeader.appendChild(el('div', { class: 'proof-section-title' }, ['Custom Theorems']));
    const createBtn = el('button', {
      type: 'button',
      class: 'jgex-btn jgex-btn-accent theorem-create-btn',
    }, ['+ Create New']);
    createBtn.disabled = true;
    createBtn.title = 'Theorem builder — coming soon';
    listHeader.appendChild(createBtn);
    content.appendChild(listHeader);

    const theorems = store.getAll();
    if (theorems.length === 0) {
      content.appendChild(el('p', { class: 'proofs-list-empty' }, ['No custom theorems saved yet.']));
    } else {
      const list = el('div', { class: 'theorem-saved-list' });
      for (const theorem of theorems) {
        list.appendChild(renderCard(theorem));
      }
      content.appendChild(list);
    }

    root.appendChild(content);
  }

  function renderCard(theorem: CustomTheorem): HTMLElement {
    const card = el('div', { class: 'theorem-saved-card' });

    const cardHeader = el('div', { class: 'theorem-card-header' });
    cardHeader.appendChild(el('span', { class: 'theorem-card-name' }, [theorem.name]));

    const actions = el('div', { class: 'theorem-card-actions' });
    const deleteBtn = el('button', {
      type: 'button',
      class: 'theorem-card-action-btn theorem-card-delete-btn',
    }, ['Delete']);
    deleteBtn.addEventListener('click', () => { store.remove(theorem.id); renderList(); });
    actions.appendChild(deleteBtn);
    cardHeader.appendChild(actions);
    card.appendChild(cardHeader);

    if (theorem.description) {
      card.appendChild(el('p', { class: 'theorem-card-desc' }, [theorem.description]));
    }

    card.appendChild(renderCardPredicateGroup('Premises:', theorem.premises));
    card.appendChild(renderCardPredicateGroup('Conclusions:', theorem.conclusions));

    return card;
  }

  function renderCardPredicateGroup(
    sectionLabel: string,
    predicates: TheoremPredicate[],
  ): HTMLElement {
    const wrap = el('div', { class: 'theorem-card-predicates' });
    wrap.appendChild(el('div', { class: 'theorem-card-pred-label' }, [sectionLabel]));
    for (const p of predicates) {
      wrap.appendChild(el('code', { class: 'theorem-card-pred' }, [predicateToJgex(p)]));
    }
    return wrap;
  }

  // ---- Re-open resets to list ----

  let wasOpen = false;
  const unsubAppStore = appStore.subscribe(() => {
    const isOpen = appStore.theoremManagerMode;
    if (isOpen && !wasOpen) renderList();
    wasOpen = isOpen;
  });

  const unsubTheorems = store.subscribe(() => renderList());

  renderList();

  return {
    root,
    destroy() { unsubAppStore(); unsubTheorems(); },
  };
}
