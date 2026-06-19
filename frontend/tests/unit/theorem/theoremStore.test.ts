import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TheoremStore } from '../../../src/store/theoremStore';
import type { CustomTheorem } from '../../../src/types/theorem';

const STORAGE_KEY = 'newclid_custom_theorems_v1';

function makeTheorem(overrides?: Partial<Omit<CustomTheorem, 'createdAt'>>): Omit<CustomTheorem, 'createdAt'> {
  return {
    id: 'test_theorem',
    name: 'test_theorem',
    description: '',
    premises: [{ predicateId: 'cong', args: ['A', 'B', 'C', 'D'] }],
    conclusions: [{ predicateId: 'para', args: ['A', 'B', 'C', 'D'] }],
    ...overrides,
  };
}

beforeEach(() => {
  localStorage.clear();
});

describe('TheoremStore — initial state', () => {
  it('getAll returns empty array when localStorage is empty', () => {
    const store = new TheoremStore();
    expect(store.getAll()).toEqual([]);
  });

  it('has returns false for any id when empty', () => {
    const store = new TheoremStore();
    expect(store.has('anything')).toBe(false);
  });

  it('getById returns undefined when empty', () => {
    const store = new TheoremStore();
    expect(store.getById('x')).toBeUndefined();
  });

  it('loads existing theorems from localStorage on construction', () => {
    const existing: CustomTheorem = {
      id: 'abc',
      name: 'abc',
      description: '',
      premises: [],
      conclusions: [],
      createdAt: 1000,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify([existing]));
    const store = new TheoremStore();
    expect(store.getAll().length).toBe(1);
    expect(store.getById('abc')?.name).toBe('abc');
  });

  it('returns empty array and does not throw when localStorage contains invalid JSON', () => {
    localStorage.setItem(STORAGE_KEY, 'not valid json {{');
    const store = new TheoremStore();
    expect(store.getAll()).toEqual([]);
  });
});

describe('TheoremStore — save', () => {
  it('adds a new theorem', () => {
    const store = new TheoremStore();
    store.save(makeTheorem());
    expect(store.getAll().length).toBe(1);
  });

  it('saved theorem is retrievable by id', () => {
    const store = new TheoremStore();
    store.save(makeTheorem({ id: 'th1', name: 'th1' }));
    expect(store.getById('th1')).toMatchObject({ name: 'th1' });
  });

  it('has returns true after save', () => {
    const store = new TheoremStore();
    store.save(makeTheorem());
    expect(store.has('test_theorem')).toBe(true);
  });

  it('appends a second theorem preserving both', () => {
    const store = new TheoremStore();
    store.save(makeTheorem({ id: 'first', name: 'first' }));
    store.save(makeTheorem({ id: 'second', name: 'second' }));
    expect(store.getAll().length).toBe(2);
    expect(store.has('first')).toBe(true);
    expect(store.has('second')).toBe(true);
  });

  it('second theorem is appended after the first', () => {
    const store = new TheoremStore();
    store.save(makeTheorem({ id: 'first' }));
    store.save(makeTheorem({ id: 'second' }));
    const all = store.getAll();
    expect(all[0].id).toBe('first');
    expect(all[1].id).toBe('second');
  });

  it('upserts an existing theorem by id', () => {
    const store = new TheoremStore();
    store.save(makeTheorem({ id: 'x', name: 'original' }));
    store.save(makeTheorem({ id: 'x', name: 'updated' }));
    expect(store.getAll().length).toBe(1);
    expect(store.getById('x')?.name).toBe('updated');
  });

  it('upsert preserves the original createdAt', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2024-01-01'));
    const store = new TheoremStore();
    store.save(makeTheorem({ id: 'x' }));
    const originalCreatedAt = store.getById('x')!.createdAt;

    vi.setSystemTime(new Date('2025-06-01'));
    store.save(makeTheorem({ id: 'x', name: 'updated' }));
    expect(store.getById('x')?.createdAt).toBe(originalCreatedAt);
    vi.useRealTimers();
  });

  it('first save sets createdAt to Date.now()', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2024-01-01'));
    const store = new TheoremStore();
    store.save(makeTheorem({ id: 'x' }));
    expect(store.getById('x')?.createdAt).toBe(new Date('2024-01-01').getTime());
    vi.useRealTimers();
  });

  it('persists to localStorage after save', () => {
    const store = new TheoremStore();
    store.save(makeTheorem({ id: 'th1', name: 'th1' }));
    const raw = localStorage.getItem(STORAGE_KEY);
    expect(raw).not.toBeNull();
    const parsed = JSON.parse(raw!) as CustomTheorem[];
    expect(parsed.length).toBe(1);
    expect(parsed[0].id).toBe('th1');
  });

  it('a new TheoremStore instance reads data persisted by a previous instance', () => {
    const storeA = new TheoremStore();
    storeA.save(makeTheorem({ id: 'shared', name: 'shared' }));
    const storeB = new TheoremStore();
    expect(storeB.getAll().length).toBe(1);
    expect(storeB.getById('shared')?.name).toBe('shared');
  });
});

describe('TheoremStore — remove', () => {
  it('removes a theorem by id', () => {
    const store = new TheoremStore();
    store.save(makeTheorem());
    store.remove('test_theorem');
    expect(store.getAll().length).toBe(0);
    expect(store.has('test_theorem')).toBe(false);
  });

  it('does not throw when removing a non-existent id', () => {
    const store = new TheoremStore();
    expect(() => store.remove('nonexistent')).not.toThrow();
    expect(store.getAll()).toEqual([]);
  });

  it('removes only the targeted theorem', () => {
    const store = new TheoremStore();
    store.save(makeTheorem({ id: 'keep', name: 'keep' }));
    store.save(makeTheorem({ id: 'delete', name: 'delete' }));
    store.remove('delete');
    expect(store.getAll().length).toBe(1);
    expect(store.has('keep')).toBe(true);
    expect(store.has('delete')).toBe(false);
  });

  it('persists removal to localStorage', () => {
    const store = new TheoremStore();
    store.save(makeTheorem());
    store.remove('test_theorem');
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY)!) as CustomTheorem[];
    expect(parsed).toEqual([]);
  });
});

describe('TheoremStore — subscribe / unsubscribe', () => {
  it('subscriber is called when save is called', () => {
    const store = new TheoremStore();
    const fn = vi.fn();
    store.subscribe(fn);
    store.save(makeTheorem());
    expect(fn).toHaveBeenCalledOnce();
  });

  it('subscriber is called when remove is called', () => {
    const store = new TheoremStore();
    store.save(makeTheorem());
    const fn = vi.fn();
    store.subscribe(fn);
    store.remove('test_theorem');
    expect(fn).toHaveBeenCalledOnce();
  });

  it('subscriber is not called by read-only methods', () => {
    const store = new TheoremStore();
    const fn = vi.fn();
    store.subscribe(fn);
    store.getAll();
    store.getById('x');
    store.has('x');
    expect(fn).not.toHaveBeenCalled();
  });

  it('multiple subscribers are all notified on save', () => {
    const store = new TheoremStore();
    const a = vi.fn();
    const b = vi.fn();
    store.subscribe(a);
    store.subscribe(b);
    store.save(makeTheorem());
    expect(a).toHaveBeenCalledOnce();
    expect(b).toHaveBeenCalledOnce();
  });

  it('unsubscribed listener is not called after unsubscribe', () => {
    const store = new TheoremStore();
    const fn = vi.fn();
    const unsub = store.subscribe(fn);
    unsub();
    store.save(makeTheorem());
    expect(fn).not.toHaveBeenCalled();
  });

  it('calling unsubscribe twice does not throw', () => {
    const store = new TheoremStore();
    const unsub = store.subscribe(vi.fn());
    expect(() => { unsub(); unsub(); }).not.toThrow();
  });

  it('subscriber is called once per save across multiple saves', () => {
    const store = new TheoremStore();
    const fn = vi.fn();
    store.subscribe(fn);
    store.save(makeTheorem({ id: 'a' }));
    store.save(makeTheorem({ id: 'b' }));
    expect(fn).toHaveBeenCalledTimes(2);
  });
});

describe('TheoremStore — getAll isolation', () => {
  it('a snapshot captured before save does not reflect the new theorem', () => {
    const store = new TheoremStore();
    store.save(makeTheorem({ id: 'first' }));
    const snapshot = store.getAll();
    store.save(makeTheorem({ id: 'second' }));
    expect(snapshot.length).toBe(1);
    expect(store.getAll().length).toBe(2);
  });

  it('a snapshot captured before remove still holds the removed theorem', () => {
    const store = new TheoremStore();
    store.save(makeTheorem({ id: 'gone' }));
    const snapshot = store.getAll();
    store.remove('gone');
    expect(snapshot.length).toBe(1);
    expect(store.getAll().length).toBe(0);
  });
});
