import type { CatalogEntry } from "./catalog-types";
import { select } from "./entries/select";
import { point } from "./entries/point";
import { circle } from "./entries/circle";
import { midpoint } from "./entries/midpoint";
import { angleBisector } from "./entries/angle_bisector";
import { line } from "./entries/line";
import { segment } from "./entries/segment";
import { circumcircle } from "./entries/circumcircle";
import { perpendicular } from "./entries/perpendicular";
import { parallel } from "./entries/parallel";
import { foot } from "./entries/foot";
import { parallelogram } from "./entries/parallelogram";
import { equilateralTriangle } from "./entries/equilateral_triangle";
import { isoscelesTriangle } from "./entries/isosceles_triangle";
import { mirror } from "./entries/mirror";
import { angleMirror } from "./entries/angle_mirror";
import { rectangle } from "./entries/rectangle";
import { tangentLine } from "./entries/tangent_line";
import { intersectionLC } from "./entries/intersection_lc";
import { onCircle } from "./entries/on_circle";
import { onLine } from "./entries/on_line";

export const CONSTRUCTION_CATALOG: Record<string, CatalogEntry> = {
  [select.name]: select,
  [point.name]: point,
  [circle.name]: circle,
  [line.name]: line,
  [segment.name]: segment,
  [midpoint.name]: midpoint,
  [angleBisector.name]: angleBisector,
  [circumcircle.name]: circumcircle,
  [perpendicular.name]: perpendicular,
  [parallel.name]: parallel,
  [foot.name]: foot,
  [parallelogram.name]: parallelogram,
  [equilateralTriangle.name]: equilateralTriangle,
  [isoscelesTriangle.name]: isoscelesTriangle,
  [mirror.name]: mirror,
  [angleMirror.name]: angleMirror,
  [rectangle.name]: rectangle,
  [tangentLine.name]: tangentLine,
  [intersectionLC.name]: intersectionLC,
  [onCircle.name]: onCircle,
  [onLine.name]: onLine,
};