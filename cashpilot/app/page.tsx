"use client";
import { useState, useEffect } from "react";
import { useSimulation } from "./context/SimulationContext";
import { TrendingDown, AlertTriangle, CheckCircle2, ChevronRight } from "lucide-react";
import Link from "next/link";
import { ResponsiveContainer, AreaChart, Area, Tooltip, ReferenceLine } from "recharts";

function fmt(n: number) {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

const priorityColor: Record<string, string> = {
  critical: "bg-red-50 border-red-200 text-red-700",
  high: "bg-amber-50 border-amber-200 text-amber-700",
  medium: "bg-blue-50 border-blue-200 text-blue-700",
};

export default function DashboardPage() {
  const { simulatedDate } = useSimulation();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    async function fetchDashboard() {
      try {
        const res = await fetch("http://localhost:8000/api/dashboard");
        if (res.ok) {
          const json = await res.json();
          setData(json);
        }
      } catch (err) {
        console.error("Failed to fetch dashboard", err);
      }
    }
    fetchDashboard();
  }, [simulatedDate]);

  if (!data) return <div className="p-8"><p>Loading simulation data...</p></div>;

  const { vitals, sparkline, actions } = data;
  const runwayDanger = vitals.daysToZero < 14;
  const urgentActions = actions.slice(0, 2);

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Executive Summary</h1>
        <p className="text-sm text-gray-400 mt-1">Real-time cash intelligence · Simulated as of {simulatedDate}</p>
      </div>

      {/* Vitals */}
      <div className="grid grid-cols-3 gap-5 mb-8">
        {/* Total Bank */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-widest mb-3">Total Bank Balance</p>
          <p className="text-3xl font-black text-gray-400">{fmt(vitals.totalBank)}</p>
          <p className="text-xs text-gray-300 mt-2">Gross — includes locked obligations</p>
        </div>

        {/* Phantom Usable */}
        <div className="bg-white rounded-2xl border border-emerald-200 shadow-sm p-6">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-widest mb-3">Phantom Usable Cash</p>
          <p className="text-3xl font-black text-emerald-500">{fmt(vitals.phantomUsable)}</p>
          <p className="text-xs text-emerald-400 mt-2 flex items-center gap-1">
            <CheckCircle2 size={11} /> Taxes &amp; payroll ring-fenced
          </p>
        </div>

        {/* Days to Zero */}
        <div className={`bg-white rounded-2xl border shadow-sm p-6 ${runwayDanger ? "border-red-200" : "border-gray-200"}`}>
          <p className="text-xs font-medium text-gray-400 uppercase tracking-widest mb-3">Days to Zero (Runway)</p>
          <p className={`text-3xl font-black ${runwayDanger ? "text-red-500" : "text-gray-800"}`}>
            {vitals.daysToZero} Days
          </p>
          {runwayDanger && (
            <p className="text-xs text-red-500 mt-2 flex items-center gap-1 font-semibold">
              <AlertTriangle size={11} /> Critical — under 14 days
            </p>
          )}
        </div>
      </div>

      {/* Bottom row: sparkline + urgent actions */}
      <div className="grid grid-cols-5 gap-5">
        {/* Sparkline */}
        <div className="col-span-3 bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm font-semibold text-gray-800">14-Day Cash Runway</p>
              <p className="text-xs text-gray-400 mt-0.5">Phantom usable projection</p>
            </div>
            {runwayDanger && <TrendingDown size={16} className="text-red-400" />}
          </div>
          <ResponsiveContainer width="100%" height={120}>
            <AreaChart data={sparkline} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="phantomGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <ReferenceLine y={0} stroke="#ef4444" strokeDasharray="3 2" strokeWidth={1} />
              <Tooltip
                contentStyle={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 8, fontSize: 11 }}
                formatter={(v) => [`$${Number(v).toLocaleString()}`, "Phantom Cash"]}
              />
              <Area type="monotone" dataKey="phantom" stroke="#10b981" strokeWidth={2} fill="url(#phantomGrad)" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Urgent Actions */}
        <div className="col-span-2 bg-white rounded-2xl border border-gray-200 shadow-sm p-6 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm font-semibold text-gray-800">Urgent Actions</p>
            <Link href="/inbox" className="text-xs text-indigo-500 hover:text-indigo-700 flex items-center gap-0.5">
              View all <ChevronRight size={12} />
            </Link>
          </div>
          <div className="flex flex-col gap-3 flex-1">
            {urgentActions.length === 0 ? (
              <p className="text-xs text-gray-400">No urgent actions pending.</p>
            ) : (
              urgentActions.map((a: any) => (
                <Link key={a.id} href="/inbox" className={`rounded-xl border px-3 py-2.5 text-xs font-medium transition-all hover:shadow-sm ${priorityColor[a.priority]}`}>
                  <p className="font-semibold truncate">{a.title}</p>
                  <p className="opacity-70 mt-0.5 text-[11px]">{a.subtitle}</p>
                </Link>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
