/* ═══════════════════════════════════════════════════════
 * TerminalX — TopBar (Bloomberg-style header)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useState, useEffect } from 'react';
import { QuoteTicker } from '@/components/market/QuoteTicker';
import { CommandBar } from './CommandBar';

function useClock() {
  const [time, setTime] = useState('');
  const [date, setDate] = useState('');

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      setTime(
        now.toLocaleTimeString('en-IN', {
          timeZone: 'Asia/Kolkata',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false,
        }) + ' IST'
      );
      setDate(
        now.toLocaleDateString('en-IN', {
          timeZone: 'Asia/Kolkata',
          weekday: 'short',
          day: '2-digit',
          month: 'short',
          year: 'numeric',
        })
      );
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, []);

  return { time, date };
}

function useMarketStatus() {
  const [isOpen, setIsOpen] = useState(false);
  useEffect(() => {
    const check = () => {
      const now = new Date();
      const h = now.getHours();
      const m = now.getMinutes();
      const day = now.getDay();
      // Indian market hours: Mon-Fri 9:15 AM to 3:30 PM IST
      const isWeekday = day >= 1 && day <= 5;
      const afterOpen = h > 9 || (h === 9 && m >= 15);
      const beforeClose = h < 15 || (h === 15 && m <= 30);
      setIsOpen(isWeekday && afterOpen && beforeClose);
    };
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, []);
  return isOpen;
}

export function TopBar() {
  const { time, date } = useClock();
  const isMarketOpen = useMarketStatus();

  return (
    <header className="topbar">
      {/* Logo */}
      <div className="topbar-logo">
        <span className="topbar-logo-text">TERMINALX</span>
        <span className="topbar-logo-sub">Intelligence Terminal</span>
      </div>

      {/* Scrolling Ticker */}
      <div className="topbar-ticker">
        <QuoteTicker />
      </div>

      {/* Right: Clock + Market Status */}
      <div className="topbar-right">
        <div>
          <div className="topbar-clock">{time}</div>
          <div className="topbar-clock-date">{date}</div>
        </div>
        <span className={`topbar-market-status ${isMarketOpen ? 'topbar-market-open' : 'topbar-market-closed'}`}>
          ● {isMarketOpen ? 'MARKET OPEN' : 'MARKET CLOSED'}
        </span>
      </div>
    </header>
  );
}
