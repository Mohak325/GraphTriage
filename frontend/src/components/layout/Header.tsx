import React, { useState, useEffect } from 'react';
import { Activity, Clock, AlertTriangle, BarChart2, Shield } from 'lucide-react';

interface HeaderProps {
  wsConnected: boolean;
  activeCount: number;
  activeView?: 'dossier' | 'analysis';
  onViewChange?: (view: 'dossier' | 'analysis') => void;
}

export const Header: React.FC<HeaderProps> = ({
  wsConnected,
  activeCount,
  activeView = 'dossier',
  onViewChange = () => {},
}) => {
  const [time, setTime] = useState<string>(new Date().toUTCString());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date().toUTCString()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="border-b border-neutral-800 bg-[#0D0D0D]/95 backdrop-blur-md px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-40 shadow-2xl">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-neutral-900 border border-neutral-700 rounded-lg text-white animate-glow-white">
          <Activity className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold tracking-tight text-white">Carrier NOC Autonomous RCA</h1>
            <span className="px-2 py-0.5 text-[11px] font-mono font-semibold bg-white text-black rounded-full">
              Person C
            </span>
            <span className="px-2 py-0.5 text-[11px] font-mono font-medium bg-neutral-800 text-neutral-200 border border-neutral-700 rounded-full">
              Layer 4-5
            </span>
          </div>
          <p className="text-[11px] text-neutral-400">RCAEval Real Dataset Benchmark (735 Cases) • D3 Digital Twin & HITL</p>
        </div>
      </div>

      {/* Central View Switcher Tabs */}
      <div className="flex items-center space-x-1.5 bg-neutral-900/90 border border-neutral-800 rounded-lg p-1">
        <button
          onClick={() => onViewChange('dossier')}
          className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-xs font-mono font-semibold transition-all ${
            activeView === 'dossier'
              ? 'bg-white text-black shadow-md'
              : 'text-neutral-400 hover:text-white hover:bg-neutral-800/60'
          }`}
        >
          <Shield className="w-3.5 h-3.5" />
          <span>Live Incident Dossier</span>
        </button>

        <button
          onClick={() => onViewChange('analysis')}
          className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-xs font-mono font-semibold transition-all ${
            activeView === 'analysis'
              ? 'bg-white text-black shadow-md'
              : 'text-neutral-400 hover:text-white hover:bg-neutral-800/60'
          }`}
        >
          <BarChart2 className="w-3.5 h-3.5" />
          <span>Result Analysis (735 Cases)</span>
          <span className={`px-1.5 py-0.5 text-[10px] rounded font-mono ${
            activeView === 'analysis' ? 'bg-neutral-200 text-black font-bold' : 'bg-neutral-800 text-neutral-300 border border-neutral-700'
          }`}>
            87.07% Top-1
          </span>
        </button>
      </div>

      <div className="flex items-center space-x-4 text-xs font-mono">
        <div className="flex items-center space-x-2 text-neutral-300">
          <Clock className="w-3.5 h-3.5 text-white" />
          <span className="text-neutral-300">{time}</span>
        </div>

        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-neutral-900 border border-emerald-900/60">
          <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
          <span className="text-emerald-300 font-medium">
            {wsConnected ? 'AWS Cloud Live (API Gateway)' : 'Connecting to AWS Cloud...'}
          </span>
        </div>

        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-neutral-900 border border-neutral-700 text-neutral-100 font-medium">
          <AlertTriangle className="w-3.5 h-3.5 text-white" />
          <span>{activeCount} Real Cases</span>
        </div>
      </div>
    </header>
  );
};
