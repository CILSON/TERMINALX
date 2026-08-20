/* ═══════════════════════════════════════════════════════
 * TerminalX — Market Store (Zustand)
 * ═══════════════════════════════════════════════════════ */

import { create } from 'zustand';
import type { Quote } from '@/types';

interface MarketState {
  quotes: Record<string, Quote>;
  previousPrices: Record<string, number>;
  selectedSymbol: string | null;
  lastUpdated: string | null;

  setQuotes: (quotes: Quote[]) => void;
  updateQuote: (quote: Quote) => void;
  selectSymbol: (symbol: string | null) => void;
}

export const useMarketStore = create<MarketState>((set) => ({
  quotes: {},
  previousPrices: {},
  selectedSymbol: null,
  lastUpdated: null,

  setQuotes: (quotes: Quote[]) =>
    set((state) => {
      const quotesMap: Record<string, Quote> = {};
      const prevPrices: Record<string, number> = { ...state.previousPrices };

      quotes.forEach((q) => {
        // Track previous price for flash animations
        if (state.quotes[q.symbol]) {
          prevPrices[q.symbol] = state.quotes[q.symbol].price;
        }
        quotesMap[q.symbol] = q;
      });

      return {
        quotes: quotesMap,
        previousPrices: prevPrices,
        lastUpdated: new Date().toISOString(),
      };
    }),

  updateQuote: (quote: Quote) =>
    set((state) => ({
      quotes: { ...state.quotes, [quote.symbol]: quote },
      previousPrices: {
        ...state.previousPrices,
        [quote.symbol]: state.quotes[quote.symbol]?.price ?? quote.price,
      },
      lastUpdated: new Date().toISOString(),
    })),

  selectSymbol: (symbol: string | null) =>
    set({ selectedSymbol: symbol }),
}));
