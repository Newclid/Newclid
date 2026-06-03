import type { CatalogEntry } from "./catalog-types";
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

export const CONSTRUCTION_CATALOG: Record<string, CatalogEntry> = {
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
};