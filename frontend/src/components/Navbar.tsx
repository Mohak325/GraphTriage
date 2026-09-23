"use client";

import { useState } from "react";
import {
  Bell,
  Play,
  RotateCcw,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Server,
} from "lucide-react";
import { triggerRCA } from "@/lib/api";

interface NavbarProps {
  onTriggerRCA?: (rcaId: string) => void;
}

export function Navbar({ onTriggerRCA }: NavbarProps) {
  const [isTriggering, setIsTriggering] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  const handleTrigger = async () => {
    setIsTriggering(true);
    try {
      const result = await triggerRCA("INC-9821", 30);
      setNotification(`RCA Job Started: ${result.rca_id}`);
      if (onTriggerRCA) {
        onTriggerRCA(result.rca_id);
      }
    } catch (err) {
      setNotification("Failed to trigger RCA");
    } finally {
      setIsTriggering(false);
      setTimeout(() => setNotification(null), 4000);
    }
  };

  return (
    <header className="h-16 border-b border-surface-border/50 bg-surface/50 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Left: System Badge & Status */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-accent-emerald/10 border border-accent-emerald/30 text-accent-emerald text-xs font-mono">
          <span className="w-2 h-2 rounded-full bg-accent-emerald animate-pulse" />
          <span>Graph Engine: Connected</span>
        </div>
        <div className="hidden md:flex items-center gap-2 text-xs text-slate-400 font-mono">
          <Server className="w-3.5 h-3.5 text-slate-500" />
          <span>Neo4j Bolt 5.x</span>
          <span className="text-slate-600">•</span>
          <span>FastAPI</span>
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        {notification && (
          <div className="flex items-center gap-2 px-3 py-1 rounded-md bg-accent-cyan/10 border border-accent-cyan/40 text-accent-cyan text-xs font-mono animate-fade-in">
            <Zap className="w-3.5 h-3.5" />
            <span>{notification}</span>
          </div>
        )}

        <button
          onClick={handleTrigger}
          disabled={isTriggering}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-accent-cyan to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-semibold text-xs transition-all shadow-md shadow-cyan-500/20 active:scale-95 disabled:opacity-50"
        >
          {isTriggering ? (
            <RotateCcw className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Play className="w-3.5 h-3.5 fill-current" />
          )}
          <span>{isTriggering ? "Triggering..." : "Trigger RCA Pipeline"}</span>
        </button>

        <div className="w-px h-6 bg-surface-border/60 mx-1" />

        <div className="w-8 h-8 rounded-lg bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-slate-300 hover:text-white transition-colors cursor-pointer relative">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-accent-rose" />
        </div>
      </div>
    </header>
  );
}
