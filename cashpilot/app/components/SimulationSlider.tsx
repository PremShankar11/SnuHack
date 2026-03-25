"use client";
import { useState, useEffect } from "react";
import { useSimulation } from "../context/SimulationContext";
import { Clock } from "lucide-react";

export default function SimulationSlider() {
  const { daysOffset, simulatedDate, triggerSimulation } = useSimulation();
  const [localOffset, setLocalOffset] = useState(daysOffset);

  // Sync local if global changes
  useEffect(() => {
    setLocalOffset(daysOffset);
  }, [daysOffset]);

  // Debounced API call when user stops sliding
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localOffset > daysOffset) {
        triggerSimulation(localOffset);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [localOffset, daysOffset, triggerSimulation]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value, 10);
    // Enforce forward-only logic
    if (val >= daysOffset) {
      setLocalOffset(val);
    }
  };

  return (
    <div className="bg-white border-t border-gray-100 p-4 shrink-0 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-indigo-700">
          <Clock size={14} className="animate-pulse" />
          <span className="text-xs font-bold uppercase tracking-wide">Living Timeline</span>
        </div>
        <span className="text-[10px] bg-indigo-50 text-indigo-700 font-bold px-2 py-0.5 rounded border border-indigo-100">
          +{localOffset} Days
        </span>
      </div>
      
      <p className="text-[10px] text-gray-500 font-medium">
        Simulated As Of: <strong className="text-gray-800">{simulatedDate}</strong>
      </p>

      <input
        type="range"
        min="0"
        max="30"
        value={localOffset}
        onChange={handleChange}
        className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600 mt-2"
        style={{ backgroundSize: `${(localOffset / 30) * 100}% 100%` }}
      />
      <div className="flex justify-between text-[9px] text-gray-400 font-bold mt-1">
        <span>Today</span>
        <span>+15</span>
        <span>+30</span>
      </div>
    </div>
  );
}
