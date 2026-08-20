/* ═══════════════════════════════════════════════════════
 * TerminalX — Constants & Command Definitions
 * ═══════════════════════════════════════════════════════ */

import type { NewsCategory } from '@/types';

/* ── News Categories ── */
export const NEWS_CATEGORIES: NewsCategory[] = [
  'TOP',
  'NEWS',
  'INDIA',
  'GLOBAL',
  'MACRO',
  'COMMODITIES',
  'CRYPTO',
];

/* ── Asset Groups ── */
export const ASSET_GROUPS = {
  indices: [
    { symbol: 'NIFTY', name: 'NIFTY 50' },
    { symbol: 'BANKNIFTY', name: 'Bank Nifty' },
    { symbol: 'FINNIFTY', name: 'Fin Nifty' },
    { symbol: 'MIDCAP', name: 'Nifty Midcap' },
    { symbol: 'SENSEX', name: 'BSE Sensex' },
  ],
  commodities: [
    { symbol: 'GOLD', name: 'Gold Spot' },
    { symbol: 'SILVER', name: 'Silver Spot' },
    { symbol: 'BRENT', name: 'Brent Crude' },
    { symbol: 'WTI', name: 'WTI Crude' },
    { symbol: 'NATGAS', name: 'Natural Gas' },
  ],
  forex: [
    { symbol: 'USDINR', name: 'USD/INR' },
    { symbol: 'DXY', name: 'Dollar Index' },
    { symbol: 'EURUSD', name: 'EUR/USD' },
    { symbol: 'GBPUSD', name: 'GBP/USD' },
  ],
  crypto: [
    { symbol: 'BTC', name: 'Bitcoin' },
    { symbol: 'ETH', name: 'Ethereum' },
    { symbol: 'SOL', name: 'Solana' },
    { symbol: 'XRP', name: 'Ripple' },
  ],
} as const;

/* ── Command Shortcuts ── */
export const COMMANDS = [
  'NEWS', 'TOP', 'MKT', 'INDIA', 'GLOBAL', 'FX', 'CMDTY',
  'CRYPTO', 'CAL', 'EARN', 'PORT', 'ALERT', 'SEARCH',
  'NIFTY', 'BANKNIFTY', 'SENSEX', 'GOLD', 'SILVER',
  'BRENT', 'WTI', 'USDINR', 'DXY', 'BTC', 'ETH',
  'SOL', 'MACRO', 'FINNIFTY', 'MIDCAP', 'NATGAS',
] as const;

export const BLOOMBERG_COMMANDS: Record<string, string> = {
  NEWS:      'Show latest market news',
  TOP:       'Top stories by importance',
  MKT:       'Market overview — all asset classes',
  INDIA:     'India market news',
  GLOBAL:    'Global market news',
  FX:        'Forex news & quotes',
  CMDTY:     'Commodities news & quotes',
  CRYPTO:    'Cryptocurrency news & quotes',
  CAL:       'Economic calendar',
  EARN:      'Earnings calendar',
  PORT:      'Portfolio overview',
  ALERT:     'Price alerts',
  SEARCH:    'Search news & assets',
  NIFTY:     'NIFTY 50 intelligence',
  BANKNIFTY: 'Bank Nifty intelligence',
  SENSEX:    'BSE Sensex intelligence',
  GOLD:      'Gold intelligence',
  SILVER:    'Silver intelligence',
  BRENT:     'Brent Crude intelligence',
  WTI:       'WTI Crude intelligence',
  USDINR:    'USD/INR intelligence',
  DXY:       'Dollar Index intelligence',
  BTC:       'Bitcoin intelligence',
  ETH:       'Ethereum intelligence',
  SOL:       'Solana intelligence',
  MACRO:     'Macro economic news',
  FINNIFTY:  'Fin Nifty intelligence',
  MIDCAP:    'Nifty Midcap intelligence',
  NATGAS:    'Natural Gas intelligence',
};

/* ── All tracked symbols (flat list) ── */
export const ALL_SYMBOLS = Object.values(ASSET_GROUPS)
  .flat()
  .map((a) => a.symbol);

/* ── Asset commands (symbols that trigger asset intelligence) ── */
export const ASSET_SYMBOLS: Set<string> = new Set(ALL_SYMBOLS);

/* ── Category commands mapping ── */
export const CATEGORY_COMMAND_MAP: Record<string, string> = {
  NEWS:   'NEWS',
  TOP:    'TOP',
  INDIA:  'INDIA',
  GLOBAL: 'GLOBAL',
  FX:     'COMMODITIES',
  CMDTY:  'COMMODITIES',
  CRYPTO: 'CRYPTO',
  MACRO:  'MACRO',
};

/* ── Country flags for calendar ── */
export const COUNTRY_FLAGS: Record<string, string> = {
  US: '🇺🇸',
  IN: '🇮🇳',
  GB: '🇬🇧',
  EU: '🇪🇺',
  JP: '🇯🇵',
  CN: '🇨🇳',
  DE: '🇩🇪',
  FR: '🇫🇷',
  AU: '🇦🇺',
  CA: '🇨🇦',
  CH: '🇨🇭',
  KR: '🇰🇷',
};
