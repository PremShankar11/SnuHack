"use client";
import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";

type SimulationContextType = {
  daysOffset: number;
  simulatedDate: string;
  refreshKey: number;
  isSimulating: boolean;
  triggerSimulation: (offset: number) => Promise<void>;
};

const SimulationContext = createContext<SimulationContextType | undefined>(undefined);

import { API_URL } from "../lib/api";

export function SimulationProvider({ children }: { children: ReactNode }) {
  const [daysOffset, setDaysOffset] = useState(0);
  const [simulatedDate, setSimulatedDate] = useState<string>(() => {
    return new Date().toISOString().split('T')[0];
  });
  const [refreshKey, setRefreshKey] = useState(0);
  const [isSimulating, setIsSimulating] = useState(false);

  const triggerSimulation = useCallback(async (offset: number) => {
    if (offset === daysOffset) return;
    setIsSimulating(true);

    try {
      const res = await fetch(`${API_URL}/api/simulate/advance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ days_offset: offset }),
      });
      if (res.ok) {
        const data = await res.json();
        setDaysOffset(offset);
        setSimulatedDate(data.simulated_as_of.split('T')[0]);
        // Bump refresh key so all consumers re-fetch
        setRefreshKey((k) => k + 1);
        console.log("Simulation advanced to:", data.simulated_as_of);
      } else {
        console.error("Failed to advance simulation");
      }
    } catch (e) {
      console.error("Error advancing simulation:", e);
    } finally {
      setIsSimulating(false);
    }
  }, [daysOffset]);

  return (
    <SimulationContext.Provider value={{ daysOffset, simulatedDate, refreshKey, isSimulating, triggerSimulation }}>
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
