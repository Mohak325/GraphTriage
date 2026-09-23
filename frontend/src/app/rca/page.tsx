"use client";

import React, { useState, useEffect } from "react";
import { RCAResults } from "@/components/RCAResults";
import { getRCAResult, getRecentIncidents } from "@/lib/api";
import { RCAResult, IncidentSummary } from "@/lib/types";
import { ShieldAlert, RefreshCw, Filter } from "lucide-react";

export default function RCAPage() {
  const [rcaResult, setRcaResult] = useState<RCAResult | null>(null);
  const [incidents, setIncidents] = useState<IncidentSummary[]>([]);
  const [selectedRcaId, setSelectedRcaId] = useState<string>("rca-20260924-001");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    getRecentIncidents().then((list) => setIncidents(list));
  }, []);

  useEffect(() => {
    setIsLoading(true);
    getRCAResult(selectedRcaId)
      .then((res) => {
        setRcaResult(res);
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, [selectedRcaId]);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Title & Incident Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-accent-rose" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-mono tracking-tight">
              Root Cause Analysis (RCA) Results
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Formal diagnosis, multimodal evidence chains, and counterfactual validation verdicts
          </p>
        </div>

        {/* Incident Selector Dropdown */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={selectedRcaId}
            onChange={(e) => setSelectedRcaId(e.target.value)}
            className="px-3 py-2 rounded-lg bg-surface border border-surface-border text-xs font-mono text-slate-200 focus:outline-none focus:border-accent-cyan"
          >
            {incidents.map((inc) => (
              <option key={inc.rca_id} value={inc.rca_id}>
                {inc.incident_id} — {inc.root_cause_service} ({inc.severity})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main RCAResults View */}
      {rcaResult && <RCAResults result={rcaResult} isLoading={isLoading} />}
    </div>
  );
}
