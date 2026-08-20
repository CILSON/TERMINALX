/* ═══════════════════════════════════════════════════════
 * TerminalX — FII / DII Flow Panel (Bottom Panel)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useState } from 'react';

type FlowTab = 'CASH MARKET' | 'DERIVATIVES';

interface FlowData {
  fii: { net: number; buy: number; sell: number; date: string };
  dii: { net: number; buy: number; sell: number; date: string };
}

const MOCK_FLOW: Record<FlowTab, FlowData> = {
  'CASH MARKET': {
    fii: { net: 2450, buy: 8920, sell: 6470, date: '09 Jun' },
    dii: { net: 1890, buy: 7340, sell: 5450, date: '09 Jun' },
  },
  DERIVATIVES: {
    fii: { net: -3120, buy: 14500, sell: 17620, date: '09 Jun' },
    dii: { net: 980, buy: 5200, sell: 4220, date: '09 Jun' },
  },
};

function formatCrores(val: number): string {
  const sign = val >= 0 ? '+' : '';
  return `${sign}${val.toLocaleString('en-IN')} Cr`;
}

export function FIIDIIFlow() {
  const [activeTab, setActiveTab] = useState<FlowTab>('CASH MARKET');
  const flow = MOCK_FLOW[activeTab];

  return (
    <div className="fii-dii">
      <div className="fii-dii-header">
        <span className="fii-dii-title">FII / DII FLOW</span>
      </div>

      {/* Tabs */}
      <div className="fii-dii-tabs">
        {(['CASH MARKET', 'DERIVATIVES'] as FlowTab[]).map((tab) => (
          <button
            key={tab}
            className={`fii-dii-tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Flow columns */}
      <div className="fii-dii-columns">
        {/* FII */}
        <div className="fii-dii-column">
          <div className="fii-dii-column-label">FII Net</div>
          <div className={`fii-dii-column-value ${flow.fii.net >= 0 ? 'positive' : 'negative'}`}>
            {formatCrores(flow.fii.net)}
          </div>
          <div className="fii-dii-column-breakdown">
            <span className="fii-dii-buy">B: {flow.fii.buy.toLocaleString('en-IN')}</span>
            <span className="fii-dii-sell">S: {flow.fii.sell.toLocaleString('en-IN')}</span>
          </div>
          <div className="fii-dii-column-date">({flow.fii.date})</div>
        </div>

        <div className="fii-dii-divider" />

        {/* DII */}
        <div className="fii-dii-column">
          <div className="fii-dii-column-label">DII Net</div>
          <div className={`fii-dii-column-value ${flow.dii.net >= 0 ? 'positive' : 'negative'}`}>
            {formatCrores(flow.dii.net)}
          </div>
          <div className="fii-dii-column-breakdown">
            <span className="fii-dii-buy">B: {flow.dii.buy.toLocaleString('en-IN')}</span>
            <span className="fii-dii-sell">S: {flow.dii.sell.toLocaleString('en-IN')}</span>
          </div>
          <div className="fii-dii-column-date">({flow.dii.date})</div>
        </div>
      </div>

      {/* Net flow indicator bar */}
      <div className="fii-dii-net-bar">
        <div className="fii-dii-net-bar-label">Combined Net</div>
        <div className="fii-dii-net-bar-track">
          <div
            className={`fii-dii-net-bar-fill ${(flow.fii.net + flow.dii.net) >= 0 ? 'positive' : 'negative'}`}
            style={{
              width: `${Math.min(Math.abs(flow.fii.net + flow.dii.net) / 100, 100)}%`,
            }}
          />
        </div>
        <div className={`fii-dii-net-bar-value ${(flow.fii.net + flow.dii.net) >= 0 ? 'positive' : 'negative'}`}>
          {formatCrores(flow.fii.net + flow.dii.net)}
        </div>
      </div>

      <div className="fii-dii-footer">
        <span className="fii-dii-link">View flow analysis →</span>
      </div>
    </div>
  );
}
