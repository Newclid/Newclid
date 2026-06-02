import type { CatalogEntry } from "./catalog-types";
import { midpoint } from "./entries/midpoint";
import { angleBisector } from "./entries/angle_bisector";
import { circumcircle } from "./entries/circumcircle";

export const CONSTRUCTION_CATALOG: Record<string, CatalogEntry> = {
  [midpoint.name]: midpoint,
  [angleBisector.name]: angleBisector,
  [circumcircle.name]: circumcircle,
};