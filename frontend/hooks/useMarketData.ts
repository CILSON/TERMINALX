/* ═══════════════════════════════════════════════════════
 * TerminalX — useMarketData Hook
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useEffect, useCallback } from 'react';
import { useMarketStore } from '@/stores/marketStore';
import { fetchQuotes } from '@/lib/api';

export function useMarketData() {
  const quotes = useMarketStore((s) => s.quotes);
  const previousPrices = useMarketStore((s) => s.previousPrices);
  const setQuotes = useMarketStore((s) => s.setQuotes);
  const selectedSymbol = useMarketStore((s) => s.selectedSymbol);
  const selectSymbol = useMarketStore((s) => s.selectSymbol);
  const lastUpdated = useMarketStore((s) => s.lastUpdated);

  const loadQuotes = useCallback(async () => {
    try {
      const data = await fetchQuotes();
      setQuotes(data);
    } catch (err) {
      console.error('[TerminalX] Failed to fetch quotes:', err);
    }
  }, [setQuotes]);

  useEffect(() => {
    loadQuotes();
    // Refresh every 30 seconds as fallback
    const interval = setInterval(loadQuotes, 30000);
    return () => clearInterval(interval);
  }, [loadQuotes]);

  const quotesArray = Object.values(quotes);

  const getQuote = useCallback(
    (symbol: string) => quotes[symbol] ?? null,
    [quotes]
  );

  const getPreviousPrice = useCallback(
    (symbol: string) => previousPrices[symbol] ?? null,
    [previousPrices]
  );

  const getPriceDirection = useCallback(
    (symbol: string): 'up' | 'down' | 'unchanged' => {
      const prev = previousPrices[symbol];
      const current = quotes[symbol]?.price;
      if (prev == null || current == null || prev === current) return 'unchanged';
      return current > prev ? 'up' : 'down';
    },
    [quotes, previousPrices]
  );

  return {
    quotes: quotesArray,
    quotesMap: quotes,
    selectedSymbol,
    selectSymbol,
    getQuote,
    getPreviousPrice,
    getPriceDirection,
    lastUpdated,
    refresh: loadQuotes,
  };
}
