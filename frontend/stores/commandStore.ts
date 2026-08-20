/* ═══════════════════════════════════════════════════════
 * TerminalX — Command Store (Zustand)
 * ═══════════════════════════════════════════════════════ */

import { create } from 'zustand';
import type { ActiveView } from '@/types';
import { ASSET_SYMBOLS, CATEGORY_COMMAND_MAP } from '@/lib/constants';

interface CommandState {
  isOpen: boolean;
  query: string;
  history: string[];
  activeView: ActiveView;
  assetSymbol: string | null;
  searchQuery: string | null;

  setQuery: (q: string) => void;
  executeCommand: (cmd: string) => void;
  setActiveView: (view: ActiveView, symbol?: string) => void;
  toggleOpen: () => void;
  setOpen: (open: boolean) => void;
}

export const useCommandStore = create<CommandState>((set, get) => ({
  isOpen: false,
  query: '',
  history: [],
  activeView: 'asset',
  assetSymbol: 'NIFTY',
  searchQuery: null,

  setQuery: (q: string) => set({ query: q }),

  executeCommand: (cmd: string) => {
    const trimmed = cmd.trim().toUpperCase();
    if (!trimmed) return;

    const state = get();
    const newHistory = [cmd, ...state.history.slice(0, 49)];

    // Check if it's an asset symbol
    if (ASSET_SYMBOLS.has(trimmed)) {
      set({
        history: newHistory,
        query: '',
        isOpen: false,
        activeView: 'asset',
        assetSymbol: trimmed,
      });
      return;
    }

    // Check if it's a category command
    if (trimmed in CATEGORY_COMMAND_MAP || trimmed === 'NEWS' || trimmed === 'TOP') {
      set({
        history: newHistory,
        query: '',
        isOpen: false,
        activeView: 'news',
      });
      return;
    }

    // Market overview
    if (trimmed === 'MKT' || trimmed === 'MARKET') {
      set({
        history: newHistory,
        query: '',
        isOpen: false,
        activeView: 'market',
      });
      return;
    }

    // Calendar
    if (trimmed === 'CAL' || trimmed === 'CALENDAR') {
      set({
        history: newHistory,
        query: '',
        isOpen: false,
        activeView: 'calendar',
      });
      return;
    }

    // Heatmap
    if (trimmed === 'HEAT' || trimmed === 'HEATMAP' || trimmed === 'MAP') {
      set({
        history: newHistory,
        query: '',
        isOpen: false,
        activeView: 'heatmap',
      });
      return;
    }

    // Search
    if (trimmed.startsWith('SEARCH ') || trimmed.startsWith('S ')) {
      const searchTerm = cmd.replace(/^(SEARCH|S)\s+/i, '');
      set({
        history: newHistory,
        query: '',
        isOpen: false,
        activeView: 'search',
        searchQuery: searchTerm,
      });
      return;
    }

    // Default: treat as search
    set({
      history: newHistory,
      query: '',
      isOpen: false,
      activeView: 'search',
      searchQuery: cmd.trim(),
    });
  },

  setActiveView: (view: ActiveView, symbol?: string) =>
    set({
      activeView: view,
      assetSymbol: symbol ?? null,
    }),

  toggleOpen: () =>
    set((state) => ({ isOpen: !state.isOpen })),

  setOpen: (open: boolean) =>
    set({ isOpen: open }),
}));
