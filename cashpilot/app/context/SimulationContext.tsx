"use client";
import React, { createContext, useContext, useState, ReactNode } from "react";

type SimulationContextType = {
  daysOffset: number;
  simulatedDate: string;
  triggerSimulation: (offset: number) => Promise<void>;
};

const SimulationContext = createContext<SimulationContextType | undefined>(undefined);

export function SimulationProvider({ children }: { children: ReactNode }) {
  const [daysOffset, setDaysOffset] = useState(0);
  const [simulatedDate, setSimulatedDate] = useState<string>(() => {
    return new Date().toISOString().split('T')[0];
  });

  const triggerSimulation = async (offset: number) => {
    if (offset <= daysOffset) return; // Only move forward

    try {
      const res = await fetch("http://localhost:8000/api/simulate/advance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ days_offset: offset }),
      });
      if (res.ok) {
        const data = await res.json();
        setDaysOffset(offset);
        setSimulatedDate(data.simulated_as_of.split('T')[0]);
        // Also could trigger global re-fetch here if we used SWR/React Query
        console.log("Simulation advanced to:", data.simulated_as_of);
      } else {
        console.error("Failed to advance simulation");
      }
    } catch (e) {
      console.error("Error advancing simulation:", e);
    }
  };

  return (
    <SimulationContext.Provider value={{ daysOffset, simulatedDate, triggerSimulation }}>
      {children}
    </SimulationContext.Provider>
  );
}

export function useSimulation() {
  const context = useContext(SimulationContext);
  if (!context) {
    throw new Error("useSimulation must be used within a SimulationProvider");
  }
  return context;
}
