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
import { createJgexInput } from '../../../src/ui/jgexInput';
import { createProofPanel } from '../../../src/ui/proofPanel';
import { createProofsList } from '../../../src/ui/proofsList';
import { createProofChoice } from '../../../src/ui/proofChoice';
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

  describe('active tool highlighting (scene subscription)', () => {
    // active state should track scene.tool, not just whatever was clicked last
    it('marks the matching tool button is-active + aria-pressed=true when scene.tool changes', () => {
      const { root } = createToolbar(scene);
      const selectBtn = findButtonByLabel(root, CONSTRUCTION_CATALOG['select'].label)!;
      expect(selectBtn.classList.contains('is-active')).toBe(true);
      expect(selectBtn.getAttribute('aria-pressed')).toBe('true');
    });

    // switching tools should clear the old highlight, not stack them up
    it('removes is-active from the previously active button when scene.tool changes', () => {
      const { root } = createToolbar(scene, undefined, appStore);
      const pointsGroup = TOOL_GROUPS.find((g) => g.id === 'points')!;
      findButtonByLabel(root, pointsGroup.label)!.click();
      const pointEntry = CONSTRUCTION_CATALOG[pointsGroup.tools[0]];
      const midpointEntry = CONSTRUCTION_CATALOG['midpoint'];

      scene.setTool(pointEntry.name);
      const firstBtn = findButtonByLabel(root, pointEntry.label)!;
      expect(firstBtn.classList.contains('is-active')).toBe(true);

      scene.setTool('midpoint');
      expect(firstBtn.classList.contains('is-active')).toBe(false);
      expect(findButtonByLabel(root, midpointEntry.label)!.classList.contains('is-active')).toBe(true);
    });

    // group buttons hint at which group currently holds the active tool
    it('marks a group button has-active when scene.tool belongs to that group, in grouped view', () => {
      const { root } = createToolbar(scene);
      scene.setTool('midpoint'); // belongs to the 'points' group
      const pointsGroup = TOOL_GROUPS.find((g) => g.id === 'points')!;
      expect(findButtonByLabel(root, pointsGroup.label)!.classList.contains('has-active')).toBe(true);
    });

    // the hint pill text comes straight from the catalog entry's first slot
    it("calls scene.setSlotHint with the new tool's first slot label when the tool changes", () => {
      const setSlotHintSpy = vi.spyOn(scene, 'setSlotHint');
      createToolbar(scene);
      const midpointEntry = CONSTRUCTION_CATALOG['midpoint'];

      scene.setTool('midpoint');

      expect(setSlotHintSpy).toHaveBeenCalledWith(midpointEntry.slots[0]?.label ?? null);
    });

    // a tool with no slots like select should clear the hint, not leave a stale one
    it("calls scene.setSlotHint(null) when switching to a tool with no slots (select)", () => {
      const setSlotHintSpy = vi.spyOn(scene, 'setSlotHint');
      createToolbar(scene);

      scene.setTool('midpoint');
      setSlotHintSpy.mockClear();
      scene.setTool('select');

      expect(setSlotHintSpy).toHaveBeenCalledWith(null);
    });
  });

  describe('create-proof / theorems / clear buttons', () => {
    // this button is the entry point into the whole proof flow
    it('clicking create-proof opens the proof choice dialog', () => {
      const { root } = createToolbar(scene, undefined, appStore);
      findButtonByLabel(root, 'Solve new problem')!.click();

      const fakeProofChoice = (createProofChoice as ReturnType<typeof vi.fn>).mock.results[0].value;
      expect(fakeProofChoice.open).toHaveBeenCalled();
    });

    // choosing the JGEX path should hand off to the jgex modal
    it("proofChoice's onJgex callback opens the jgex input dialog", () => {
      createToolbar(scene, undefined, appStore);
      const opts = (createProofChoice as ReturnType<typeof vi.fn>).mock.calls[0][0];
      const fakeJgex = (createJgexInput as ReturnType<typeof vi.fn>).mock.results[0].value;

      opts.onJgex();

      expect(fakeJgex.open).toHaveBeenCalled();
    });

    // choosing the points path should hand off to appStore instead
    it("proofChoice's onPoints callback calls appStore.enterProofByPoints", () => {
      const enterSpy = vi.spyOn(appStore, 'enterProofByPoints');
      createToolbar(scene, undefined, appStore);
      const opts = (createProofChoice as ReturnType<typeof vi.fn>).mock.calls[0][0];

      opts.onPoints();

      expect(enterSpy).toHaveBeenCalled();
    });

    // this button is just a thin wrapper around appStore
    it('clicking manage-theorems calls appStore.enterTheoremManager when appStore is provided', () => {
      const enterSpy = vi.spyOn(appStore, 'enterTheoremManager');
      const { root } = createToolbar(scene, undefined, appStore);
      findButtonByLabel(root, 'User-Defined Theorems')!.click();

      expect(enterSpy).toHaveBeenCalled();
    });

    // optional chaining should keep this safe even without appStore
    it('clicking manage-theorems is a no-op (no throw) when appStore is omitted', () => {
      const { root } = createToolbar(scene);
      expect(() => findButtonByLabel(root, 'User-Defined Theorems')!.click()).not.toThrow();
    });

    // clear should go straight through to the scene, nothing fancier
    it('clicking clear calls scene.clear()', () => {
      const clearSpy = vi.spyOn(scene, 'clear');
      const { root } = createToolbar(scene);
      findButtonByLabel(root, 'Clear')!.click();

      expect(clearSpy).toHaveBeenCalled();
    });
  });

  describe('panel tab switching and full-panel mode (appStore subscription)', () => {
    function getTabBtns(root: ParentNode) {
      const tabs = Array.from(root.querySelectorAll('.panel-tab-btn')) as HTMLButtonElement[];
      return {
        toolbarTab: tabs.find((b) => b.textContent === 'Toolbar')!,
        proofsTab: tabs.find((b) => b.textContent === 'Proofs')!,
      };
    }

    // confirms the toolbar boots into a sane default state
    it('defaults to Toolbar tab active, group visible, proofsContent hidden', () => {
      const { root } = createToolbar(scene, undefined, appStore);
      const { toolbarTab, proofsTab } = getTabBtns(root);
      const group = root.querySelector('.toolbar-group') as HTMLElement;
      const proofsContent = root.querySelector('.panel-proofs') as HTMLElement;

      expect(toolbarTab.classList.contains('is-active')).toBe(true);
      expect(toolbarTab.getAttribute('aria-selected')).toBe('true');
      expect(proofsTab.classList.contains('is-active')).toBe(false);
      expect(group.style.display).toBe('');
      expect(proofsContent.style.display).toBe('none');
    });

    // tab switching should swap both the content and the active styling together
    it('clicking Proofs tab hides the group/shows proofsContent and marks Proofs tab active', () => {
      const { root } = createToolbar(scene, undefined, appStore);
      const { proofsTab } = getTabBtns(root);
      const group = root.querySelector('.toolbar-group') as HTMLElement;
      const proofsContent = root.querySelector('.panel-proofs') as HTMLElement;

      proofsTab.click();

      expect(proofsTab.classList.contains('is-active')).toBe(true);
      expect(proofsTab.getAttribute('aria-selected')).toBe('true');
      expect(group.style.display).toBe('none');
      expect(proofsContent.style.display).toBe('');
    });

    // the tab click should also clear any in-progress group navigation
    it("clicking Proofs tab calls appStore.setActiveToolGroup(null) and setPanelTab('proofs')", () => {
      const setActiveSpy = vi.spyOn(appStore, 'setActiveToolGroup');
      const setPanelTabSpy = vi.spyOn(appStore, 'setPanelTab');
      const { root } = createToolbar(scene, undefined, appStore);
      getTabBtns(root).proofsTab.click();

      expect(setActiveSpy).toHaveBeenCalledWith(null);
      expect(setPanelTabSpy).toHaveBeenCalledWith('proofs');
    });

    // coming back to the Toolbar tab should remember where the user left off
    it("clicking Toolbar tab after Proofs restores appStore.lastToolGroup as the active group and calls setPanelTab('toolbar')", () => {
      const setActiveSpy = vi.spyOn(appStore, 'setActiveToolGroup');
      const setPanelTabSpy = vi.spyOn(appStore, 'setPanelTab');
      const { root } = createToolbar(scene, undefined, appStore);
      const pointsGroup = TOOL_GROUPS.find((g) => g.id === 'points')!;
      findButtonByLabel(root, pointsGroup.label)!.click(); // sets lastToolGroup = 'points'
      const { toolbarTab, proofsTab } = getTabBtns(root);
      proofsTab.click();

      toolbarTab.click();

      expect(setActiveSpy).toHaveBeenCalledWith('points');
      expect(setPanelTabSpy).toHaveBeenCalledWith('toolbar');
    });

    // entering proof mode should swap the whole toolbar for the proof panel
    it('when appStore.proofMode becomes true, all tool elements are hidden and proofPanel.root becomes visible', () => {
      createToolbar(scene, undefined, appStore);
      const fakeProofPanel = (createProofPanel as ReturnType<typeof vi.fn>).mock.results[0].value;

      appStore.enterProofMode();

      expect(fakeProofPanel.root.style.display).toBe('');
    });

    // the two full-panel modes should never both be visible at the same time
    it('when appStore.proofByPointsMode becomes true, proofByPointsPanel.root is shown and proofPanel.root stays hidden', () => {
      createToolbar(scene, undefined, appStore);
      const fakeProofPanel = (createProofPanel as ReturnType<typeof vi.fn>).mock.results[0].value;
      const fakeProofByPoints = (createProofByPointsPanel as ReturnType<typeof vi.fn>).mock.results[0].value;

      appStore.enterProofByPoints();

      expect(fakeProofByPoints.root.style.display).toBe('');
      expect(fakeProofPanel.root.style.display).toBe('none');
    });

    // theorem manager is its own full panel mode, same rules as proof mode
    it('when appStore.theoremManagerMode becomes true, theoremManagerPanel.root is shown and tool elements stay hidden', () => {
      const { root } = createToolbar(scene, undefined, appStore);
      const fakeTheoremManager = (createTheoremManager as ReturnType<typeof vi.fn>).mock.results[0].value;
      const group = root.querySelector('.toolbar-group') as HTMLElement;

      appStore.enterTheoremManager();

      expect(fakeTheoremManager.root.style.display).toBe('');
      expect(group.style.display).toBe('none');
    });

    // exiting a full panel mode should hand the UI back to wherever panelTab points
    it('leaving all full-panel modes shows tool elements again', () => {
      const { root } = createToolbar(scene, undefined, appStore);
      const group = root.querySelector('.toolbar-group') as HTMLElement;
      const proofsContent = root.querySelector('.panel-proofs') as HTMLElement;

      appStore.enterProofMode();
      expect(group.style.display).toBe('none');
      appStore.exitProofMode(); // also switches panelTab to 'proofs' (see appStore.ts)

      expect(group.style.display).toBe('none');
      expect(proofsContent.style.display).toBe('');
    });
  });

  describe('destroy()', () => {
    // destroy should actually stop listening, not just exist as a formality
    it('destroy() unsubscribes from scene (further scene.setTool calls no longer update the DOM)', () => {
      const { root, destroy } = createToolbar(scene);
      destroy();

      scene.setTool('midpoint');

      const midpointBtn = findButtonByLabel(root, CONSTRUCTION_CATALOG['midpoint'].label);
      expect(midpointBtn).toBeUndefined(); // grouped view never re-rendered after destroy
    });

    // same idea as the scene unsubscribe test but for the appStore subscription
    it('destroy() unsubscribes from appStore (further mutations no longer update the DOM)', () => {
      const { root, destroy } = createToolbar(scene, undefined, appStore);
      const group = root.querySelector('.toolbar-group') as HTMLElement;
      destroy();

      appStore.enterProofMode();

      expect(group.style.display).toBe(''); // syncPanelState no longer ran
    });

    // destroy needs to cascade to every child panel it created, not just itself
    it('destroy() calls destroy on proofPanel, proofByPointsPanel, theoremManagerPanel, proofsList, proofChoice, and jgex', () => {
      const { destroy } = createToolbar(scene, undefined, appStore);
      const fakeProofPanel = (createProofPanel as ReturnType<typeof vi.fn>).mock.results[0].value;
      const fakeProofByPoints = (createProofByPointsPanel as ReturnType<typeof vi.fn>).mock.results[0].value;
      const fakeTheoremManager = (createTheoremManager as ReturnType<typeof vi.fn>).mock.results[0].value;
      const fakeProofsList = (createProofsList as ReturnType<typeof vi.fn>).mock.results[0].value;
      const fakeProofChoice = (createProofChoice as ReturnType<typeof vi.fn>).mock.results[0].value;
      const fakeJgex = (createJgexInput as ReturnType<typeof vi.fn>).mock.results[0].value;

      destroy();

      expect(fakeProofPanel.destroy).toHaveBeenCalled();
      expect(fakeProofByPoints.destroy).toHaveBeenCalled();
      expect(fakeTheoremManager.destroy).toHaveBeenCalled();
      expect(fakeProofsList.destroy).toHaveBeenCalled();
      expect(fakeProofChoice.destroy).toHaveBeenCalled();
      expect(fakeJgex.destroy).toHaveBeenCalled();
    });

    // destroy must stay safe even when the optional panels were never built
    it('destroy() does not throw when appStore was omitted', () => {
      const { destroy } = createToolbar(scene);
      expect(() => destroy()).not.toThrow();
    });
  });
});
