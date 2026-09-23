"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Network,
  Activity,
  Bot,
  ShieldAlert,
  GitBranch,
  Terminal,
} from "lucide-react";

const NAV_ITEMS = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    badge: "Live",
  },
  {
    name: "Graph Topology",
    href: "/graph",
    icon: Network,
    badge: "Neo4j",
  },
  {
    name: "RCA Diagnosis",
    href: "/rca",
    icon: ShieldAlert,
    badge: "Verified",
  },
  {
    name: "Agent Monitor",
    href: "/agents",
    icon: Bot,
    badge: "LangGraph",
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 flex-shrink-0 bg-surface/80 border-r border-surface-border/60 flex flex-col justify-between h-screen sticky top-0 z-30 backdrop-blur-md">
      {/* Brand Header */}
      <div>
        <div className="p-6 border-b border-surface-border/40">
          <Link href="/dashboard" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-cyan via-accent-violet to-accent-emerald flex items-center justify-center shadow-lg shadow-accent-cyan/20 group-hover:scale-105 transition-transform duration-200">
              <Network className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-wider text-white flex items-center gap-1.5">
                GRAPH<span className="text-accent-cyan">TRIAGE</span>
              </span>
              <span className="text-[10px] tracking-widest uppercase text-slate-400 block font-medium">
                Multi-Agent RCA Engine
              </span>
            </div>
          </Link>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-1.5">
          <div className="px-3 py-2 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Core Modules
          </div>
          {NAV_ITEMS.map((item) => {
            const isActive =
              pathname === item.href || (item.href === "/dashboard" && pathname === "/");
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group ${
                  isActive
                    ? "bg-accent-cyan/15 text-accent-cyan border border-accent-cyan/30 shadow-sm shadow-accent-cyan/10"
                    : "text-slate-400 hover:text-white hover:bg-slate-800/50"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 transition-colors ${
                      isActive ? "text-accent-cyan" : "text-slate-400 group-hover:text-white"
                    }`}
                  />
                  <span>{item.name}</span>
                </div>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                    isActive
                      ? "bg-accent-cyan/20 text-accent-cyan font-semibold"
                      : "bg-slate-800/80 text-slate-400 group-hover:bg-slate-700"
                  }`}
                >
                  {item.badge}
                </span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer / System Status */}
      <div className="p-4 border-t border-surface-border/40 space-y-3">
        {/* Agent Trio Status Widget */}
        <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 font-medium">Agents Online</span>
            <span className="flex items-center gap-1.5 text-accent-emerald text-[11px] font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald animate-pulse"></span>
              3 / 3 Active
            </span>
          </div>
          <div className="grid grid-cols-3 gap-1 text-[10px] text-center font-mono">
            <div className="py-1 rounded bg-slate-800/60 text-slate-300 border border-slate-700/50">
              Nav
            </div>
            <div className="py-1 rounded bg-slate-800/60 text-slate-300 border border-slate-700/50">
              Diag
            </div>
            <div className="py-1 rounded bg-slate-800/60 text-slate-300 border border-slate-700/50">
              Verif
            </div>
          </div>
        </div>

        {/* User Credit */}
        <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono px-1">
          <span className="flex items-center gap-1">
            <Terminal className="w-3 h-3 text-slate-400" /> PC 3: Aarnav
          </span>
          <span className="text-[10px] text-slate-600">v0.3-beta</span>
        </div>
      </div>
    </aside>
  );
}
