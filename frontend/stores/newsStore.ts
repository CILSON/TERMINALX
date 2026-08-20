/* ═══════════════════════════════════════════════════════
 * TerminalX — News Store (Zustand)
 * ═══════════════════════════════════════════════════════ */

import { create } from 'zustand';
import type { NewsItem } from '@/types';

interface NewsState {
  articles: NewsItem[];
  selectedArticle: NewsItem | null;
  category: string;
  loading: boolean;
  hasMore: boolean;
  offset: number;

  setArticles: (articles: NewsItem[]) => void;
  addArticles: (articles: NewsItem[]) => void;
  selectArticle: (article: NewsItem | null) => void;
  setCategory: (category: string) => void;
  setLoading: (loading: boolean) => void;
  setHasMore: (hasMore: boolean) => void;
  incrementOffset: (count: number) => void;
  resetOffset: () => void;
}

export const useNewsStore = create<NewsState>((set) => ({
  articles: [],
  selectedArticle: null,
  category: 'TOP',
  loading: false,
  hasMore: true,
  offset: 0,

  setArticles: (articles: NewsItem[]) => {
    const seen = new Set<string>();
    const unique = articles.filter((a) => {
      if (seen.has(a.id)) return false;
      seen.add(a.id);
      return true;
    });
    set({ articles: unique, offset: unique.length });
  },

  addArticles: (articles: NewsItem[]) =>
    set((state) => {
      const existingIds = new Set(state.articles.map((a) => a.id));
      const newUnique = articles.filter((a) => !existingIds.has(a.id));
      return {
        articles: [...state.articles, ...newUnique],
        offset: state.offset + newUnique.length,
        hasMore: articles.length > 0,
      };
    }),

  selectArticle: (article: NewsItem | null) =>
    set({ selectedArticle: article }),

  setCategory: (category: string) =>
    set({ category, articles: [], offset: 0, hasMore: true }),

  setLoading: (loading: boolean) =>
    set({ loading }),

  setHasMore: (hasMore: boolean) =>
    set({ hasMore }),

  incrementOffset: (count: number) =>
    set((state) => ({ offset: state.offset + count })),

  resetOffset: () =>
    set({ offset: 0 }),
}));
