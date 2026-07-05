"use client";

/** Anonymous-first identity (Phase 10). A stable client id lives in
 * localStorage and owns this browser's runs + tier — no password. Managed
 * auth (email magic-link / OAuth) is the documented upgrade path. */

const KEY = "eip_uid";
const EMAIL_KEY = "eip_email";

export function getUserId(): string {
  if (typeof window === "undefined") return "";
  let id = localStorage.getItem(KEY);
  if (!id) {
    const rnd = (typeof crypto !== "undefined" && crypto.randomUUID)
      ? crypto.randomUUID().replace(/-/g, "")
      : Math.random().toString(36).slice(2) + Date.now().toString(36);
    id = "u_" + rnd.slice(0, 20);
    localStorage.setItem(KEY, id);
  }
  return id;
}

export function getEmail(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem(EMAIL_KEY) ?? "";
}

export function setEmail(email: string): void {
  if (typeof window !== "undefined") localStorage.setItem(EMAIL_KEY, email);
}

/** headers to attach to every backend call so runs/history are per-user */
export function userHeaders(): Record<string, string> {
  const id = getUserId();
  const email = getEmail();
  const h: Record<string, string> = {};
  if (id) h["X-EIP-User"] = id;
  if (email) h["X-EIP-Email"] = email;
  return h;
}
