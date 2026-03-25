"use client";
import { useState, useEffect } from "react";
import { useSimulation } from "../context/SimulationContext";
import { mockState } from "../mockState";
import { API_URL } from "../lib/api";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  ReferenceLine, CartesianGrid, Legend,
} from "recharts";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from "recharts";

type AnalyticsData = {
  cashFlow: { day: string; standard: number; phantom: number }[];
  vendors: { name: string; goodwill: number }[];
  monteCarlo: { simulations: number; probability: number; p10: number; median: number; p90: number };
};

export default function AnalyticsPage() {
  const { refreshKey, isSimulating, simulatedDate } = useSimulation();
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [decisionData, setDecisionData] = useState<any>(null);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        // Fetch all data from Quant Engine and legacy analytics
        const [analyticsRes, decisionRes, dashboardRes] = await Promise.all([
          fetch(`${API_URL}/api/analytics`),
          fetch(`${API_URL}/quant/api/decision`),
          fetch(`${API_URL}/quant/api/dashboard`),
        ]);

        if (analyticsRes.ok) {
          const json = await analyticsRes.json();
          setData(json);
        }

        if (decisionRes.ok) {
          const decisionJson = await decisionRes.json();
          setDecisionData(decisionJson.solver_directive);
        }

        if (dashboardRes.ok) {
          const dashboardJson = await dashboardRes.json();
          setDashboardData(dashboardJson.global_state);
        }
      } catch (err) {
        console.error("Failed to fetch analytics data", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [refreshKey]);

  if (loading || !data) {
    return (
      <div className="p-8 max-w-5xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-sm text-gray-400 mt-1">Loading live data from Supabase…</p>
        </div>
        <div className="shimmer h-72 rounded-2xl mb-6" />
        <div className="grid grid-cols-2 gap-6">
          <div className="shimmer h-64 rounded-2xl" />
          <div className="shimmer h-64 rounded-2xl" />
        </div>
      </div>
    );
  }

  const { cashFlow, monteCarlo, vendors } = data;
  const radarData = vendors.map((v) => ({ vendor: v.name, score: v.goodwill }));

  const survivalProb = dashboardData?.runway_metrics?.monte_carlo_survival_prob || 0;
  const breachAmount = decisionData?.breach_amount || 0;
  const hasLiquidityBreach = breachAmount < 0;

  return (
    <div className={`p-8 max-w-5xl mx-auto transition-opacity duration-300 ${isSimulating ? "opacity-60" : "opacity-100"}`}>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-sm text-gray-400 mt-1">
          Live from Supabase · Simulated as of {simulatedDate}
        </p>
        <p className="text-sm text-gray-400 mt-1">Math engine · LP Solver · Monte Carlo</p>
        <div className="mt-2 flex items-center gap-2">
          <span className="text-xs bg-emerald-50 border border-emerald-200 text-emerald-700 px-2 py-1 rounded-full font-medium">
            Quant Engine Active
          </span>
          {hasLiquidityBreach && (
            <span className="text-xs bg-red-50 border border-red-200 text-red-600 px-2 py-1 rounded-full font-medium">
              Liquidity Breach: {breachAmount.toLocaleString("en-US", { style: "currency", currency: "USD" })}
            </span>
          )}
        </div>
      </div>

      {/* Main dual-line chart */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6 fade-in">
        <div className="flex items-start justify-between mb-6">
          <div>
            <p className="text-sm font-semibold text-gray-800">30-Day Cash Projection</p>
            <p className="text-xs text-gray-400 mt-0.5">Standard vs. Phantom (Liquidity Breach visible)</p>
          </div>
          {hasLiquidityBreach && breachAmount < 0 && (
            <span className="text-[10px] bg-red-50 border border-red-200 text-red-600 font-semibold px-2.5 py-1 rounded-full uppercase tracking-wide">
              Liquidity Breach Detected
            </span>
          )}
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={cashFlow} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="day" tick={{ fill: "#94a3b8", fontSize: 10 }} tickLine={false} axisLine={false} interval={4} />
            <YAxis
              tick={{ fill: "#94a3b8", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
              width={40}
            />
            <Tooltip
              contentStyle={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 10, fontSize: 11 }}
              formatter={(v, name) => [`${Number(v).toLocaleString()}`, name === "standard" ? "Standard Balance" : "Phantom Usable"]}
            />
            <Legend
              formatter={(v) => v === "standard" ? "Standard Balance" : "Phantom Usable"}
              wrapperStyle={{ fontSize: 11, color: "#64748b" }}
            />
            <ReferenceLine y={0} stroke="#ef4444" strokeDasharray="4 2" strokeWidth={1.5} label={{ value: "$0 Breach", fill: "#ef4444", fontSize: 10 }} />
            <Line type="monotone" dataKey="standard" stroke="#cbd5e1" strokeWidth={2} dot={false} strokeDasharray="6 3" />
            <Line type="monotone" dataKey="phantom" stroke="#6366f1" strokeWidth={2.5} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Monte Carlo + LP Optimizer Results */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        {/* Monte Carlo */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 fade-in">
          <p className="text-sm font-semibold text-gray-800 mb-1">Monte Carlo Engine</p>
          <p className="text-xs text-gray-400 mb-5">1,000 simulations of invoice payment latency</p>

          {/* Big probability ring */}
          <div className="flex items-center gap-6 mb-6">
            <div className="relative w-24 h-24 shrink-0">
              <svg viewBox="0 0 36 36" className="w-24 h-24 -rotate-90">
                <circle cx="18" cy="18" r="15.9" fill="none" stroke="#f1f5f9" strokeWidth="3" />
                <circle
                  cx="18" cy="18" r="15.9" fill="none"
                  stroke={survivalProb >= 0.7 ? "#10b981" : survivalProb >= 0.4 ? "#f59e0b" : "#ef4444"}
                  strokeWidth="3"
                  strokeDasharray={`${survivalProb * 100} ${100 - survivalProb * 100}`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-xl font-black text-gray-800">{(survivalProb * 100).toFixed(0)}%</span>
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <p className="text-xs font-semibold text-gray-700">Probability of Survival</p>
              <p className="text-[11px] text-gray-400">Based on invoice latency variance across 1,000 runs</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {[
              { label: "P10 (Bear)", value: monteCarlo.p10, color: "text-red-500" },
              { label: "Median", value: monteCarlo.median, color: "text-gray-700" },
              { label: "P90 (Bull)", value: monteCarlo.p90, color: "text-emerald-500" },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-gray-50 rounded-xl p-3 text-center">
                <p className="text-[10px] text-gray-400 mb-1">{label}</p>
                <p className={`text-sm font-bold ${color}`}>${value.toLocaleString()}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Goodwill Radar */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 fade-in">
          <p className="text-sm font-semibold text-gray-800 mb-1">Vendor Goodwill Radar</p>
          <p className="text-xs text-gray-400 mb-4">Ontology health scores by vendor · Live from Supabase</p>
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={radarData} margin={{ top: 0, right: 20, bottom: 0, left: 20 }}>
              <PolarGrid stroke="#f1f5f9" />
              <PolarAngleAxis dataKey="vendor" tick={{ fill: "#94a3b8", fontSize: 10 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#cbd5e1", fontSize: 9 }} />
              <Radar name="Goodwill" dataKey="score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.15} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* LP Optimizer Results */}
      {decisionData?.optimization_result && decisionData.optimization_result.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <div className="mb-4">
            <p className="text-sm font-semibold text-gray-800">LP Optimizer Results</p>
            <p className="text-xs text-gray-400 mt-0.5">
              Payment decisions optimized to minimize late fees + goodwill penalties
            </p>
          </div>

          <div className="space-y-3">
            {decisionData.optimization_result.map((result: any) => {
              const isFullPayment = result.math_decision === "FULL";
              const isFractional = result.math_decision === "FRACTIONAL_PAYMENT";
              const isDelay = result.math_decision === "DELAY";

              return (
                <div
                  key={result.obligation_id}
                  className={`border rounded-xl p-4 ${
                    isFullPayment
                      ? "border-emerald-200 bg-emerald-50"
                      : isFractional
                      ? "border-amber-200 bg-amber-50"
                      : "border-red-200 bg-red-50"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-gray-800">{result.entity_name}</p>
                      <p className="text-xs text-gray-500 mt-0.5">Due: {result.original_due}</p>
                    </div>
                    <span
                      className={`text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-wide ${
                        isFullPayment
                          ? "bg-emerald-100 text-emerald-700"
                          : isFractional
                          ? "bg-amber-100 text-amber-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {result.math_decision.replace("_", " ")}
                    </span>
                  </div>

                  <div className="mt-3 grid grid-cols-3 gap-3">
                    <div>
                      <p className="text-[10px] text-gray-400 uppercase tracking-wide">Pay Now</p>
                      <p className="text-sm font-bold text-gray-800">
                        ${result.pay_now_amount.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-400 uppercase tracking-wide">Delay</p>
                      <p className="text-sm font-bold text-gray-800">
                        ${result.delay_amount.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] text-gray-400 uppercase tracking-wide">Extension</p>
                      <p className="text-sm font-bold text-gray-800">
                        {result.requested_extension_days} days
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
