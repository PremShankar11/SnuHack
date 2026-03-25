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
  const { simulatedDate, refreshKey, isSimulating } = useSimulation();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDashboard() {
      setLoading(true);
      setError(null);
      try {
        // Fetch from Quant Engine
        const res = await fetch("http://localhost:8000/quant/api/dashboard");
        if (res.ok) {
          const json = await res.json();
          
          // Transform Quant Engine response to match UI expectations
          const globalState = json.global_state;
          const transformedData = {
            vitals: {
              totalBank: globalState.plaid_balance,
              phantomUsable: globalState.phantom_usable_cash,
              daysToZero: globalState.runway_metrics.days_to_zero,
              lockedFunds: globalState.locked_tier_0_funds,
              survivalProb: globalState.runway_metrics.monte_carlo_survival_prob,
              breachDate: globalState.runway_metrics.liquidity_breach_date,
            },
            sparkline: globalState.cashflow_projection_array.map((item: any) => ({
              day: item.date,
              phantom: item.balance,
            })),
            actions: [], // Will be populated from inbox endpoint
            simulatedDate: globalState.simulated_as_of,
          };
          
          setData(transformedData);
        } else {
          setError(`Failed to fetch dashboard: ${res.status}`);
        }
      } catch (err) {
        console.error("Failed to fetch dashboard", err);
        setError("Network error - is the backend running?");
      } finally {
        setLoading(false);
      }
    }
    fetchDashboard();
  }, [refreshKey]);

  if (loading) {
    return (
      <div className="p-8">
        <div className="max-w-5xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="grid grid-cols-3 gap-5 mb-8">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-gray-100 rounded-2xl h-32"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="max-w-5xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
            <p className="text-red-700 font-semibold">Error loading dashboard</p>
            <p className="text-red-600 text-sm mt-2">{error}</p>
            <p className="text-red-500 text-xs mt-2">
              Make sure the backend is running: <code className="bg-red-100 px-2 py-1 rounded">python main.py</code>
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const { vitals, sparkline } = data;
  const runwayDanger = vitals.daysToZero < 14;
  const survivalDanger = vitals.survivalProb < 0.5;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Executive Summary</h1>
        <p className="text-sm text-gray-400 mt-1">
          Real-time cash intelligence · Simulated as of {data.simulatedDate || simulatedDate}
        </p>
        <div className="mt-2 flex items-center gap-2">
          <span className="text-xs bg-emerald-50 border border-emerald-200 text-emerald-700 px-2 py-1 rounded-full font-medium">
            Quant Engine Active
          </span>
          <span className="text-xs bg-blue-50 border border-blue-200 text-blue-700 px-2 py-1 rounded-full font-medium">
            Monte Carlo: {(vitals.survivalProb * 100).toFixed(0)}% Survival
          </span>
        </div>
      </div>

      {/* Vitals */}
      <div className="grid grid-cols-3 gap-5 mb-8">
        {/* Total Bank */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-widest mb-3">Total Bank Balance</p>
          <p className="text-3xl font-black text-gray-400">{fmt(vitals.totalBank)}</p>
          <p className="text-xs text-gray-300 mt-2">Gross — includes locked obligations</p>
          {vitals.lockedFunds > 0 && (
            <p className="text-xs text-amber-500 mt-1 font-medium">
              {fmt(vitals.lockedFunds)} locked (Tier 0)
            </p>
          )}
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
            {vitals.daysToZero === 999 ? "∞" : `${vitals.daysToZero} Days`}
          </p>
          {runwayDanger && vitals.breachDate && (
            <p className="text-xs text-red-500 mt-2 flex items-center gap-1 font-semibold">
              <AlertTriangle size={11} /> Breach: {vitals.breachDate}
            </p>
          )}
          {!runwayDanger && (
            <p className="text-xs text-emerald-500 mt-2 flex items-center gap-1">
              <CheckCircle2 size={11} /> Healthy runway
            </p>
          )}
        </div>
      </div>

      {/* Bottom row: sparkline + Monte Carlo */}
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
                formatter={(v) => [`${Number(v).toLocaleString()}`, "Phantom Cash"]}
              />
              <Area type="monotone" dataKey="phantom" stroke="#10b981" strokeWidth={2} fill="url(#phantomGrad)" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Monte Carlo Survival */}
        <div className="col-span-2 bg-white rounded-2xl border border-gray-200 shadow-sm p-6 flex flex-col">
          <div className="mb-4">
            <p className="text-sm font-semibold text-gray-800">Monte Carlo Engine</p>
            <p className="text-xs text-gray-400 mt-0.5">1,000 simulations</p>
          </div>
          
          <div className="flex-1 flex items-center justify-center">
            <div className="relative w-32 h-32">
              <svg viewBox="0 0 36 36" className="w-32 h-32 -rotate-90">
                <circle cx="18" cy="18" r="15.9" fill="none" stroke="#f1f5f9" strokeWidth="3" />
                <circle
                  cx="18" cy="18" r="15.9" fill="none"
                  stroke={vitals.survivalProb >= 0.7 ? "#10b981" : vitals.survivalProb >= 0.4 ? "#f59e0b" : "#ef4444"}
                  strokeWidth="3"
                  strokeDasharray={`${vitals.survivalProb * 100} ${100 - vitals.survivalProb * 100}`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-2xl font-black ${survivalDanger ? "text-red-500" : "text-emerald-500"}`}>
                  {(vitals.survivalProb * 100).toFixed(0)}%
                </span>
                <span className="text-[10px] text-gray-400 mt-0.5">Survival</span>
              </div>
            </div>
          </div>
          
          <Link 
            href="/analytics" 
            className="text-xs text-indigo-500 hover:text-indigo-700 flex items-center justify-center gap-0.5 mt-2"
          >
            View Analytics <ChevronRight size={12} />
          </Link>
        </div>
      </div>
    </div>
  );
}
