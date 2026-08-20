/* ═══════════════════════════════════════════════════════
 * TerminalX — Sparkline (Mini Chart)
 * ═══════════════════════════════════════════════════════ */
'use client';

import { useRef, useEffect } from 'react';

interface SparklineProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  showGradient?: boolean;
}

export function Sparkline({
  data,
  width = 80,
  height = 28,
  color,
  showGradient = true,
}: SparklineProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || data.length < 2) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, width, height);

    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    const padding = 2;

    // Determine color from trend
    const lineColor = color || (data[data.length - 1] >= data[0] ? '#00e676' : '#ff1744');

    // Draw line
    ctx.beginPath();
    ctx.strokeStyle = lineColor;
    ctx.lineWidth = 1.5;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';

    for (let i = 0; i < data.length; i++) {
      const x = (i / (data.length - 1)) * (width - padding * 2) + padding;
      const y = height - padding - ((data[i] - min) / range) * (height - padding * 2);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Draw gradient fill
    if (showGradient) {
      ctx.lineTo(width - padding, height);
      ctx.lineTo(padding, height);
      ctx.closePath();

      const gradient = ctx.createLinearGradient(0, 0, 0, height);
      const rgb = lineColor === '#00e676' ? '0, 230, 118' : '255, 23, 68';
      gradient.addColorStop(0, `rgba(${rgb}, 0.15)`);
      gradient.addColorStop(1, `rgba(${rgb}, 0)`);
      ctx.fillStyle = gradient;
      ctx.fill();
    }
  }, [data, width, height, color, showGradient]);

  return (
    <div className="sparkline-container">
      <canvas
        ref={canvasRef}
        style={{ width: `${width}px`, height: `${height}px` }}
      />
    </div>
  );
}
