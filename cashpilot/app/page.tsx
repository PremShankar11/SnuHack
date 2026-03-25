"use client";
import { useState, useEffect } from "react";
import { useSimulation } from "./context/SimulationContext";
import { TrendingDown, AlertTriangle, CheckCircle2, ChevronRight, Zap, Shield, Clock } from "lucide-react";
import Link from "next/link";
import { ResponsiveContainer, AreaChart, Area, Tooltip, ReferenceLine, XAxis } from "recharts";

function fmt(n: number) {
  return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

const priorityColor: Record<string, string> = {
  critical: "bg-red-50 border-red-200 text-red-700",
  high: "bg-amber-50 border-amber-200 text-amber-700",
  medium: "bg-blue-50 border-blue-200 text-blue-700",
};

const tierStyle: Record<number, { bg: string; text: string; label: string }> = {
  0: { bg: "bg-red-100", text: "text-red-700", label: "Locked" },
  1: { bg: "bg-amber-100", text: "text-amber-700", label: "Penalty" },
  2: { bg: "bg-blue-100", text: "text-blue-700", label: "Relational" },
  3: { bg: "bg-emerald-100", text: "text-emerald-700", label: "Flexible" },
};

export default function DashboardPage() {
  const { simulatedDate, refreshKey, isSimulating } = useSimulation();
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
  }, [refreshKey]);

  if (!data) return <div className="p-8"><div className="shimmer h-40 rounded-2xl" /></div>;

  const { vitals, sparkline, actions, optimization } = data;
  const runwayDanger = vitals.daysToZero < 14;
  const urgentActions = actions.slice(0, 2);

  // Only show actionable vendors (those with delay_amount > 0)
  const actionableVendors = optimization?.optimized_obligations?.filter(
    (ob: any) => ob.delay_amount > 0
  ) || [];

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
      <div className="grid grid-cols-5 gap-5 mb-8">
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
              <XAxis dataKey="day" tick={{ fill: "#94a3b8", fontSize: 9 }} tickLine={false} axisLine={false} interval={2} />
              <ReferenceLine y={0} stroke="#ef4444" strokeDasharray="3 2" strokeWidth={1} />
              <Tooltip
                contentStyle={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 8, fontSize: 11 }}
                formatter={(v: any) => [`$${Number(v).toLocaleString()}`, "Phantom Cash"]}
                labelFormatter={(label: string) => `Day: ${label}`}
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

      {/* LP Solver Optimization Strategy */}
      {optimization && optimization.status !== "UNAVAILABLE" && (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-indigo-50 flex items-center justify-center">
                <Zap size={16} className="text-indigo-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-800">LP Optimization Strategy</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {optimization.status === "SUCCESS"
                    ? `${actionableVendors.length} vendor${actionableVendors.length !== 1 ? "s" : ""} with recommended actions`
                    : optimization.status === "NO_OPTIMIZATION_NEEDED"
                    ? "All obligations covered — no changes needed"
                    : "Optimization could not be computed"}
                </p>
              </div>
            </div>
            {optimization.status === "SUCCESS" && optimization.breach_prevented && (
              <span className="text-[10px] bg-emerald-50 border border-emerald-200 text-emerald-600 font-semibold px-2.5 py-1 rounded-full uppercase tracking-wide flex items-center gap-1">
                <Shield size={10} /> Breach Prevented
              </span>
            )}
          </div>

          {optimization.status === "NO_OPTIMIZATION_NEEDED" && (
            <div className="bg-emerald-50 border border-emerald-100 rounded-xl px-4 py-3 flex items-center gap-3">
              <CheckCircle2 size={16} className="text-emerald-500 shrink-0" />
              <p className="text-xs text-emerald-700">
                Current balance fully covers all upcoming obligations. No payment deferrals needed.
              </p>
            </div>
          )}

          {actionableVendors.length > 0 && (
            <div className="flex flex-col gap-3">
              {actionableVendors.map((ob: any, idx: number) => {
                const ts = tierStyle[ob.ontology_tier] || tierStyle[3];
                return (
                  <div key={ob.obligation_id || idx} className="bg-gray-50 rounded-xl border border-gray-100 px-5 py-4 flex items-center gap-4">
                    {/* Vendor info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-semibold text-gray-800 truncate">{ob.entity_name}</p>
                        <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${ts.bg} ${ts.text} uppercase tracking-wide`}>
                          Tier {ob.ontology_tier} · {ts.label}
                        </span>
                      </div>
                      <p className="text-xs text-gray-400">
                        Due {ob.original_due} · Goodwill: {ob.goodwill_score ?? "N/A"}/100
                      </p>
                    </div>

                    {/* Pay now / Delay split */}
                    <div className="flex items-center gap-3 shrink-0">
                      <div className="text-center">
                        <p className="text-[10px] text-gray-400 mb-0.5">Pay Now</p>
                        <p className="text-sm font-bold text-emerald-600">{fmt(ob.pay_now)}</p>
                      </div>
                      <div className="w-px h-8 bg-gray-200" />
                      <div className="text-center">
                        <p className="text-[10px] text-gray-400 mb-0.5">Delay</p>
                        <p className="text-sm font-bold text-amber-600">{fmt(ob.delay_amount)}</p>
                      </div>
                      <div className="w-px h-8 bg-gray-200" />
                      <div className="text-center">
                        <p className="text-[10px] text-gray-400 mb-0.5 flex items-center gap-0.5"><Clock size={9} /> New Due</p>
                        <p className="text-xs font-semibold text-gray-600">{ob.new_due_date}</p>
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Summary footer */}
              {optimization.total_delayed > 0 && (
                <div className="flex items-center justify-between bg-indigo-50 border border-indigo-100 rounded-xl px-4 py-3 mt-1">
                  <p className="text-xs text-indigo-700 font-medium">
                    Total deferred: <span className="font-bold">{fmt(optimization.total_delayed)}</span>
                  </p>
                  <p className="text-xs text-indigo-500">
                    Est. cost: {fmt(optimization.projected_savings)} saved vs. full penalties
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
