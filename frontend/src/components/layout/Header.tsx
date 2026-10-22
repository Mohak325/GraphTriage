import React, { useState, useEffect } from 'react';
import { Activity, Clock, AlertTriangle } from 'lucide-react';

interface HeaderProps {
  wsConnected: boolean;
  activeCount: number;
}

export const Header: React.FC<HeaderProps> = ({ wsConnected, activeCount }) => {
  const [time, setTime] = useState<string>(new Date().toUTCString());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date().toUTCString()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="border-b border-gray-800 bg-gray-900/90 backdrop-blur-md px-6 py-4 flex flex-wrap items-center justify-between sticky top-0 z-40 shadow-xl">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400 animate-glow-cyan">
          <Activity className="w-6 h-6" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold tracking-tight text-white">Carrier NOC Autonomous RCA</h1>
            <span className="px-2 py-0.5 text-xs font-semibold bg-cyan-900/50 text-cyan-300 border border-cyan-700/50 rounded-full">
              Person C
            </span>
            <span className="px-2 py-0.5 text-xs font-semibold bg-purple-900/50 text-purple-300 border border-purple-700/50 rounded-full">
              Layer 4-5
            </span>
          </div>
          <p className="text-xs text-slate-400">Grounded in 15 Peer-Reviewed Papers (2023–2026) • 5G SBA & NFV-MANO</p>
        </div>
      </div>

      <div className="flex items-center space-x-6 text-sm">
        <div className="flex items-center space-x-2 text-slate-300">
          <Clock className="w-4 h-4 text-cyan-400" />
          <span className="font-mono text-xs text-slate-300">{time}</span>
        </div>

        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-gray-800 border border-gray-700 text-xs">
          <span className={`w-2.5 h-2.5 rounded-full ${wsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
          <span className="text-slate-300">{wsConnected ? 'WebSocket Live' : 'Disconnected'}</span>
        </div>

        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-rose-950/40 border border-rose-800/50 text-rose-300 text-xs font-medium">
          <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
          <span>{activeCount} Active Incidents</span>
        </div>
      </div>
    </header>
  );
};
