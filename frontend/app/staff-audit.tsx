"use client";

import { type FormEvent, useState } from "react";
import { staffApi } from "./staff-api";

type Event = { id: number; actor: string; actorVerified: boolean; action: string; time: string; reason: string; record: string };
type Results = { events: Event[]; hasMore: boolean };
const eventTime = new Intl.DateTimeFormat("en-NG", {
  timeZone: "Africa/Lagos",
  dateStyle: "medium",
  timeStyle: "medium",
});

export default function AuditPanel() {
  const [results, setResults] = useState<Results>();
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function search(filters: string, nextPage: number) {
    setBusy(true);
    setError("");
    try {
      const params = new URLSearchParams(filters);
      params.set("page", String(nextPage));
      setResults(await staffApi<Results>(`audit/?${params}`));
      setQuery(filters);
      setPage(nextPage);
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setBusy(false);
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const fields = new FormData(event.currentTarget);
    const filters = new URLSearchParams();
    for (const key of ["actor", "record", "date"]) filters.set(key, String(fields.get(key) ?? ""));
    void search(filters.toString(), 1);
  }

  return (
    <section>
      <h2>Audit events</h2>
      <form onSubmit={submit}>
        <label>Actor <input name="actor" /></label>
        <label>Affected record <input name="record" /></label>
        <label>Business date <input name="date" type="date" /></label>
        <button disabled={busy}>Search</button>
      </form>
      {error && <p role="alert">{error}</p>}
      {results && (
        <>
          {results.events.length === 0 && <p>No matching events.</p>}
          <ol>
            {results.events.map((entry) => (
              <li key={entry.id}>
                <strong>{entry.action}</strong> · {entry.actor || "Unknown actor"}
                {!entry.actorVerified && " (unverified)"} · <time dateTime={entry.time}>{eventTime.format(new Date(entry.time))}</time>
                <p>{entry.record} · {entry.reason}</p>
              </li>
            ))}
          </ol>
          <button type="button" disabled={busy || page === 1} onClick={() => void search(query, page - 1)}>Previous</button>
          <button type="button" disabled={busy || !results.hasMore} onClick={() => void search(query, page + 1)}>Next</button>
        </>
      )}
    </section>
  );
}
