/* ═══════════════════════════════════════════════════════
 * TerminalX — useWebSocket Hook
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useEffect, useState } from 'react';
import { wsManager } from '@/lib/websocket';
import { useMarketStore } from '@/stores/marketStore';
import { useNewsStore } from '@/stores/newsStore';
import type { Quote, NewsItem } from '@/types';

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const setQuotes = useMarketStore((s) => s.setQuotes);
  const updateQuote = useMarketStore((s) => s.updateQuote);
  const addArticles = useNewsStore((s) => s.addArticles);

  useEffect(() => {
    // Connect
    wsManager.connect();

    // Track connection state
    const unsubConnection = wsManager.onConnectionChange(setIsConnected);

    // Subscribe to quote updates
    // Backend broadcasts EITHER an array of all quotes OR a single quote
    const unsubQuotes = wsManager.subscribe('quotes', (data) => {
      if (Array.isArray(data)) {
        // Bulk update — scheduler sends all quotes as an array
        setQuotes(data as Quote[]);
      } else if (data && typeof data === 'object' && 'symbol' in data) {
        // Single quote update
        updateQuote(data as Quote);
      }
    });

    // Subscribe to news updates
    const unsubNews = wsManager.subscribe('news', (data) => {
      if (Array.isArray(data)) {
        addArticles(data as NewsItem[]);
      } else if (data && typeof data === 'object') {
        addArticles([data as NewsItem]);
      }
    });

    return () => {
      unsubConnection();
      unsubQuotes();
      unsubNews();
      wsManager.disconnect();
    };
  }, [setQuotes, updateQuote, addArticles]);

  return { isConnected };
}
