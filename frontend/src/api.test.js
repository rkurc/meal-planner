import { describe, it, afterEach } from "node:test";
import assert from "node:assert/strict";
import { api, ApiError } from "./api.js";

describe("api", () => {
  const originalFetch = globalThis.fetch;
  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it("returns parsed JSON on 200", async () => {
    globalThis.fetch = async () =>
      new Response(JSON.stringify({ id: "1" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    const data = await api.get("/api/recipes/1");
    assert.equal(data.id, "1");
  });

  it("returns undefined on 204", async () => {
    globalThis.fetch = async () => new Response(null, { status: 204 });
    const data = await api.del("/api/recipes/1");
    assert.equal(data, undefined);
  });

  it("throws ApiError with status and body.error on 409", async () => {
    globalThis.fetch = async () =>
      new Response(JSON.stringify({ error: "dup" }), {
        status: 409,
        headers: { "Content-Type": "application/json" },
      });
    await assert.rejects(
      () => api.post("/api/ingredients", { name: "Flour" }),
      (err) =>
        err instanceof ApiError && err.status === 409 && err.message === "dup",
    );
  });
});
