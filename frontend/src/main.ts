import { Viewport } from './geometry/viewport';
import { Renderer } from './render/renderer';
import { Scene } from './scene/scene';
import { attachPanZoom } from './input/panZoom';
import { attachClickToAddPoint } from './input/clickToAddPoint';
import './style.css';

const container = document.getElementById('app');
if (!container) {
  throw new Error('No #app element found in HTML');
}

const viewport = new Viewport();
viewport.width = window.innerWidth;
viewport.height = window.innerHeight;

const scene = new Scene();
const renderer = new Renderer(container, viewport, scene);
const redraw = () => renderer.draw();
redraw();

attachPanZoom(renderer.svg, viewport, redraw);
attachClickToAddPoint(renderer.svg, viewport, scene, redraw);

window.addEventListener('resize', () => {
  viewport.width = window.innerWidth;
  viewport.height = window.innerHeight;
  renderer.resize();
  redraw();
});
