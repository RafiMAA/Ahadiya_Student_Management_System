import { createContext, useContext, useState, type ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/apiClient';

interface AppContextType {
  currentAcademicYear: string;
  isSidebarCollapsed: boolean;
  setSidebarCollapsed: (v: boolean) => void;
  isMobileSidebarOpen: boolean;
  setMobileSidebarOpen: (v: boolean) => void;
}

const AppContext = createContext<AppContextType>({
  currentAcademicYear: '',
  isSidebarCollapsed: false,
  setSidebarCollapsed: () => {},
  isMobileSidebarOpen: false,
  setMobileSidebarOpen: () => {},
});

export function AppProvider({ children }: { children: ReactNode }) {
  const [isSidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const { data: currentYear } = useQuery({
    queryKey: ['current-academic-year'],
    queryFn: () => api.get<{ year_label: string }>('/academic-years/current'),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  return (
    <AppContext.Provider value={{
      currentAcademicYear: currentYear?.year_label || '',
      isSidebarCollapsed,
      setSidebarCollapsed,
      isMobileSidebarOpen,
      setMobileSidebarOpen,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export const useApp = () => useContext(AppContext);
