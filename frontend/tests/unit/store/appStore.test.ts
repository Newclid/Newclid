import { describe, it, expect, beforeEach, vi } from 'vitest';
import { AppStore } from '../../../src/store/appStore';

describe('AppStore', () => {
  let store: AppStore;

  beforeEach(() => {
    store = new AppStore();
  });

  describe('initial state', () => {
    it('has correct defaults', () => {
      const s = new AppStore();
      expect(s.problem).toBeNull();
      expect(s.jobs.size).toBe(0);
      expect(s.activeJobId).toBeNull();
      expect(s.proofMode).toBe(false);
      expect(s.activeProofStepIndex).toBeNull();
      expect(s.activeProofSubStepIndex).toBe(0);
      expect(s.proofByPointsMode).toBe(false);
      expect(s.theoremManagerMode).toBe(false);
      expect(s.panelTab).toBe('toolbar');
      expect(s.lastToolGroup).toBeNull();
      expect(s.activeToolGroup).toBeNull();
      expect(s.goalPickCallback).toBeNull();
    });
  });

  describe('setProblem()', () => {
    it('sets the problem and emits', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.setProblem('jgex string');
      expect(store.problem).toBe('jgex string');
      expect(listener).toHaveBeenCalledTimes(1);
    });
  });

  describe('addJob()', () => {
    it('creates a JobRecord with correct initial fields', () => {
      const before = Date.now();
      store.addJob('j1', 'problem A');
      const record = store.jobs.get('j1')!;
      expect(record.jobId).toBe('j1');
      expect(record.problem).toBe('problem A');
      expect(record.status).toBe('queued');
      expect(record.message).toBeNull();
      expect(record.result).toBeNull();
      expect(record.error).toBeNull();
      expect(record.submittedAt).toBeGreaterThanOrEqual(before);
    });

    it('sets activeJobId, proofMode, resets proofByPointsMode, activeProofStepIndex, activeToolGroup', () => {
      store.activeToolGroup = 'line';
      store.proofByPointsMode = true;
      store.addJob('j1', 'problem');
      expect(store.activeJobId).toBe('j1');
      expect(store.proofMode).toBe(true);
      expect(store.proofByPointsMode).toBe(false);
      expect(store.activeProofStepIndex).toBeNull();
      expect(store.activeToolGroup).toBeNull();
    });

    it('emits', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.addJob('j1', 'problem');
      expect(listener).toHaveBeenCalledTimes(1);
    });
  });

  describe('enterProofMode()', () => {
    it('sets proofMode=true, proofByPointsMode=false, activeToolGroup=null and emits', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.proofByPointsMode = true;
      store.activeToolGroup = 'circle';
      store.enterProofMode();
      expect(store.proofMode).toBe(true);
      expect(store.proofByPointsMode).toBe(false);
      expect(store.activeToolGroup).toBeNull();
      expect(listener).toHaveBeenCalledTimes(1);
    });
  });

  describe('exitProofMode()', () => {
    it('sets proofMode=false, clears step indices, sets panelTab=proofs and emits', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.proofMode = true;
      store.activeProofStepIndex = 3;
      store.activeProofSubStepIndex = 1;
      store.exitProofMode();
      expect(store.proofMode).toBe(false);
      expect(store.activeProofStepIndex).toBeNull();
      expect(store.activeProofSubStepIndex).toBeNull();
      expect(store.panelTab).toBe('proofs');
      expect(listener).toHaveBeenCalledTimes(1);
    });
  });

  describe('setLastToolGroup()', () => {
    it('sets lastToolGroup without emitting', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.setLastToolGroup('angle');
      expect(store.lastToolGroup).toBe('angle');
      expect(listener).not.toHaveBeenCalled();
    });
  });

  describe('setActiveToolGroup()', () => {
    it('sets activeToolGroup without emitting', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.setActiveToolGroup('circle');
      expect(store.activeToolGroup).toBe('circle');
      expect(listener).not.toHaveBeenCalled();
    });
  });

  describe('setActiveProofStep()', () => {
    it('sets activeProofStepIndex, resets activeProofSubStepIndex to 0, and emits', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.activeProofSubStepIndex = 5;
      store.setActiveProofStep(2);
      expect(store.activeProofStepIndex).toBe(2);
      expect(store.activeProofSubStepIndex).toBe(0);
      expect(listener).toHaveBeenCalledTimes(1);
    });
  });

  describe('setActiveProofSubStep()', () => {
    it('sets activeProofSubStepIndex and emits', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.setActiveProofSubStep(3);
      expect(store.activeProofSubStepIndex).toBe(3);
      expect(listener).toHaveBeenCalledTimes(1);
    });
  });

  describe('enterProofByPoints()', () => {
    it('sets proofByPointsMode=true, proofMode=false, activeToolGroup=null and emits', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.proofMode = true;
      store.activeToolGroup = 'line';
      store.enterProofByPoints();
      expect(store.proofByPointsMode).toBe(true);
      expect(store.proofMode).toBe(false);
      expect(store.activeToolGroup).toBeNull();
      expect(listener).toHaveBeenCalledTimes(1);
    });
  });

  describe('exitProofByPoints()', () => {
    it('sets proofByPointsMode=false, clears goalPickCallback and emits', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.proofByPointsMode = true;
      store.goalPickCallback = vi.fn();
      store.exitProofByPoints();
      expect(store.proofByPointsMode).toBe(false);
      expect(store.goalPickCallback).toBeNull();
      expect(listener).toHaveBeenCalledTimes(1);
    });
  });

  describe('enterTheoremManager()', () => {
    it('sets theoremManagerMode=true, clears proofMode/proofByPointsMode/activeToolGroup and emits', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.proofMode = true;
      store.proofByPointsMode = true;
      store.activeToolGroup = 'point';
      store.enterTheoremManager();
      expect(store.theoremManagerMode).toBe(true);
      expect(store.proofMode).toBe(false);
      expect(store.proofByPointsMode).toBe(false);
      expect(store.activeToolGroup).toBeNull();
      expect(listener).toHaveBeenCalledTimes(1);
    });
  });

  describe('exitTheoremManager()', () => {
    it('sets theoremManagerMode=false and emits', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.theoremManagerMode = true;
      store.exitTheoremManager();
      expect(store.theoremManagerMode).toBe(false);
      expect(listener).toHaveBeenCalledTimes(1);
    });
  });

  describe('setGoalPickCallback()', () => {
    it('sets goalPickCallback without emitting', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      const cb = vi.fn();
      store.setGoalPickCallback(cb);
      expect(store.goalPickCallback).toBe(cb);
      expect(listener).not.toHaveBeenCalled();
    });
  });

  describe('setPanelTab()', () => {
    it('changes tab and emits when tab differs', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.setPanelTab('proofs');
      expect(store.panelTab).toBe('proofs');
      expect(listener).toHaveBeenCalledTimes(1);
    });

    it('does not emit when the same tab is set again', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.setPanelTab('toolbar');
      expect(listener).not.toHaveBeenCalled();
    });
  });

  describe('updateJob()', () => {
    it('merges patch onto existing record and emits', () => {
      store.addJob('j1', 'problem');
      const listener = vi.fn();
      store.subscribe(listener);
      store.updateJob('j1', { status: 'running', message: 'Working' });
      const record = store.jobs.get('j1')!;
      expect(record.status).toBe('running');
      expect(record.message).toBe('Working');
      expect(listener).toHaveBeenCalledTimes(1);
    });

    it('is a no-op when jobId does not exist', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.updateJob('unknown', { status: 'running' });
      expect(listener).not.toHaveBeenCalled();
    });
  });

  describe('renameJob()', () => {
    it('sets name when a non-empty string is provided', () => {
      store.addJob('j1', 'problem');
      const listener = vi.fn();
      store.subscribe(listener);
      store.renameJob('j1', 'My proof');
      expect(store.jobs.get('j1')!.name).toBe('My proof');
      expect(listener).toHaveBeenCalledTimes(1);
    });

    it('sets name to undefined when an empty string is provided', () => {
      store.addJob('j1', 'problem');
      store.renameJob('j1', 'Some name');
      store.renameJob('j1', '');
      expect(store.jobs.get('j1')!.name).toBeUndefined();
    });

    it('is a no-op when jobId does not exist', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.renameJob('unknown', 'name');
      expect(listener).not.toHaveBeenCalled();
    });
  });

  describe('removeJob()', () => {
    it('deletes the job and emits', () => {
      store.addJob('j1', 'problem');
      const listener = vi.fn();
      store.subscribe(listener);
      store.removeJob('j1');
      expect(store.jobs.has('j1')).toBe(false);
      expect(listener).toHaveBeenCalledTimes(1);
    });

    it('clears activeJobId and resets proof state when the removed job was active', () => {
      store.addJob('j1', 'problem');
      store.activeProofStepIndex = 2;
      store.activeProofSubStepIndex = 1;
      store.proofMode = true;
      store.removeJob('j1');
      expect(store.activeJobId).toBeNull();
      expect(store.proofMode).toBe(false);
      expect(store.activeProofStepIndex).toBeNull();
      expect(store.activeProofSubStepIndex).toBeNull();
    });

    it('does not clear activeJobId when a different job is removed', () => {
      store.addJob('j1', 'problem 1');
      store.addJob('j2', 'problem 2');
      store.activeJobId = 'j2';
      store.removeJob('j1');
      expect(store.activeJobId).toBe('j2');
    });

    it('is a no-op when jobId does not exist', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.removeJob('unknown');
      expect(listener).not.toHaveBeenCalled();
    });
  });

  describe('setActiveJob()', () => {
    it('sets activeJobId and emits', () => {
      const listener = vi.fn();
      store.subscribe(listener);
      store.setActiveJob('j1');
      expect(store.activeJobId).toBe('j1');
      expect(listener).toHaveBeenCalledTimes(1);
    });
  });

  describe('subscribe()', () => {
    it('returns an unsubscribe function that stops notifications', () => {
      const listener = vi.fn();
      const unsub = store.subscribe(listener);
      store.setProblem('test');
      expect(listener).toHaveBeenCalledTimes(1);
      unsub();
      store.setProblem('test2');
      expect(listener).toHaveBeenCalledTimes(1);
    });
  });
});
