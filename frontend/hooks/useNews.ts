/* ═══════════════════════════════════════════════════════
 * TerminalX — useNews Hook
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useEffect, useCallback } from 'react';
import { useNewsStore } from '@/stores/newsStore';
import { fetchNews, fetchArticle } from '@/lib/api';

const PAGE_SIZE = 20;

export function useNews() {
  const articles = useNewsStore((s) => s.articles);
  const selectedArticle = useNewsStore((s) => s.selectedArticle);
  const category = useNewsStore((s) => s.category);
  const loading = useNewsStore((s) => s.loading);
  const hasMore = useNewsStore((s) => s.hasMore);
  const offset = useNewsStore((s) => s.offset);
  const setArticles = useNewsStore((s) => s.setArticles);
  const addArticles = useNewsStore((s) => s.addArticles);
  const selectArticle = useNewsStore((s) => s.selectArticle);
  const setCategory = useNewsStore((s) => s.setCategory);
  const setLoading = useNewsStore((s) => s.setLoading);

  const loadNews = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchNews({
        category: category === 'TOP' ? undefined : category,
        limit: PAGE_SIZE,
        offset: 0,
      });
      setArticles(data);
    } catch (err) {
      console.error('[TerminalX] Failed to fetch news:', err);
    } finally {
      setLoading(false);
    }
  }, [category, setArticles, setLoading]);

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;
    setLoading(true);
    try {
      const data = await fetchNews({
        category: category === 'TOP' ? undefined : category,
        limit: PAGE_SIZE,
        offset,
      });
      addArticles(data);
    } catch (err) {
      console.error('[TerminalX] Failed to load more news:', err);
    } finally {
      setLoading(false);
    }
  }, [loading, hasMore, category, offset, addArticles, setLoading]);

  const openArticle = useCallback(
    async (articleOrId: string | { id: string }) => {
      const id = typeof articleOrId === 'string' ? articleOrId : articleOrId.id;
      try {
        const article = await fetchArticle(id);
        selectArticle(article);
      } catch {
        // If API fails, try to find in local state
        const local = articles.find((a) => a.id === id);
        if (local) selectArticle(local);
      }
    },
    [articles, selectArticle]
  );

  const closeArticle = useCallback(() => {
    selectArticle(null);
  }, [selectArticle]);

  useEffect(() => {
    loadNews();
  }, [loadNews]);

  return {
    articles,
    selectedArticle,
    category,
    loading,
    hasMore,
    setCategory,
    loadMore,
    openArticle,
    closeArticle,
    selectArticle,
    refresh: loadNews,
  };
}
