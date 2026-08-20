/* ═══════════════════════════════════════════════════════
 * TerminalX — API Client
 * ═══════════════════════════════════════════════════════ */

import type { Quote, NewsItem, EconomicEvent, AssetIntelligence, Command, CommandResult } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function apiFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      ...options,
    });
    if (!res.ok) {
      throw new Error(`API Error: ${res.status} ${res.statusText}`);
    }
    return res.json() as Promise<T>;
  } catch (error) {
    console.error(`[TerminalX API] Failed to fetch ${endpoint}:`, error);
    throw error;
  }
}

/* ── Quotes ── */
export async function fetchQuotes(): Promise<Quote[]> {
  const data = await apiFetch<{ quotes: Quote[] }>('/api/quotes');
  return data.quotes;
}

export async function fetchQuote(symbol: string): Promise<Quote> {
  return apiFetch<Quote>(`/api/quotes/${encodeURIComponent(symbol)}`);
}

/* ── Asset Intelligence ── */
export async function fetchAssetIntelligence(symbol: string): Promise<AssetIntelligence> {
  return apiFetch<AssetIntelligence>(`/api/quotes/${encodeURIComponent(symbol)}/intelligence`);
}

/* ── News ── */
export async function fetchNews(params?: {
  category?: string;
  limit?: number;
  offset?: number;
}): Promise<NewsItem[]> {
  const searchParams = new URLSearchParams();
  if (params?.category && params.category !== 'TOP') {
    searchParams.set('category', params.category);
  }
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.offset) searchParams.set('offset', String(params.offset));
  const qs = searchParams.toString();
  const data = await apiFetch<{ articles: NewsItem[] }>(`/api/news${qs ? `?${qs}` : ''}`);
  return data.articles;
}

export async function fetchArticle(id: string): Promise<NewsItem> {
  return apiFetch<NewsItem>(`/api/news/${encodeURIComponent(id)}`);
}

export async function searchNews(query: string): Promise<NewsItem[]> {
  const data = await apiFetch<{ results: NewsItem[] }>(`/api/news/search?q=${encodeURIComponent(query)}`);
  return data.results;
}

/* ── Economic Calendar ── */
export async function fetchCalendar(todayOnly?: boolean): Promise<EconomicEvent[]> {
  const endpoint = todayOnly ? '/api/calendar/today' : '/api/calendar';
  const data = await apiFetch<{ events: EconomicEvent[] }>(endpoint);
  return data.events;
}

/* ── Command Execution ── */
export async function executeCommand(cmd: Command): Promise<CommandResult> {
  return apiFetch<CommandResult>('/api/command', {
    method: 'POST',
    body: JSON.stringify(cmd),
  });
}
