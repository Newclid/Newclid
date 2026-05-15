import type { CatalogEntry } from "./catalog-types";
import { midpoint } from "./entries/midpoint";

export const CONSTRUCTION_CATALOG: Record<string, CatalogEntry> = {
  [midpoint.name]: midpoint,
};