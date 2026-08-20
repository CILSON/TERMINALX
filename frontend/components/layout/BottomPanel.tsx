/* ═══════════════════════════════════════════════════════
 * TerminalX — Bottom Panel (3-section horizontal layout)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { EconomicCalendarMini } from '@/components/calendar/EconomicCalendarMini';
import { EarningsCalendarMini } from '@/components/calendar/EarningsCalendarMini';
import { FIIDIIFlow } from '@/components/market/FIIDIIFlow';

export function BottomPanel() {
  return (
    <div className="bottom-panel">
      <div className="bottom-panel-section">
        <EconomicCalendarMini />
      </div>
      <div className="bottom-panel-section">
        <EarningsCalendarMini />
      </div>
      <div className="bottom-panel-section">
        <FIIDIIFlow />
      </div>
    </div>
  );
}
