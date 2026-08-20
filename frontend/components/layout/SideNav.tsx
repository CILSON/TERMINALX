/* ═══════════════════════════════════════════════════════
 * TerminalX — Side Navigation Bar
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useCommandStore } from '@/stores/commandStore';
import { useNewsStore } from '@/stores/newsStore';

export function SideNav() {
  const setActiveView = useCommandStore((s) => s.setActiveView);
  const selectArticle = useNewsStore((s) => s.selectArticle);

  const navItems = [
    { icon: 'HME', label: 'Home', action: () => { selectArticle(null); setActiveView('market'); } },
    { icon: 'MKT', label: 'Markets', action: () => { selectArticle(null); setActiveView('heatmap'); } },
    { icon: 'NWS', label: 'News', action: () => { selectArticle(null); setActiveView('news'); } },
    { icon: 'CAL', label: 'Calendar', action: () => { selectArticle(null); setActiveView('calendar'); } },
    { icon: 'CFG', label: 'Settings', action: () => { alert('Settings panel coming soon'); } },
  ];

  return (
    <nav className="side-nav">
      {navItems.map((item) => (
        <button
          key={item.label}
          className="side-nav-btn"
          onClick={item.action}
          title={item.label}
        >
          <span className="side-nav-icon">{item.icon}</span>
        </button>
      ))}
    </nav>
  );
}
