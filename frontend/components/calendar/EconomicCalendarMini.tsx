/* ═══════════════════════════════════════════════════════
 * TerminalX — Economic Calendar Mini (Bottom Panel)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useState, useEffect, useMemo } from 'react';
import { useCommandStore } from '@/stores/commandStore';


interface CalEvent {
  time: string;
  country: string;
  event: string;
  impact: 'High' | 'Medium' | 'Low';
}

const MOCK_EVENTS: CalEvent[] = [
  { time: '09:30', country: 'IN', event: 'RBI Monetary Policy', impact: 'High' },
  { time: '14:00', country: 'US', event: 'FOMC Member Speaks', impact: 'Medium' },
  { time: '16:00', country: 'US', event: 'Existing Home Sales (MoM)', impact: 'Medium' },
  { time: '18:30', country: 'US', event: 'API Crude Oil Stock Change', impact: 'Low' },
  { time: '20:00', country: 'GB', event: 'BoE Interest Rate Decision', impact: 'High' },
];

const TABS = ['TODAY', 'TOMORROW', 'THIS WEEK'] as const;

export function EconomicCalendarMini() {
  const [activeTab, setActiveTab] = useState<string>('TODAY');
  const [events, setEvents] = useState<CalEvent[]>(MOCK_EVENTS);
  const setActiveView = useCommandStore((s) => s.setActiveView);

  const displayedEvents = useMemo(() => {
    if (activeTab === 'TODAY') return events.slice(0, 5);
    if (activeTab === 'TOMORROW') return [...events].reverse().slice(0, 5);
    return [...events, ...events].slice(1, 6);
  }, [activeTab, events]);

  useEffect(() => {
    const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    fetch(`${API}/api/calendar`)
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setEvents(data.slice(0, 5).map((e: Record<string, string>) => ({
            time: new Date(e.event_date).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: false }),
            country: e.country,
            event: e.event_name,
            impact: (e.impact?.charAt(0).toUpperCase() + e.impact?.slice(1) || 'Medium') as CalEvent['impact'],
          })));
        }
      })
      .catch(() => { /* keep mock data */ });
  }, []);

  const impactColor = (impact: string) => {
    if (impact === 'High') return 'var(--accent-red)';
    if (impact === 'Medium') return 'var(--accent-yellow)';
    return 'var(--text-muted)';
  };

  return (
    <>
      <div className="bottom-panel-header">
        <span className="bottom-panel-title">Economic Calendar</span>
        <div className="bottom-panel-tabs">
          {TABS.map((tab) => (
            <button
              key={tab}
              className={`bottom-panel-tab ${activeTab === tab ? 'bottom-panel-tab-active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>
      <div className="bottom-panel-content">
        {displayedEvents.map((ev, i) => (
          <div key={i} className="earnings-cal-row">
            <span className="earnings-cal-ticker" style={{ minWidth: 40 }}>{ev.time}</span>
            <span style={{ fontSize: 11, color: 'var(--text-secondary)', minWidth: 24, fontWeight: 'bold' }}>{ev.country}</span>
            <span className="earnings-cal-name">{ev.event}</span>
            <span style={{ color: impactColor(ev.impact), fontSize: 11, fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
              {ev.impact}
            </span>
          </div>
        ))}
      </div>
      <span 
        className="bottom-panel-link"
        onClick={() => setActiveView('calendar')}
        style={{ cursor: 'pointer' }}
      >
        View full calendar &gt;
      </span>
    </>
  );
}
