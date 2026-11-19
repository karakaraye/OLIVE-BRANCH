import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, expect, test, vi } from "vitest";
import Home from "./page";

afterEach(() => vi.unstubAllEnvs());

test("links staff to the local backend by default", () => {
  vi.stubEnv("OLIVE_STAFF_ORIGIN", undefined);
  const html = renderToStaticMarkup(Home());
  expect(html).toContain('href="http://localhost:8000/staff/login/"');
  expect(html).toContain("Staff sign in");
});

test("links staff to the configured LAN backend", () => {
  vi.stubEnv("OLIVE_STAFF_ORIGIN", "http://hotel-server.local:8000");
  expect(renderToStaticMarkup(Home())).toContain(
    'href="http://hotel-server.local:8000/staff/login/"',
  );
});
