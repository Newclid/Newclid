import { Viewport } from './geometry/viewport';
import { Renderer } from './render/renderer';
import { attachPanZoom } from './input/panZoom';
import './style.css';

const container = document.getElementById('app');
if (!container) {
  throw new Error('No #app element found in HTML');
}

const viewport = new Viewport();
viewport.width = window.innerWidth;
viewport.height = window.innerHeight;

const renderer = new Renderer(container, viewport);
renderer.draw();

attachPanZoom(renderer.svg, viewport, () => renderer.draw());

window.addEventListener('resize', () => {
  viewport.width = window.innerWidth;
  viewport.height = window.innerHeight;
  renderer.resize();
  renderer.draw();
});