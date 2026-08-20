/* ═══════════════════════════════════════════════════════
 * TerminalX — Earnings Calendar Mini (Bottom Panel)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useState } from 'react';

interface EarningsEntry {
  ticker: string;
  name: string;
  date: string;
  result: 'beat' | 'meet' | 'miss' | 'upcoming';
}

const MOCK_EARNINGS: EarningsEntry[] = [
  { ticker: 'TCS', name: 'Tata Consultancy Services', date: '12 Jun', result: 'beat' },
  { ticker: 'INFY', name: 'Infosys Ltd', date: '14 Jun', result: 'meet' },
  { ticker: 'RELIANCE', name: 'Reliance Industries', date: '18 Jun', result: 'upcoming' },
  { ticker: 'HDFC', name: 'HDFC Bank Ltd', date: '20 Jun', result: 'upcoming' },
  { ticker: 'WIPRO', name: 'Wipro Ltd', date: '22 Jun', result: 'miss' },
];

const RESULT_DOTS: Record<string, { colors: string[]; label: string }> = {
  beat:     { colors: ['var(--accent-green)', 'var(--accent-green)', 'var(--accent-green)'], label: 'Beat' },
  meet:     { colors: ['var(--accent-yellow)', 'var(--accent-yellow)', 'var(--text-muted)'], label: 'Meet' },
  miss:     { colors: ['var(--accent-red)', 'var(--accent-red)', 'var(--text-muted)'], label: 'Miss' },
  upcoming: { colors: ['var(--text-muted)', 'var(--text-muted)', 'var(--text-muted)'], label: 'Upcoming' },
};

export function EarningsCalendarMini() {
  const [hoveredRow, setHoveredRow] = useState<number | null>(null);

  return (
    <div className="earnings-cal">
      <div className="earnings-cal-header">
        <span className="earnings-cal-title">EARNINGS CALENDAR</span>
        <span className="earnings-cal-badge">
          {MOCK_EARNINGS.filter((e) => e.result === 'upcoming').length} upcoming
        </span>
      </div>

      <div className="earnings-cal-list">
        {MOCK_EARNINGS.map((entry, i) => {
          const dotInfo = RESULT_DOTS[entry.result];
          return (
            <div
              key={entry.ticker}
              className={`earnings-cal-row ${hoveredRow === i ? 'hovered' : ''}`}
              onMouseEnter={() => setHoveredRow(i)}
              onMouseLeave={() => setHoveredRow(null)}
            >
              <div className="earnings-cal-ticker-area">
                <span className="earnings-cal-ticker">{entry.ticker}</span>
                <span className="earnings-cal-name">{entry.name}</span>
              </div>
              <div className="earnings-cal-date">{entry.date}</div>
              <div className="earnings-cal-dots" title={dotInfo.label}>
                {dotInfo.colors.map((color, ci) => (
                  <span
                    key={ci}
                    className="earnings-cal-dot"
                    style={{ background: color }}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="earnings-cal-footer">
        <span className="earnings-cal-link">View all earnings →</span>
      </div>
    </div>
  );
}
