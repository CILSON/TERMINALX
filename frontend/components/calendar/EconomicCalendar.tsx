/* ═══════════════════════════════════════════════════════
 * TerminalX — Economic Calendar
 * ═══════════════════════════════════════════════════════ */
'use client';

import React, { useEffect, useState, Fragment } from 'react';
import { fetchCalendar } from '@/lib/api';
import { LoadingPulse } from '@/components/common/LoadingPulse';
import { useCommandStore } from '@/stores/commandStore';
import type { EconomicEvent } from '@/types';

const COUNTRY_FLAGS: Record<string, string> = {
  IN: '🇮🇳',
  US: '🇺🇸',
  EU: '🇪🇺',
  GB: '🇬🇧',
  JP: '🇯🇵',
  CN: '🇨🇳',
};

export function EconomicCalendar() {
  const [events, setEvents] = useState<EconomicEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const setActiveView = useCommandStore((s) => s.setActiveView);

  useEffect(() => {
    fetchCalendar()
      .then((data) => setEvents(data))
      .catch(() => setEvents([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="calendar">
        <div className="section-header">Economic Calendar</div>
        <LoadingPulse count={6} />
      </div>
    );
  }

  // Group events by date
  const grouped = events.reduce<Record<string, EconomicEvent[]>>((acc, event) => {
    const date = event.event_date?.split('T')[0] || 'Unknown';
    if (!acc[date]) acc[date] = [];
    acc[date].push(event);
    return acc;
  }, {});

  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="calendar">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
        <button className="article-reader-back" onClick={() => setActiveView('market')}>
          ← Back to Market
        </button>
      </div>
      <div className="section-header">Economic Calendar</div>

      <table className="calendar-table">
        <thead>
          <tr>
            <th style={{ width: '30px' }}></th>
            <th>Event</th>
            <th>Country</th>
            <th>Impact</th>
            <th>Forecast</th>
            <th>Actual</th>
            <th>Previous</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(grouped).map(([date, dateEvents]) => (
            <Fragment key={date}>
              <tr key={`date-${date}`}>
                <td
                  colSpan={7}
                  className={`calendar-date-group ${date === today ? 'calendar-today' : ''}`}
                >
                  {date === today ? '📅 TODAY — ' : ''}{formatDate(date)}
                </td>
              </tr>
              {dateEvents.map((event, i) => (
                <tr key={`${date}-${i}`} className={date === today ? 'calendar-today' : ''}>
                  <td>
                    <span className={`calendar-impact ${event.impact}`} />
                  </td>
                  <td className="calendar-event-name">{event.event_name}</td>
                  <td>
                    <span className="calendar-country">
                      {COUNTRY_FLAGS[event.country] || '🌍'} {event.country}
                    </span>
                  </td>
                  <td>
                    <span className={`badge badge-${event.impact}`}>
                      {event.impact?.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>{event.forecast || '—'}</td>
                  <td style={{ color: event.actual ? 'var(--text-primary)' : 'var(--text-muted)', fontWeight: event.actual ? 600 : 400 }}>
                    {event.actual || '—'}
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>{event.previous || '—'}</td>
                </tr>
              ))}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-IN', {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
}
