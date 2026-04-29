import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { useEffect } from "react";
import { apiScopes } from "./msalConfig";

const DEV_MODE = !import.meta.env.VITE_ENTRA_CLIENT_ID || import.meta.env.VITE_ENTRA_CLIENT_ID === "your-client-id";

// In dev mode, send a fake unsigned JWT that matches what the backend
// accepts when ENTRA_TENANT_ID is empty (see backend/app/auth/entra.py).
// Payload encodes a dev OID — adjust if you want a different identity.
const DEV_TOKEN =
  "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0." +
  // {"oid":"dev-user","sub":"dev-user","name":"Dev User"}
  "eyJvaWQiOiJkZXYtdXNlciIsInN1YiI6ImRldi11c2VyIiwibmFtZSI6IkRldiBVc2VyIn0." +
  "";

export function useAccessToken(): string | null {
  const { instance, accounts } = useMsal();
  const isAuth = useIsAuthenticated();

  useEffect(() => {
    if (DEV_MODE) return;
    if (!isAuth) {
      instance.loginRedirect({ scopes: apiScopes }).catch(() => {});
    }
  }, [isAuth, instance]);

  if (DEV_MODE) return DEV_TOKEN;
  if (!accounts.length) return null;
  return null;
}

export async function acquireToken(): Promise<string | null> {
  if (DEV_MODE) return DEV_TOKEN;
  const inst = (await import("./msalConfig")).msalInstance;
  const account = inst.getAllAccounts()[0];
  if (!account) return null;
  try {
    const r = await inst.acquireTokenSilent({ scopes: apiScopes, account });
    return r.accessToken;
  } catch {
    return null;
  }
}

export function AuthGate({ children }: { children: React.ReactNode }) {
  useAccessToken();
  return <>{children}</>;
}
