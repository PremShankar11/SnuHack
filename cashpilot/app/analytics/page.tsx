"use client";
import { mockState } from "../mockState";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  ReferenceLine, CartesianGrid, Legend,
} from "recharts";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from "recharts";

const { cashFlow, monteCarlo, vendors } = mockState;

const radarData = vendors.map((v) => ({ vendor: v.name, score: v.goodwill }));

export default function AnalyticsPage() {
  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-sm text-gray-400 mt-1">Math engine · LP Solver · Monte Carlo</p>
      </div>

      {/* Main dual-line chart */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 mb-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <p className="text-sm font-semibold text-gray-800">30-Day Cash Projection</p>
            <p className="text-xs text-gray-400 mt-0.5">Standard vs. Phantom (Liquidity Breach visible)</p>
          </div>
          <span className="text-[10px] bg-red-50 border border-red-200 text-red-600 font-semibold px-2.5 py-1 rounded-full uppercase tracking-wide">
            Liquidity Breach Detected
          </span>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={cashFlow} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="day" tick={{ fill: "#94a3b8", fontSize: 10 }} tickLine={false} axisLine={false} interval={4} />
            <YAxis
              tick={{ fill: "#94a3b8", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
              width={40}
            />
            <Tooltip
              contentStyle={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: 10, fontSize: 11 }}
              formatter={(v, name) => [`$${Number(v).toLocaleString()}`, name === "standard" ? "Standard Balance" : "Phantom Usable"]}
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

      {/* Monte Carlo + Goodwill Radar */}
      <div className="grid grid-cols-2 gap-6">
        {/* Monte Carlo */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <p className="text-sm font-semibold text-gray-800 mb-1">Monte Carlo Engine</p>
          <p className="text-xs text-gray-400 mb-5">{monteCarlo.simulations.toLocaleString()} simulations of invoice payment latency</p>

          {/* Big probability ring */}
          <div className="flex items-center gap-6 mb-6">
            <div className="relative w-24 h-24 shrink-0">
              <svg viewBox="0 0 36 36" className="w-24 h-24 -rotate-90">
                <circle cx="18" cy="18" r="15.9" fill="none" stroke="#f1f5f9" strokeWidth="3" />
                <circle
                  cx="18" cy="18" r="15.9" fill="none"
                  stroke={monteCarlo.probability >= 70 ? "#10b981" : monteCarlo.probability >= 40 ? "#f59e0b" : "#ef4444"}
                  strokeWidth="3"
                  strokeDasharray={`${monteCarlo.probability} ${100 - monteCarlo.probability}`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-xl font-black text-gray-800">{monteCarlo.probability}%</span>
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <p className="text-xs font-semibold text-gray-700">Probability of Survival</p>
              <p className="text-[11px] text-gray-400">Based on invoice latency variance across {monteCarlo.simulations.toLocaleString()} runs</p>
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
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
          <p className="text-sm font-semibold text-gray-800 mb-1">Vendor Goodwill Radar</p>
          <p className="text-xs text-gray-400 mb-4">Ontology health scores by vendor</p>
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
    </div>
  );
}
