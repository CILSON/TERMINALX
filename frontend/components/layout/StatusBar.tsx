/* ═══════════════════════════════════════════════════════
 * TerminalX — Status Bar
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useMarketStore } from '@/stores/marketStore';

interface StatusBarProps { isConnected: boolean; }

export function StatusBar({ isConnected }: StatusBarProps) {
  const lastUpdated = useMarketStore((s) => s.lastUpdated);
  const time = lastUpdated ? new Date(lastUpdated).toLocaleTimeString('en-IN', { hour12: false, timeZone: 'Asia/Kolkata' }) + ' IST' : '--:--:--';

  return (
    <footer className="status-bar">
      <div className="status-bar-left">
        <span className={`status-dot ${isConnected ? 'status-dot-connected' : 'status-dot-disconnected'}`} />
        <span className="status-label">{isConnected ? 'CONNECTED' : 'DISCONNECTED'}</span>
        <span className="status-divider">|</span>
        <span className="status-label">WS: {isConnected ? '1' : '0'}</span>
        <span className="status-divider">|</span>
        <span className="status-label">LAST UPDATE: {time}</span>
      </div>
      <div className="status-bar-center">
        <span className="status-mode-badge">LIVE DATA</span>
      </div>
      <div className="status-bar-right">
        <button className="status-link" onClick={() => alert('TerminalX v1.0.0\nAI-powered market terminal.')}>ABOUT</button>
        <button className="status-link" onClick={() => alert('Help documentation is currently being compiled.')}>HELP</button>
        <button className="status-link" onClick={() => alert('Keyboard Shortcuts:\nCmd/Ctrl+K: Command Palette\nCmd/Ctrl+J: Toggle AI Panel\nEsc: Close Panels')}>SHORTCUTS</button>
      </div>
    </footer>
  );
}
