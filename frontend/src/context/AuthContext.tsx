import { createContext, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { clearToken, getToken, setToken as persistToken } from "../api/client";

interface AuthContextValue {
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => Boolean(getToken()));

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuthenticated,
      login: (token: string) => {
        persistToken(token);
        setIsAuthenticated(true);
      },
      logout: () => {
        clearToken();
        setIsAuthenticated(false);
      },
    }),
    [isAuthenticated],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
