/* ═══════════════════════════════════════════════════════
 * TerminalX — Terminal Layout (Main Grid)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useEffect } from 'react';
import { TopBar } from './TopBar';
import { SideNav } from './SideNav';
import { LeftPanel } from './LeftPanel';
import { CenterPanel } from './CenterPanel';
import { RightPanel } from './RightPanel';
import { BottomPanel } from './BottomPanel';
import { StatusBar } from './StatusBar';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useMarketData } from '@/hooks/useMarketData';
import { useNews } from '@/hooks/useNews';
import { useCommandStore } from '@/stores/commandStore';

export function TerminalLayout() {
  const { isConnected } = useWebSocket();
  useMarketData();
  useNews();
  const setOpen = useCommandStore((s) => s.setOpen);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
        e.preventDefault();
        setOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setOpen]);

  return (
    <div className="terminal-layout">
      <TopBar />
      <SideNav />
      <LeftPanel />
      <CenterPanel />
      <RightPanel />
      <BottomPanel />
      <StatusBar isConnected={isConnected} />
    </div>
  );
}
