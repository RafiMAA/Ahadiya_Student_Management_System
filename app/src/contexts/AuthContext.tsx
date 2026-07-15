import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { setAccessToken } from '@/lib/apiClient';

interface AuthUser {
  id: string;
  full_name: string;
  username: string;
  role: 'Principal' | 'Admin' | 'Teacher' | 'Super Admin';
}

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // On mount, instantly hydrate from localStorage (no network call needed)
  // then verify token validity in the background
  useEffect(() => {
    const token = localStorage.getItem('ahadiya_token');
    const storedUser = localStorage.getItem('ahadiya_user');

    if (token && storedUser) {
      // Instant hydration — no waiting for /auth/me
      setAccessToken(token);
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        // Corrupted data — clear and start fresh
        localStorage.removeItem('ahadiya_user');
      }
      setIsLoading(false);

      // Background validation — if token expired, will auto-redirect via apiClient 401 handler
      api.get<AuthUser>('/auth/me')
        .then((freshUser) => {
          setUser(freshUser);
          localStorage.setItem('ahadiya_user', JSON.stringify(freshUser));
        })
        .catch(() => {
          // Token invalid — clear everything
          localStorage.removeItem('ahadiya_token');
          localStorage.removeItem('ahadiya_user');
          setAccessToken(null);
          setUser(null);
        });
    } else if (token) {
      // Token exists but no stored user — must call /auth/me
      setAccessToken(token);
      api.get<AuthUser>('/auth/me')
        .then((u) => {
          setUser(u);
          localStorage.setItem('ahadiya_user', JSON.stringify(u));
        })
        .catch(() => {
          localStorage.removeItem('ahadiya_token');
          setAccessToken(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (username: string, password: string) => {
    const res = await api.post<{
      access_token: string;
      role: string;
      teacher_id: string;
      full_name: string;
    }>('/auth/login', { username, password });

    setAccessToken(res.access_token);
    localStorage.setItem('ahadiya_token', res.access_token);

    const userData: AuthUser = {
      id: res.teacher_id,
      full_name: res.full_name,
      username,
      role: res.role as AuthUser['role'],
    };
    setUser(userData);
    // Store user data so next page load is instant (no /auth/me round trip)
    localStorage.setItem('ahadiya_user', JSON.stringify(userData));
  };

  const logout = () => {
    setAccessToken(null);
    localStorage.removeItem('ahadiya_token');
    localStorage.removeItem('ahadiya_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);

/** Wrapper component that redirects unauthenticated users to /login */
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login', { replace: true });
    }
  }, [isLoading, isAuthenticated, navigate]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" />
      </div>
    );
  }

  return isAuthenticated ? <>{children}</> : null;
}
