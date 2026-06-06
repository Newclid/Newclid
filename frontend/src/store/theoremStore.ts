import type { CustomTheorem } from '../types/theorem';

const STORAGE_KEY = 'newclid_custom_theorems_v1';

function loadFromStorage(): CustomTheorem[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as CustomTheorem[];
  } catch {
    return [];
  }
}

function saveToStorage(theorems: CustomTheorem[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(theorems));
  } catch {
    // ignore quota errors silently
  }
}

export class TheoremStore {
  private theorems: CustomTheorem[] = loadFromStorage();
  private readonly listeners = new Set<() => void>();

  getAll(): readonly CustomTheorem[] {
    return this.theorems;
  }

  getById(id: string): CustomTheorem | undefined {
    return this.theorems.find((t) => t.id === id);
  }

  has(id: string): boolean {
    return this.theorems.some((t) => t.id === id);
  }

  save(theorem: Omit<CustomTheorem, 'createdAt'>): void {
    const existing = this.theorems.find((t) => t.id === theorem.id);
    const record: CustomTheorem = {
      ...theorem,
      createdAt: existing?.createdAt ?? Date.now(),
    };
    this.theorems = [...this.theorems.filter((t) => t.id !== theorem.id), record];
    saveToStorage(this.theorems);
    this.emit();
  }

  remove(id: string): void {
    this.theorems = this.theorems.filter((t) => t.id !== id);
    saveToStorage(this.theorems);
    this.emit();
  }

  subscribe(fn: () => void): () => void {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  private emit(): void {
    for (const fn of this.listeners) fn();
  }
}

export const theoremStore = new TheoremStore();
