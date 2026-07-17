import { afterEach, vi } from 'vitest';

function createStorageMock(): Storage {
    const store = new Map<string, string>();

    return {
        get length(): number {
            return store.size;
        },

        clear(): void {
            store.clear();
        },

        getItem(key: string): string | null {
            return store.get(key) ?? null;
        },

        key(index: number): string | null {
            return Array.from(store.keys())[index] ?? null;
        },

        removeItem(key: string): void {
            store.delete(key);
        },

        setItem(key: string, value: string): void {
            store.set(key, value);
        },
    };
}

Object.defineProperty(globalThis, 'localStorage', {
    configurable: true,
    writable: true,
    value: createStorageMock(),
});

Object.defineProperty(globalThis, 'sessionStorage', {
    configurable: true,
    writable: true,
    value: createStorageMock(),
});

afterEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    vi.restoreAllMocks();
});
