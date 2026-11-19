"use client";

import { type FormEvent, useEffect, useState } from "react";
import AccountPanel from "./staff-accounts";
import AuditPanel from "./staff-audit";
import { ApiError, type Screen, type StaffSession, staffApi } from "./staff-api";

type OpenScreen = { title: string; description: string; outlet?: string };

export default function StaffWorkspace() {
  const [session, setSession] = useState<StaffSession>();
  const [screen, setScreen] = useState<OpenScreen>();
  const [panel, setPanel] = useState<"accounts" | "audit">();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    const current = await staffApi<StaffSession>("session/");
    setSession(current);
    if (!current.staff) {
      setScreen(undefined);
      setPanel(undefined);
    }
  }

  useEffect(() => {
    let active = true;
    function checkSession() {
      void staffApi<StaffSession>("session/").then((current) => {
        if (!active) return;
        setSession(current);
        if (!current.staff) {
          setScreen(undefined);
          setPanel(undefined);
        }
      }).catch(() => {
        if (active) setError("Cannot contact the staff server.");
      });
    }
    checkSession();
    const timer = window.setInterval(checkSession, 30_000);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!session) return;
    setBusy(true);
    setError("");
    try {
      await staffApi("login/", { csrfToken: session.csrfToken, form: new FormData(event.currentTarget) });
      await refresh();
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function handleLogout() {
    if (!session) return;
    setBusy(true);
    setError("");
    try {
      await staffApi("logout/", { csrfToken: session.csrfToken });
      await refresh();
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function open(target: Screen) {
    setScreen(undefined);
    setPanel(undefined);
    setError("");
    try {
      setScreen(await staffApi<OpenScreen>(`screens/${target.slug}/`));
      if (target.slug === "accounts") setPanel("accounts");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) await refresh().catch(() => {});
      setError((error as Error).message);
    }
  }

  return (
    <>
      {error && <p role="alert">{error}</p>}
      {!session && <p role="status">Checking staff session…</p>}
      {session && !session.staff && (
        <form onSubmit={handleLogin}>
          <h2>Staff sign in</h2>
          <label>Username <input name="username" autoComplete="username" required /></label>
          <label>Password <input name="password" type="password" autoComplete="current-password" required /></label>
          <button disabled={busy}>Sign in</button>
        </form>
      )}
      {session?.staff && (
        <>
          <header>
            <p>Signed in as <strong>{session.staff.username}</strong>
              {session.staff.roles.length > 0 && ` (${session.staff.roles.join(", ")})`}
            </p>
            <button type="button" disabled={busy} onClick={handleLogout}>Sign out</button>
          </header>
          <section aria-labelledby="role-demo">
            <h2 id="role-demo">Role access demo</h2>
            <ul className="screen-list">
              {session.screens?.map((option) => (
                <li key={option.slug}>
                  <button type="button" onClick={() => void open(option)}>
                    {option.title} <small>{option.allowed ? "Permitted" : "Denied"}</small>
                  </button>
                </li>
              ))}
            </ul>
            {session.canSearchAudit && (
              <button type="button" onClick={() => {
                setError("");
                setScreen(undefined);
                setPanel("audit");
              }}>Search audit events</button>
            )}
          </section>
          {screen && (
            <section aria-live="polite">
              <h2>{screen.title}</h2>
              <p>{screen.description}</p>
              {screen.outlet && <p>Assigned outlet: {screen.outlet}</p>}
            </section>
          )}
          {panel === "accounts" && <AccountPanel csrfToken={session.csrfToken} signedInUser={session.staff.username} />}
          {panel === "audit" && <AuditPanel />}
        </>
      )}
    </>
  );
}
