import { Viewport } from './geometry/viewport';
import { Renderer } from './render/renderer';
import './style.css';

// Find the div we created in index.html.
const container = document.getElementById('app');
if (!container) {
  throw new Error('No #app element found in HTML');
}

// Set up the viewport and renderer. The plane fills the whole window.
const viewport = new Viewport();
viewport.width = window.innerWidth;
viewport.height = window.innerHeight;

const renderer = new Renderer(container, viewport);
renderer.draw();

window.addEventListener('resize', () => {
  viewport.width = window.innerWidth;
  viewport.height = window.innerHeight;
  renderer.resize();
  renderer.draw();
});