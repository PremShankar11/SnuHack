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
  const [monteCarlo, setMonteCarlo] = useState<any>(null);

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
    
    async function fetchMonteCarlo() {
      try {
        const res = await fetch("http://localhost:8000/api/quant/monte-carlo");
        if (res.ok) {
          const json = await res.json();
          setMonteCarlo(json);
        }
      } catch (err) {
        console.error("Failed to fetch Monte Carlo", err);
      }
    }
    
    fetchDashboard();
    fetchMonteCarlo();
  }, [refreshKey]);

  if (!data) return <div className="p-8"><div className="shimmer h-40 rounded-2xl" /></div>;

  const { vitals, sparkline, actions, optimization } = data;
  const runwayDanger = vitals.daysToZero < 14;
  const urgentActions = actions.slice(0, 2);

  // Only show actionable vendors (those with delay_amount > 0)
  const actionableVendors = optimization?.optimized_obligations?.filter(
    (ob: any) => ob.delay_amount > 0
  ) || [];
  
  // Monte Carlo survival color
  const survivalColor = monteCarlo?.survival_probability >= 70 
    ? "#10b981" 
    : monteCarlo?.survival_probability >= 40 
    ? "#f59e0b" 
    : "#ef4444";

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
                labelFormatter={(label: any) => `Day: ${label}`}
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
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-8">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-indigo-50 flex items-center justify-center">
              <Zap size={16} className="text-indigo-600" />
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-800">LP Optimization Strategy</p>
              <p className="text-xs text-gray-400 mt-0.5">
                {!optimization || optimization.status === "UNAVAILABLE"
                  ? "Optimization engine unavailable"
                  : optimization.status === "SUCCESS"
                  ? `${actionableVendors.length} vendor${actionableVendors.length !== 1 ? "s" : ""} with recommended actions`
                  : optimization.status === "NO_OPTIMIZATION_NEEDED"
                  ? "All obligations covered — no changes needed"
                  : optimization.status === "PARTIAL_OPTIMIZATION"
                  ? `Best-effort strategy — ${optimization.coverage_pct}% of shortfall covered`
                  : optimization.status === "OPTIMIZATION_FAILED"
                  ? "Optimization could not be computed"
                  : "Computing optimization..."}
              </p>
            </div>
          </div>
          {optimization?.breach_prevented && (
            <span className="text-[10px] bg-emerald-50 border border-emerald-200 text-emerald-600 font-semibold px-2.5 py-1 rounded-full uppercase tracking-wide flex items-center gap-1">
              <Shield size={10} /> Breach Prevented
            </span>
          )}
          {optimization?.status === "PARTIAL_OPTIMIZATION" && !optimization.breach_prevented && (
            <span className="text-[10px] bg-amber-50 border border-amber-200 text-amber-600 font-semibold px-2.5 py-1 rounded-full uppercase tracking-wide">
              Partial Coverage
            </span>
          )}
        </div>

        {(!optimization || optimization.status === "UNAVAILABLE") && (
          <div className="bg-gray-50 border border-gray-100 rounded-xl px-4 py-3 flex items-center gap-3">
            <AlertTriangle size={16} className="text-gray-400 shrink-0" />
            <p className="text-xs text-gray-600">
              LP optimization engine is currently unavailable. Check backend logs for details.
            </p>
          </div>
        )}

        {optimization?.status === "NO_OPTIMIZATION_NEEDED" && (
          <div className="bg-emerald-50 border border-emerald-100 rounded-xl px-4 py-3 flex items-center gap-3">
            <CheckCircle2 size={16} className="text-emerald-500 shrink-0" />
            <p className="text-xs text-emerald-700">
              Current balance fully covers all upcoming obligations. No payment deferrals needed.
            </p>
          </div>
        )}

        {optimization?.status === "PARTIAL_OPTIMIZATION" && optimization.remaining_shortfall > 0 && (
          <div className="bg-amber-50 border border-amber-100 rounded-xl px-4 py-3 flex items-center gap-3 mb-4">
            <AlertTriangle size={16} className="text-amber-500 shrink-0" />
            <p className="text-xs text-amber-700">
              <span className="font-semibold">Tier constraints limit deferrals.</span> Covered {optimization.coverage_pct}% of the {fmt(optimization.shortfall)} shortfall.
              Remaining gap: <span className="font-bold">{fmt(optimization.remaining_shortfall)}</span> — manual intervention recommended.
            </p>
          </div>
        )}

        {/* Chain of Thought from LP solver */}
        {optimization?.chain_of_thought && optimization.chain_of_thought.length > 0 && (
          <div className="mb-4">
            <p className="text-[10px] text-gray-400 uppercase tracking-widest font-semibold mb-3">Decision Audit Trail</p>
            <div className="flex flex-col gap-2">
              {optimization.chain_of_thought.map((step: any, idx: number) => (
                <div key={idx} className="flex items-start gap-3">
                  <span className="w-5 h-5 rounded-full bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600 text-[9px] font-bold shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <div>
                    <p className="text-xs font-semibold text-gray-700">{step.label}</p>
                    <p className="text-[11px] text-gray-500">{step.detail}</p>
                  </div>
                </div>
              ))}
            </div>
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
                      Due {ob.original_due} · Goodwill: {ob.goodwill_score ?? "N/A"}/100 · Max defer: {ob.max_allowed_delay_pct}%
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
                {optimization.projected_savings > 0 && (
                  <p className="text-xs text-indigo-500">
                    Est. savings: {fmt(optimization.projected_savings)}
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Monte Carlo Survival Analysis */}
      {monteCarlo && (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <div className="flex items-center gap-2 mb-5">
            <div className="w-8 h-8 rounded-xl bg-purple-50 flex items-center justify-center">
              <TrendingDown size={16} className="text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-800">Monte Carlo Survival Analysis</p>
              <p className="text-xs text-gray-400 mt-0.5">
                {monteCarlo.simulations.toLocaleString()} simulations · Probabilistic cash flow modeling
              </p>
            </div>
          </div>

          <div className="grid grid-cols-4 gap-4">
            {/* Survival Probability Ring */}
            <div className="col-span-1 flex flex-col items-center justify-center">
              <div className="relative w-28 h-28">
                <svg viewBox="0 0 36 36" className="w-28 h-28 -rotate-90">
                  <circle cx="18" cy="18" r="15.9" fill="none" stroke="#f1f5f9" strokeWidth="2.5" />
                  <circle
                    cx="18" cy="18" r="15.9" fill="none"
                    stroke={survivalColor}
                    strokeWidth="2.5"
                    strokeDasharray={`${monteCarlo.survival_probability} ${100 - monteCarlo.survival_probability}`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-2xl font-black text-gray-800">{monteCarlo.survival_probability}%</span>
                  <span className="text-[9px] text-gray-400 uppercase tracking-wide">Survival</span>
                </div>
              </div>
            </div>

            {/* Balance Projections */}
            <div className="col-span-3 grid grid-cols-3 gap-3">
              <div className="bg-red-50 border border-red-100 rounded-xl p-4 text-center">
                <p className="text-[10px] text-red-400 uppercase tracking-wide mb-2 font-semibold">P10 (Bear Case)</p>
                <p className="text-xl font-black text-red-600">{fmt(monteCarlo.p10_balance)}</p>
                <p className="text-[9px] text-red-400 mt-1">10th percentile</p>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center">
                <p className="text-[10px] text-gray-400 uppercase tracking-wide mb-2 font-semibold">Median (Expected)</p>
                <p className="text-xl font-black text-gray-700">{fmt(monteCarlo.median_balance)}</p>
                <p className="text-[9px] text-gray-400 mt-1">50th percentile</p>
              </div>

              <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-4 text-center">
                <p className="text-[10px] text-emerald-400 uppercase tracking-wide mb-2 font-semibold">P90 (Bull Case)</p>
                <p className="text-xl font-black text-emerald-600">{fmt(monteCarlo.p90_balance)}</p>
                <p className="text-[9px] text-emerald-400 mt-1">90th percentile</p>
              </div>
            </div>
          </div>

          <div className="mt-4 bg-purple-50 border border-purple-100 rounded-xl px-4 py-2.5">
            <p className="text-xs text-purple-700">
              <span className="font-semibold">Methodology:</span> Simulates {monteCarlo.simulations.toLocaleString()} scenarios with randomized payment delays, 
              invoice latency variance, and 5% receivable default rate to model cash flow uncertainty.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
