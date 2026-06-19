// Shared fake-handle shape for toolbar.ts's child panel factories
// (createProofPanel, createProofsList, createProofByPointsPanel,
// createTheoremManager, createJgexInput, createProofChoice). All of them
// return an object exposing at least `root` + `destroy()`. The dialog-style
// ones (jgexInput, proofChoice) add `open()`/`close()`.
import { vi } from 'vitest';

export interface FakePanelHandle {
  root: HTMLElement;
  destroy: ReturnType<typeof vi.fn>;
}

export interface FakeDialogHandle extends FakePanelHandle {
  open: ReturnType<typeof vi.fn>;
  close: ReturnType<typeof vi.fn>;
}

export function makeFakePanelHandle(): FakePanelHandle {
  return {
    root: document.createElement('div'),
    destroy: vi.fn(),
  };
}

export function makeFakeDialogHandle(): FakeDialogHandle {
  return {
    root: document.createElement('div'),
    open: vi.fn(),
    close: vi.fn(),
    destroy: vi.fn(),
  };
}
