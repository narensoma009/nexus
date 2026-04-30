/** Use before `.map` when API may return a non-array (e.g. HTML fallback from wrong base URL). */
export function asArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? value : [];
}
