import { afterEach, expect, test, vi } from "vitest";
import { staffApi } from "./staff-api";

afterEach(() => vi.unstubAllGlobals());

test("a lost write response retries with the same UUID and CSRF token", async () => {
  const fetch = vi.fn()
    .mockRejectedValueOnce(new TypeError("connection closed"))
    .mockResolvedValueOnce(Response.json({ signedIn: true }));
  vi.stubGlobal("fetch", fetch);
  const form = new FormData();
  form.set("username", "staff-member");
  await expect(staffApi("login/", { csrfToken: "csrf", form })).resolves.toEqual({ signedIn: true });
  expect(fetch).toHaveBeenCalledTimes(2);
  expect(fetch.mock.calls[0]).toEqual(fetch.mock.calls[1]);
  expect(fetch).toHaveBeenCalledWith("/api/staff/login/", expect.objectContaining({
    method: "POST",
    headers: {
      "X-CSRFToken": "csrf",
      "Idempotency-Key": expect.stringMatching(/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/),
    },
    body: form,
  }));
});

test("a denied screen reports the server response without retrying", async () => {
  const fetch = vi.fn().mockResolvedValue(Response.json({ error: "Permission denied." }, { status: 403 }));
  vi.stubGlobal("fetch", fetch);
  await expect(staffApi("screens/reception/")).rejects.toMatchObject({
    status: 403,
    message: "Permission denied.",
  });
  expect(fetch).toHaveBeenCalledTimes(1);
});
