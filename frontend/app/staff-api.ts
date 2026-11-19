export type Screen = { slug: string; title: string; allowed: boolean };
export type StaffSession = {
  csrfToken: string;
  staff: { username: string; roles: string[] } | null;
  screens?: Screen[];
  canSearchAudit?: boolean;
};

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

function requestId(): string {
  // Staff may use the development demo over LAN HTTP, where randomUUID is unavailable.
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 15) | 64;
  bytes[8] = (bytes[8] & 63) | 128;
  const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
  return [hex.slice(0, 8), hex.slice(8, 12), hex.slice(12, 16), hex.slice(16, 20), hex.slice(20)].join("-");
}

export async function staffApi<T>(
  path: string,
  change?: { csrfToken: string; form?: FormData },
): Promise<T> {
  const options: RequestInit = { cache: "no-store" };
  if (change) {
    options.method = "POST";
    options.headers = {
      "X-CSRFToken": change.csrfToken,
      "Idempotency-Key": requestId(),
    };
    options.body = change.form;
  }
  const send = () => fetch(`/api/staff/${path}`, options);
  // If a write response is lost, retry once with the same request ID.
  const response = await send().catch((error) => {
    if (change) return send();
    throw error;
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const errors = data.errors as Record<string, string[]> | undefined;
    const validation = errors && Object.entries(errors)
      .map(([name, messages]) => `${name === "__all__" ? "" : name + " — "}${messages.join(" ")}`)
      .join(" ");
    throw new ApiError(response.status, data.error || validation || "The request could not be completed.");
  }
  return data as T;
}
