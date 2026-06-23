import { describe, it, expect } from 'vitest';
import { el } from '../../../src/ui/dom';

describe('el', () => {
  // Basic element creation with tag name
  it('creates an element with the given tag', () => {
    const node = el('div');
    expect(node.tagName).toBe('DIV');
  });

  // Class attribute sets className property
  it('sets class via node.className when key is "class"', () => {
    const node = el('div', { class: 'my-class' });
    expect(node.className).toBe('my-class');
  });

  // Arbitrary attributes set via setAttribute
  it('sets arbitrary attributes via setAttribute', () => {
    const node = el('button', { type: 'button', 'aria-pressed': 'false' });
    expect(node.getAttribute('type')).toBe('button');
    expect(node.getAttribute('aria-pressed')).toBe('false');
  });

  // Undefined attribute values should be skipped
  it('skips attributes whose value is undefined', () => {
    const node = el('div', { class: undefined as unknown as string, id: 'x' });
    expect(node.className).toBe('');
    expect(node.getAttribute('id')).toBe('x');
  });

  // String children create text nodes
  it('appends string children as text nodes', () => {
    const node = el('span', {}, ['hello']);
    expect(node.textContent).toBe('hello');
  });

  // Element children are appended directly
  it('appends element children', () => {
    const child = document.createElement('span');
    const node = el('div', {}, [child]);
    expect(node.contains(child)).toBe(true);
  });
});
