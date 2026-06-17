import { describe, it, expect, vi, beforeEach } from 'vitest';
import { makeFakePanelHandle, makeFakeDialogHandle } from '../../helpers/toolbarChildMocks';

// Toolbar's child UI factories are mocked so this file exercises only the
// toolbar's own wiring (per tests/README.md: "replace external collaborators
// with fakes, stubs or mocks"). Scene/AppStore/CONSTRUCTION_CATALOG/TOOL_GROUPS
// are real, they're cheap, synchronous, dependency-free state/data.
vi.mock('../../../src/ui/jgexInput', () => ({
  createJgexInput: vi.fn(() => makeFakeDialogHandle()),
}));
vi.mock('../../../src/ui/proofPanel', () => ({
  createProofPanel: vi.fn(() => makeFakePanelHandle()),
}));
vi.mock('../../../src/ui/proofsList', () => ({
  createProofsList: vi.fn(() => makeFakePanelHandle()),
}));
vi.mock('../../../src/ui/proofChoice', () => ({
  createProofChoice: vi.fn(() => makeFakeDialogHandle()),
}));
vi.mock('../../../src/ui/proofByPointsPanel', () => ({
  createProofByPointsPanel: vi.fn(() => makeFakePanelHandle()),
}));
vi.mock('../../../src/ui/theoremManager', () => ({
  createTheoremManager: vi.fn(() => makeFakePanelHandle()),
}));
vi.mock('../../../src/store/theoremStore', () => ({
  theoremStore: { getAll: vi.fn(() => []) },
}));

import { createToolbar } from '../../../src/ui/toolbar';
import { Scene } from '../../../src/scene/scene';
import { AppStore } from '../../../src/store/appStore';
import { CONSTRUCTION_CATALOG } from '../../../src/construction/catalog';
import { TOOL_GROUPS } from '../../../src/tools/groups';
import { createProofPanel } from '../../../src/ui/proofPanel';
import { createProofByPointsPanel } from '../../../src/ui/proofByPointsPanel';
import { createTheoremManager } from '../../../src/ui/theoremManager';

// Find a tool/group/back button in `group` by the text of its `.tool-btn-label` span.
function findButtonByLabel(root: ParentNode, label: string): HTMLButtonElement | undefined {
  return Array.from(root.querySelectorAll('button')).find(
    (b) => b.querySelector('.tool-btn-label')?.textContent === label,
  ) as HTMLButtonElement | undefined;
}

describe('createToolbar', () => {
  let scene: Scene;
  let appStore: AppStore;

  beforeEach(() => {
    scene = new Scene();
    appStore = new AppStore();
    vi.clearAllMocks();
  });

  describe('initial render (grouped view)', () => {
    // sanity check that createToolbar mounts the right element with the right class
    it('renders an aside.toolbar root element', () => {
      const { root } = createToolbar(scene);
      expect(root.tagName).toBe('ASIDE');
      expect(root.classList.contains('toolbar')).toBe(true);
    });

    // select lives outside any group so it should always be there
    it('renders a select tool button in the grouped view', () => {
      const { root } = createToolbar(scene);
      expect(findButtonByLabel(root, CONSTRUCTION_CATALOG['select'].label)).toBeTruthy();
    });

    // keeps the grouped view honest against the TOOL_GROUPS data
    it('renders one tool-group-btn per TOOL_GROUPS entry', () => {
      const { root } = createToolbar(scene);
      const groupBtns = root.querySelectorAll('.tool-group-btn');
      expect(groupBtns.length).toBe(TOOL_GROUPS.length);
      for (const g of TOOL_GROUPS) {
        expect(findButtonByLabel(root, g.label)).toBeTruthy();
      }
    });

    // panels are optional, skipping appStore should skip building them too
    it('does not create proofPanel/proofByPointsPanel/theoremManagerPanel when appStore is omitted', () => {
      createToolbar(scene);
      expect(createProofPanel).not.toHaveBeenCalled();
      expect(createProofByPointsPanel).not.toHaveBeenCalled();
      expect(createTheoremManager).not.toHaveBeenCalled();
    });

    // passing appStore should wire up every optional panel with the right args
    it('creates proofPanel, proofByPointsPanel, and theoremManagerPanel when appStore is provided', () => {
      createToolbar(scene, undefined, appStore);
      expect(createProofPanel).toHaveBeenCalledWith(appStore);
      expect(createProofByPointsPanel).toHaveBeenCalledWith(appStore, scene, undefined);
      expect(createTheoremManager).toHaveBeenCalled();
    });
  });

  describe('tool group navigation', () => {
    // group buttons are a one-way door into that group's filtered tool list
    it('clicking a tool-group-btn switches to the filtered view for that group', () => {
      const { root } = createToolbar(scene, undefined, appStore);
      const pointsGroup = TOOL_GROUPS.find((g) => g.id === 'points')!;
      findButtonByLabel(root, pointsGroup.label)!.click();

      // Filtered view: no more group buttons, but a tool from this group is present.
      expect(root.querySelectorAll('.tool-group-btn').length).toBe(0);
      const firstTool = CONSTRUCTION_CATALOG[pointsGroup.tools[0]];
      expect(findButtonByLabel(root, firstTool.label)).toBeTruthy();
    });

    // navigating into a group should also persist it on appStore
    it('clicking a tool-group-btn calls appStore.setLastToolGroup and setActiveToolGroup', () => {
      const setLastSpy = vi.spyOn(appStore, 'setLastToolGroup');
      const setActiveSpy = vi.spyOn(appStore, 'setActiveToolGroup');
      const { root } = createToolbar(scene, undefined, appStore);
      const linesGroup = TOOL_GROUPS.find((g) => g.id === 'lines')!;
      findButtonByLabel(root, linesGroup.label)!.click();

      expect(setLastSpy).toHaveBeenCalledWith('lines');
      expect(setActiveSpy).toHaveBeenCalledWith('lines');
    });

    // filtered view should show exactly the back button plus that group's tools, nothing extra
    it('filtered view renders a back button plus one button per tool in that group', () => {
      const { root } = createToolbar(scene, undefined, appStore);
      const circlesGroup = TOOL_GROUPS.find((g) => g.id === 'circles')!;
      findButtonByLabel(root, circlesGroup.label)!.click();

      expect(findButtonByLabel(root, '← All tools')).toBeTruthy();
      for (const toolName of circlesGroup.tools) {
        const entry = CONSTRUCTION_CATALOG[toolName];
        if (entry) expect(findButtonByLabel(root, entry.label)).toBeTruthy();
      }
    });

    // backing out of a group should undo everything entering it did
    it("clicking the back button returns to grouped view, resets scene.tool to 'select', and resets the active group", () => {
      const setLastSpy = vi.spyOn(appStore, 'setLastToolGroup');
      const setActiveSpy = vi.spyOn(appStore, 'setActiveToolGroup');
      const { root } = createToolbar(scene, undefined, appStore);
      scene.setTool('midpoint');
      const triangleGroup = TOOL_GROUPS.find((g) => g.id === 'triangles')!;
      findButtonByLabel(root, triangleGroup.label)!.click();

      findButtonByLabel(root, '← All tools')!.click();

      expect(root.querySelectorAll('.tool-group-btn').length).toBe(TOOL_GROUPS.length);
      expect(scene.tool).toBe('select');
      expect(setLastSpy).toHaveBeenCalledWith(null);
      expect(setActiveSpy).toHaveBeenCalledWith(null);
    });

    // picking a tool from the filtered list is what actually drives the scene
    it("clicking a tool button in the filtered view calls scene.setTool with that tool's name", () => {
      const { root } = createToolbar(scene, undefined, appStore);
      const quadsGroup = TOOL_GROUPS.find((g) => g.id === 'quads')!;
      findButtonByLabel(root, quadsGroup.label)!.click();

      const entry = CONSTRUCTION_CATALOG[quadsGroup.tools[0]];
      findButtonByLabel(root, entry.label)!.click();

      expect(scene.tool).toBe(entry.name);
    });
  });
});
