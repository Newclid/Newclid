import type { AppStore } from '../store/appStore';
import type { TheoremStore } from '../store/theoremStore';
import { el } from './dom';
import {
  PREDICATE_DEFINITIONS,
  PREDICATE_BY_ID,
  predicateToJgex,
} from '../types/theorem';
import type { CustomTheorem, TheoremPredicate, PredicateDef } from '../types/theorem';

interface EditablePredicate {
  predicateId: string;
  args: string[];
}

type ManagerView = 'list' | 'builder';
type SectionKind = 'premises' | 'conclusions';

export interface TheoremManagerHandle {
  root: HTMLElement;
  destroy(): void;
}

export function createTheoremManager(
  appStore: AppStore,
  store: TheoremStore,
): TheoremManagerHandle {
  const root = el('div', { class: 'proof-panel' });

  // ---- Mutable state ----
  let view: ManagerView = 'list';
  let editingId: string | null = null;
  let nameVal = '';
  let descVal = '';
  let premises: EditablePredicate[] = [];
  let conclusions: EditablePredicate[] = [];
  let addingTo: SectionKind | null = null;
  let saveError = '';
  // Tracks which saved-theorem cards currently have their JGEX expanded.
  const jgexExpandedCards = new Set<string>();

  // ---- Validation ----

  const THEOREM_NAME_RE = /^[A-Za-z_][A-Za-z0-9_-]*$/;
  const POINT_NAME_RE = /^[A-Za-z]$/;
  // Accepts plain rationals (1/2, 3) and angle constants as fractions of π (pi/4, 11pi/36).
  const FRACTION_RE = /^-?[0-9]+(\/-?[0-9]+)?$|^-?[0-9]*pi\/-?[0-9]+$/;

  function validate(): string | null {
    if (!THEOREM_NAME_RE.test(nameVal.trim())) {
      return 'Name must start with a letter or underscore and contain only letters, digits, underscores, or hyphens (no spaces).';
    }
    if (premises.length === 0) return 'Add at least one premise.';
    if (conclusions.length === 0) return 'Add at least one conclusion.';

    const sections: [string, EditablePredicate[]][] = [
      ['Premise', premises],
      ['Conclusion', conclusions],
    ];
    for (const [sectionLabel, list] of sections) {
      for (const ep of list) {
        const def = PREDICATE_BY_ID.get(ep.predicateId);
        if (!def) return `Unknown predicate: ${ep.predicateId}`;
        for (let i = 0; i < ep.args.length; i++) {
          const val = ep.args[i].trim();
          const type = i < def.argTypes.length ? def.argTypes[i] : 'point';
          if (!val) return `${sectionLabel} "${def.label}": all arguments must be filled.`;
          if (type === 'point' && !POINT_NAME_RE.test(val)) {
            return `${sectionLabel} "${def.label}": point "${val}" must be a single letter (A–Z or a–z).`;
          }
          if (type === 'fraction' && !FRACTION_RE.test(val)) {
            return `${sectionLabel} "${def.label}": constant "${val}" must be an integer or fraction like 1/2.`;
          }
        }
      }
    }
    return null;
  }

  // ---- Navigation ----

  function enterBuilder(theorem?: CustomTheorem): void {
    editingId = theorem?.id ?? null;
    nameVal = theorem?.name ?? '';
    descVal = theorem?.description ?? '';
    premises = theorem?.premises.map((p) => ({ predicateId: p.predicateId, args: [...p.args] })) ?? [];
    conclusions = theorem?.conclusions.map((p) => ({ predicateId: p.predicateId, args: [...p.args] })) ?? [];
    addingTo = null;
    saveError = '';
    view = 'builder';
    render();
  }

  function enterList(): void {
    view = 'list';
    render();
  }

  // ---- Helpers ----

  function toTheoremPredicate(ep: EditablePredicate): TheoremPredicate {
    return { predicateId: ep.predicateId, args: [...ep.args] };
  }

  function defaultArgs(def: PredicateDef): string[] {
    return def.argLabels.map((_, i) =>
      def.argTypes[i] === 'fraction' ? '1' : '',
    );
  }

  // ============================================================
  //  LIST VIEW
  // ============================================================

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
    createBtn.addEventListener('click', () => enterBuilder());
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
    const editBtn = el('button', { type: 'button', class: 'theorem-card-action-btn' }, ['Edit']);
    editBtn.addEventListener('click', () => enterBuilder(theorem));
    actions.appendChild(editBtn);

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

    const showJgex = jgexExpandedCards.has(theorem.id);
    card.appendChild(renderCardPredicateGroup('Premises:', theorem.premises, showJgex));
    card.appendChild(renderCardPredicateGroup('Conclusions:', theorem.conclusions, showJgex));

    const jgexToggle = el('button', {
      type: 'button',
      class: 'theorem-card-jgex-toggle',
    }, [showJgex ? 'Hide JGEX ▲' : 'Show JGEX ▼']);
    jgexToggle.addEventListener('click', () => {
      if (jgexExpandedCards.has(theorem.id)) jgexExpandedCards.delete(theorem.id);
      else jgexExpandedCards.add(theorem.id);
      renderList();
    });
    card.appendChild(jgexToggle);

    return card;
  }

  function renderCardPredicateGroup(
    sectionLabel: string,
    predicates: TheoremPredicate[],
    showJgex: boolean,
  ): HTMLElement {
    const wrap = el('div', { class: 'theorem-card-predicates' });
    wrap.appendChild(el('div', { class: 'theorem-card-pred-label' }, [sectionLabel]));
    for (const pred of predicates) {
      const def = PREDICATE_BY_ID.get(pred.predicateId);
      const humanText = def ? def.shorthand(pred.args) : predicateToJgex(pred);
      const predItem = el('div', { class: 'theorem-card-pred-item' });
      predItem.appendChild(el('span', { class: 'theorem-card-pred-human' }, [humanText]));
      if (showJgex) {
        predItem.appendChild(el('code', { class: 'theorem-card-pred-jgex' }, [predicateToJgex(pred)]));
      }
      wrap.appendChild(predItem);
    }
    return wrap;
  }

  // ============================================================
  //  BUILDER SUBCOMPONENTS
  // ============================================================

  // ---- Predicate picker grid ----

  function renderPredicatePicker(section: SectionKind): HTMLElement {
    const picker = el('div', { class: 'theorem-pred-picker' });
    picker.appendChild(el('div', { class: 'proof-section-title' }, ['Choose predicate:']));

    const grid = el('div', { class: 'goal-pred-grid' });
    for (const def of PREDICATE_DEFINITIONS) {
      const btn = el('button', {
        type: 'button',
        class: 'goal-pred-btn',
        title: def.shorthand([]),
      }) as HTMLButtonElement;
      btn.appendChild(el('span', { class: 'goal-pred-icon' }, [def.icon]));
      btn.appendChild(el('span', { class: 'goal-pred-label' }, [def.label]));
      btn.addEventListener('click', () => {
        const newPred: EditablePredicate = { predicateId: def.id, args: defaultArgs(def) };
        if (section === 'premises') premises.push(newPred);
        else conclusions.push(newPred);
        addingTo = null;
        renderKeepingScroll();
      });
      grid.appendChild(btn);
    }
    picker.appendChild(grid);

    const cancelBtn = el('button', {
      type: 'button',
      class: 'jgex-btn jgex-btn-quiet theorem-picker-cancel',
    }, ['Cancel']);
    cancelBtn.addEventListener('click', () => { addingTo = null; render(); });
    picker.appendChild(cancelBtn);

    return picker;
  }

  // ---- Single arg input row ----

  function renderArgInput(ep: EditablePredicate, def: PredicateDef, argIdx: number): HTMLElement {
    const argType = argIdx < def.argTypes.length ? def.argTypes[argIdx] : 'point';
    const isFraction = argType === 'fraction';
    // Fraction args keep their semantic label (k); point args use the def's semantic name (A, B, …).
    const label = isFraction
      ? (argIdx < def.argLabels.length ? def.argLabels[argIdx] : 'k')
      : (argIdx < def.argLabels.length ? def.argLabels[argIdx] : `P${argIdx + 1}`);

    const row = el('div', { class: 'theorem-arg-row' });
    row.appendChild(el('span', { class: 'theorem-arg-label' }, [label]));

    const isAngle = isFraction && def.id === 'aconst';
    const inputAttrs: Partial<Record<string, string>> = {
      type: 'text',
      class: `theorem-arg-input${isFraction ? ' theorem-arg-input-fraction' : ' theorem-arg-input-point'}`,
      value: ep.args[argIdx] ?? '',
      placeholder: isAngle ? 'pi/4' : (isFraction ? 'e.g. 1/2' : label),
      title: isAngle
        ? 'Angle as a fraction of π: pi/4 = 45°, pi/2 = 90°, pi/3 = 60°, pi/6 = 30°'
        : (isFraction ? 'Rational constant, e.g. 1/2 or 3' : 'Single letter (A–Z or a–z)'),
    };
    if (!isFraction) inputAttrs.maxlength = '1';
    const input = el('input', inputAttrs) as HTMLInputElement;
    input.addEventListener('input', () => {
      if (!isFraction) {
        // Enforce single A–Z / a–z character; strip everything else.
        const filtered = input.value.replace(/[^A-Za-z]/g, '').slice(0, 1);
        if (filtered !== input.value) input.value = filtered;
      }
      ep.args[argIdx] = input.value;
      // Update the header shorthand live so the user sees their variable names reflected.
      const predEl = row.closest('.theorem-editable-pred');
      const nameSpan = predEl?.querySelector('.theorem-editable-pred-name');
      if (nameSpan) nameSpan.textContent = `${def.label} — ${def.shorthand(ep.args)}`;
    });
    row.appendChild(input);
    if (!isFraction) {
      row.appendChild(el('span', { class: 'theorem-arg-hint' }, ['1 letter']));
    }
    if (isAngle) {
      row.appendChild(el('span', { class: 'theorem-arg-unit' }, ['× π rad']));
    }
    return row;
  }

  // ---- Editable predicate row ----

  function renderEditablePredicate(
    ep: EditablePredicate,
    idx: number,
    section: SectionKind,
  ): HTMLElement {
    const def = PREDICATE_BY_ID.get(ep.predicateId);
    if (!def) return el('div', {}, [`Unknown predicate: ${ep.predicateId}`]);

    const row = el('div', { class: 'theorem-editable-pred' });

    // Header: predicate description + delete button
    const header = el('div', { class: 'theorem-editable-pred-header' });
    header.appendChild(
      el('span', { class: 'theorem-editable-pred-name' }, [`${def.label} — ${def.shorthand(ep.args)}`]),
    );
    const delBtn = el('button', {
      type: 'button',
      class: 'goal-slot-clear theorem-pred-delete-btn',
      title: 'Remove predicate',
    }, ['×']);
    delBtn.addEventListener('click', () => {
      const list = section === 'premises' ? premises : conclusions;
      list.splice(idx, 1);
      renderKeepingScroll();
    });
    header.appendChild(delBtn);
    row.appendChild(header);

    // Arg inputs — grouped if the predicate has groups, flat otherwise
    const argsWrap = el('div', { class: 'theorem-args' });
    if (def.groups) {
      let offset = 0;
      for (const group of def.groups) {
        // For circumcenter the "Triangle" group grows dynamically — relabel when > 3 polygon points.
        let groupLabel = group.label;
        if (def.id === 'circumcenter' && group.label === 'Triangle') {
          const polyCount = ep.args.length - 1; // args minus the center point
          if (polyCount > 3) groupLabel = `${polyCount}-gon`;
        }
        argsWrap.appendChild(el('div', { class: 'goal-slot-group-label' }, [groupLabel]));
        const groupEl = el('div', { class: 'goal-slot-group' });
        for (let j = 0; j < group.count && offset + j < ep.args.length; j++) {
          groupEl.appendChild(renderArgInput(ep, def, offset + j));
        }
        argsWrap.appendChild(groupEl);
        offset += group.count;
      }
      // Extra variable args that overflow beyond defined groups
      if (def.variableArgs) {
        const groupedTotal = def.groups.reduce((s, g) => s + g.count, 0);
        for (let i = groupedTotal; i < ep.args.length; i++) {
          argsWrap.appendChild(renderArgInput(ep, def, i));
        }
      }
    } else {
      for (let i = 0; i < ep.args.length; i++) {
        argsWrap.appendChild(renderArgInput(ep, def, i));
      }
    }
    row.appendChild(argsWrap);

    // + / − controls for variable-length predicates (coll, cyclic, circumcenter)
    if (def.variableArgs) {
      const varControls = el('div', { class: 'goal-var-controls' });

      const addArgBtn = el('button', { type: 'button', class: 'goal-var-btn' }, ['+ Add point']);
      addArgBtn.addEventListener('click', () => {
        ep.args.push('');
        renderKeepingScroll();
      });
      varControls.appendChild(addArgBtn);

      if (ep.args.length > def.minArgs) {
        const remArgBtn = el('button', {
          type: 'button',
          class: 'goal-var-btn goal-var-btn-remove',
        }, ['− Remove last']);
        remArgBtn.addEventListener('click', () => { ep.args.pop(); renderKeepingScroll(); });
        varControls.appendChild(remArgBtn);
      }
      row.appendChild(varControls);
    }

    return row;
  }

  // ---- Predicate section (premises or conclusions) ----

  function renderSection(section: SectionKind, predicates: EditablePredicate[]): HTMLElement {
    const wrap = el('div', { class: 'theorem-pred-section' });

    wrap.appendChild(
      el('div', { class: 'proof-section-title' }, [
        section === 'premises' ? 'Premises — Given:' : 'Conclusions — To Prove:',
      ]),
    );

    const listEl = el('div', { class: 'theorem-pred-list' });
    predicates.forEach((ep, idx) => {
      listEl.appendChild(renderEditablePredicate(ep, idx, section));
    });
    wrap.appendChild(listEl);

    if (addingTo === section) {
      wrap.appendChild(renderPredicatePicker(section));
    } else {
      const addBtn = el('button', {
        type: 'button',
        class: 'goal-var-btn theorem-add-pred-btn',
      }, [`+ Add ${section === 'premises' ? 'Premise' : 'Conclusion'}`]);
      addBtn.addEventListener('click', () => { addingTo = section; renderKeepingScroll(); });
      wrap.appendChild(addBtn);
    }

    return wrap;
  }

  // ============================================================
  //  BUILDER VIEW  (name / desc fields + sections — save wired in next commit)
  // ============================================================

  function renderBuilder(): void {
    root.innerHTML = '';

    const backBtn = el('button', { class: 'proof-back-btn', type: 'button' }, ['← Back to list']);
    backBtn.addEventListener('click', () => { addingTo = null; enterList(); });
    root.appendChild(backBtn);

    const content = el('div', { class: 'proof-panel-content' });

    content.appendChild(
      el('div', { class: 'proof-section-title' }, [editingId ? `Edit: ${editingId}` : 'New Theorem']),
    );

    // Name field
    const nameGroup = el('div', { class: 'theorem-field' });
    nameGroup.appendChild(el('label', { class: 'theorem-field-label', for: 'th-name' }, ['Name (unique, no spaces):']));
    const nameInput = el('input', {
      type: 'text',
      id: 'th-name',
      class: 'theorem-field-input',
      value: nameVal,
      placeholder: 'my_theorem',
    }) as HTMLInputElement;
    nameInput.addEventListener('input', () => { nameVal = nameInput.value; });
    nameGroup.appendChild(nameInput);
    content.appendChild(nameGroup);

    // Description field
    const descGroup = el('div', { class: 'theorem-field' });
    descGroup.appendChild(el('label', { class: 'theorem-field-label', for: 'th-desc' }, ['Description (optional):']));
    const descInput = el('textarea', {
      id: 'th-desc',
      class: 'theorem-field-input theorem-field-textarea',
      placeholder: 'Human-readable description…',
    }) as HTMLTextAreaElement;
    descInput.value = descVal;
    descInput.addEventListener('input', () => { descVal = descInput.value; });
    descGroup.appendChild(descInput);
    content.appendChild(descGroup);

    content.appendChild(renderSection('premises', premises));
    content.appendChild(renderSection('conclusions', conclusions));

    root.appendChild(content);

    // ---- Pinned footer (always visible, never scrolls away) ----
    const footer = el('div', { class: 'theorem-builder-footer' });

    if (saveError) {
      const errorBox = el('div', { class: 'theorem-error-box' });
      errorBox.appendChild(el('span', { class: 'theorem-error-icon' }, ['⚠']));
      errorBox.appendChild(el('span', {}, [saveError]));
      footer.appendChild(errorBox);
    }

    const saveBtn = el('button', {
      type: 'button',
      class: 'jgex-btn jgex-btn-accent theorem-save-btn',
    }, ['Save Theorem']) as HTMLButtonElement;
    saveBtn.addEventListener('click', () => {
      const err = validate();
      if (err) { saveError = err; render(); return; }
      store.save({
        id: nameVal.trim(),
        name: nameVal.trim(),
        description: descVal.trim(),
        premises: premises.map(toTheoremPredicate),
        conclusions: conclusions.map(toTheoremPredicate),
      });
      enterList();
    });
    footer.appendChild(saveBtn);

    root.appendChild(footer);
  }

  // ============================================================
  //  MASTER RENDER + LIFECYCLE
  // ============================================================

  function render(): void {
    if (view === 'list') renderList();
    else renderBuilder();
  }

  // Re-render while keeping the scroll position of the content area.
  // Used by add/remove arg buttons so the user stays at the same spot.
  function renderKeepingScroll(): void {
    const scrollTop = root.querySelector('.proof-panel-content')?.scrollTop ?? 0;
    render();
    const content = root.querySelector('.proof-panel-content');
    if (content) content.scrollTop = scrollTop;
  }

  // Reset to list whenever the panel is opened fresh
  let wasOpen = false;
  const unsubAppStore = appStore.subscribe(() => {
    const isOpen = appStore.theoremManagerMode;
    if (isOpen && !wasOpen) { view = 'list'; render(); }
    wasOpen = isOpen;
  });

  const unsubTheorems = store.subscribe(() => {
    if (view === 'list') renderList();
  });

  renderList();

  return {
    root,
    destroy() { unsubAppStore(); unsubTheorems(); },
  };
}

