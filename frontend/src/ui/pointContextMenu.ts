import type { Scene } from '../scene/scene';

export function createPointContextMenu(scene: Scene, container: HTMLElement, requestRedraw: () => void) {
  let menuEl: HTMLElement | null = null;

  function show(pointId: string, x: number, y: number): void {
    dismiss();
    const point = scene.objects.get(pointId);
    if (!point || point.kind !== 'point') return;

    menuEl = document.createElement('div');
    menuEl.className = 'point-context-menu';
    menuEl.style.left = `${x}px`;
    menuEl.style.top = `${y}px`;

    const renameBtn = document.createElement('button');
    renameBtn.textContent = 'Rename point';
    renameBtn.addEventListener('click', () => startRename(pointId, x, y));
    menuEl.appendChild(renameBtn);

    const removeBtn = document.createElement('button');
    removeBtn.textContent = 'Remove point';
    removeBtn.addEventListener('click', () => {
      const before = scene.snapshot();
      scene.removeObject(pointId);
      scene.pushUndo(before);
      requestRedraw();
      dismiss();
    });
    menuEl.appendChild(removeBtn);

    container.appendChild(menuEl);

    // Clamp to container bounds after render
    requestAnimationFrame(() => {
      if (!menuEl) return;
      const cr = container.getBoundingClientRect();
      const mr = menuEl.getBoundingClientRect();
      if (mr.right > cr.right) menuEl.style.left = `${x - (mr.right - cr.right)}px`;
      if (mr.bottom > cr.bottom) menuEl.style.top = `${y - mr.height}px`;
    });

    setTimeout(() => document.addEventListener('click', onOutsideClick, { once: true }));
  }

  function startRename(pointId: string, x: number, y: number): void {
    dismiss();
    const point = scene.objects.get(pointId);
    if (!point || point.kind !== 'point') return;

    const inputEl = document.createElement('input');
    inputEl.type = 'text';
    inputEl.className = 'point-rename-input';
    inputEl.value = point.label;
    inputEl.style.left = `${x}px`;
    inputEl.style.top = `${y}px`;
    container.appendChild(inputEl);
    inputEl.focus();
    inputEl.select();

    let done = false;
    const commit = () => {
      if (done) return;
      done = true;
      const newLabel = inputEl.value.trim();
      if (newLabel && newLabel !== point.label) {
        const before = scene.snapshot();
        scene.renamePoint(pointId, newLabel);
        scene.pushUndo(before);
      }
      inputEl.remove();
      requestRedraw();
    };

    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') commit();
      if (e.key === 'Escape') { done = true; inputEl.remove(); }
    });
    inputEl.addEventListener('blur', commit);
  }

  function dismiss(): void {
    menuEl?.remove();
    menuEl = null;
    document.removeEventListener('click', onOutsideClick);
  }

  function onOutsideClick(): void { dismiss(); }

  return { show, dismiss };
}
