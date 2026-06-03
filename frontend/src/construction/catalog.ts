import type { CatalogEntry } from "./catalog-types";
import { midpoint } from "./entries/midpoint";
import { angleBisector } from "./entries/angle_bisector";
import { line } from "./entries/line";
import { segment } from "./entries/segment";
import { circumcircle } from "./entries/circumcircle";
import { parallelogram } from "./entries/parallelogram";
import { equilateralTriangle } from "./entries/equilateral_triangle";

export const CONSTRUCTION_CATALOG: Record<string, CatalogEntry> = {
  [line.name]: line,
  [segment.name]: segment,
  [midpoint.name]: midpoint,
  [angleBisector.name]: angleBisector,
  [circumcircle.name]: circumcircle,
  [parallelogram.name]: parallelogram,
  [equilateralTriangle.name]: equilateralTriangle,
};