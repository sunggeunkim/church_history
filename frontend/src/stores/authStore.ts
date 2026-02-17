import { create } from "zustand";
import type { User } from "@/types";
import {
  fetchCurrentUser,
  googleLogin,
  logout as apiLogout,
} from "@/services/api";

type AuthState = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  checkAuth: () => Promise<void>;
  loginWithGoogle: (code: string) => Promise<void>;
  performLogout: () => Promise<void>;
};

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  setUser: (user) => set({ user, isAuthenticated: !!user, isLoading: false }),
  setLoading: (isLoading) => set({ isLoading }),

  checkAuth: async () => {
    try {
      set({ isLoading: true });
      const user = await fetchCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  loginWithGoogle: async (code: string) => {
    try {
      set({ isLoading: true });
      await googleLogin(code);
      const user = await fetchCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ user: null, isAuthenticated: false, isLoading: false });
      throw error;
    }
  },

  performLogout: async () => {
    try {
      await apiLogout();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      set({ user: null, isAuthenticated: false, isLoading: false });
      window.location.href = "/login";
    }
  },
}));
