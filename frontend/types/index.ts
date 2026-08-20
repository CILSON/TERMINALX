/* ═══════════════════════════════════════════════════════
 * TerminalX — Core Type Definitions
 * ═══════════════════════════════════════════════════════ */

export interface Quote {
  symbol: string;
  name: string;
  asset_class: 'index' | 'commodity' | 'forex' | 'crypto';
  exchange: string;
  price: number;
  change: number;
  change_pct: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  prev_close: number;
  day_high: number;
  day_low: number;
  updated_at: string;
}

export interface NewsItem {
  id: string;
  headline: string;
  summary: string;
  body: string;
  source: string;
  source_url: string;
  publisher: string;
  published_at: string;
  importance: number;
  sentiment: 'bullish' | 'bearish' | 'neutral';
  category: string;
  entities: string[] | string;
  ai_analysis: AIAnalysis | null;
}

export interface AIAnalysis {
  what_happened: string;
  why_it_matters: string;
  affected_assets: string[];
  bullish_for: string[];
  bearish_for: string[];
  confidence: number;
}

export interface EconomicEvent {
  id: string;
  event_name: string;
  country: string;
  event_date: string;
  forecast: string;
  actual: string;
  previous: string;
  impact: 'high' | 'medium' | 'low';
}

export interface AssetIntelligence {
  symbol: string;
  quote: Quote;
  related_news: NewsItem[];
  earnings: Record<string, string>;
  ai_summary: string;
  ai_outlook?: string;
  ai_key_levels?: { support?: number; resistance?: number };
  ai_risk_factors?: string[];
  ai_catalysts?: string[];
  sentiment: string;
  sentiment_breakdown: Record<string, number>;
}

export interface Command {
  command: string;
  target: string;
  params: Record<string, string | number | boolean>;
}

export interface CommandResult {
  type: 'news' | 'quote' | 'calendar' | 'search' | 'asset' | 'error';
  data: Quote[] | NewsItem[] | EconomicEvent[] | AssetIntelligence | string;
  message?: string;
}

export type ActiveView = 'market' | 'news' | 'calendar' | 'asset' | 'search' | 'heatmap';
export type NewsCategory = 'TOP' | 'NEWS' | 'INDIA' | 'GLOBAL' | 'MACRO' | 'COMMODITIES' | 'CRYPTO';
export type Sentiment = 'bullish' | 'bearish' | 'neutral';
export type Impact = 'high' | 'medium' | 'low';
export type BadgeVariant = 'bullish' | 'bearish' | 'neutral' | 'info' | 'warning' | 'orange';
