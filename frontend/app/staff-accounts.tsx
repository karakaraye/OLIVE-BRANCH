"use client";

import { type FormEvent, useEffect, useState } from "react";
import { staffApi } from "./staff-api";

type Account = { id: number; name: string; username: string; roles: string[]; active: boolean; outlet: number | null };
type Directory = { accounts: Account[]; roles: string[]; outlets: { id: number; name: string }[] };

function RoleFields({ directory, account }: { directory: Directory; account?: Account }) {
  const [role, setRole] = useState(account?.roles[0] ?? directory.roles[0]);
  return (
    <>
      <label>Role
        <select name="role" value={role} onChange={(event) => setRole(event.target.value)}>
          {directory.roles.map((name) => <option key={name}>{name}</option>)}
        </select>
      </label>
      {role === "cashier" && (
        <label>Outlet
          <select name="outlet" required defaultValue={account?.outlet ?? ""}>
            <option value="">Select outlet</option>
            {directory.outlets.map((outlet) => <option key={outlet.id} value={outlet.id}>{outlet.name}</option>)}
          </select>
        </label>
      )}
    </>
  );
}

export default function AccountPanel({ csrfToken, signedInUser }: {
  csrfToken: string;
  signedInUser: string;
}) {
  const [directory, setDirectory] = useState<Directory>();
  const [selected, setSelected] = useState<number>();
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<{ text: string; error?: boolean }>();

  useEffect(() => {
    let active = true;
    void staffApi<Directory>("accounts/").then((result) => {
      if (active) setDirectory(result);
    }).catch((error: Error) => {
      if (active) setFeedback({ text: error.message, error: true });
    });
    return () => { active = false; };
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>, path: string, reset = false) {
    event.preventDefault();
    const form = event.currentTarget;
    setFeedback(undefined);
    setBusy(true);
    try {
      await staffApi(path, { csrfToken, form: new FormData(form) });
      setDirectory(await staffApi<Directory>("accounts/"));
      if (reset) form.reset();
      setFeedback({ text: "Account saved." });
    } catch (error) {
      setFeedback({ text: (error as Error).message, error: true });
    } finally {
      setBusy(false);
    }
  }

  const account = directory?.accounts.find((account) => account.id === selected);
  return (
    <section aria-label="Named staff accounts">
      {directory && (
        <>
          <details>
            <summary>Create a named account</summary>
            <form onSubmit={(event) => void submit(event, "accounts/", true)}>
              <label>Username <input name="username" autoComplete="off" required /></label>
              <label>First name <input name="first_name" required /></label>
              <label>Last name <input name="last_name" required /></label>
              <label>Initial password <input name="password" type="password" autoComplete="new-password" required /></label>
              <RoleFields directory={directory} />
              <label>Reason <input name="reason" maxLength={255} required /></label>
              <button disabled={busy}>Create account</button>
            </form>
          </details>
          <label>Staff account
            <select value={selected ?? ""} onChange={(event) => setSelected(Number(event.target.value) || undefined)}>
              <option value="">Choose an account</option>
              {directory.accounts.filter((entry) => entry.username !== signedInUser).map((entry) => (
                <option key={entry.id} value={entry.id}>
                  {entry.name || entry.username} ({entry.roles.join(", ")}){entry.active ? "" : " — disabled"}
                </option>
              ))}
            </select>
          </label>
          {account && (
            <>
              <form key={`role-${account.id}-${account.roles.join(",")}-${account.outlet}`}
                onSubmit={(event) => void submit(event, `accounts/${account.id}/role/`, true)}>
                <RoleFields directory={directory} account={account} />
                <label>Reason for permission change <input name="reason" maxLength={255} required /></label>
                <button disabled={busy}>Change role</button>
              </form>
              <form key={`state-${account.id}-${account.active}`}
                onSubmit={(event) => void submit(event, `accounts/${account.id}/${account.active ? "disable" : "enable"}/`)}>
                <label>Reason for account status change <input name="reason" maxLength={255} required /></label>
                <button disabled={busy}>{account.active ? "Disable account" : "Enable account"}</button>
              </form>
            </>
          )}
        </>
      )}
      {feedback && <p role={feedback.error ? "alert" : "status"}>{feedback.text}</p>}
    </section>
  );
}
