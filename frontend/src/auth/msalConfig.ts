import { PublicClientApplication, type Configuration } from "@azure/msal-browser";

const config: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_ENTRA_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_ENTRA_TENANT_ID}`,
    redirectUri: import.meta.env.VITE_ENTRA_REDIRECT_URI,
  },
  cache: { cacheLocation: "sessionStorage" },
};

export const msalInstance = new PublicClientApplication(config);
export const apiScopes = [`api://${import.meta.env.VITE_ENTRA_CLIENT_ID}/access`];
