import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { useEffect } from "react";
import { apiScopes } from "./msalConfig";

export function useAccessToken(): string | null {
  const { instance, accounts } = useMsal();
  const isAuth = useIsAuthenticated();

  useEffect(() => {
    if (!isAuth) {
      instance.loginRedirect({ scopes: apiScopes }).catch(() => {});
    }
  }, [isAuth, instance]);

  if (!accounts.length) return null;
  // Best-effort cached token; calls use acquireTokenSilent in api/client.
  return null;
}

export async function acquireToken(): Promise<string | null> {
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
