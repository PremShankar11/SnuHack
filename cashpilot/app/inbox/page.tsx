"use client";
import { useState, useEffect } from "react";
import { useSimulation } from "../context/SimulationContext";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight, X, CheckCircle2, XCircle, Zap, Mail } from "lucide-react";
import { API_URL } from "../lib/api";

export type Action = {
  id: string;
  title: string;
  subtitle: string;
  priority: "critical" | "high" | "medium";
  emailDraft: string;
  steps: { label: string; detail: string }[];
};

const priorityStyles: Record<string, { badge: string; dot: string }> = {
  critical: { badge: "bg-red-50 text-red-600 border-red-200", dot: "bg-red-500" },
  high:     { badge: "bg-amber-50 text-amber-600 border-amber-200", dot: "bg-amber-500" },
  medium:   { badge: "bg-blue-50 text-blue-600 border-blue-200", dot: "bg-blue-400" },
};

export default function InboxPage() {
  const { simulatedDate, refreshKey } = useSimulation();
  const [actions, setActions] = useState<Action[]>([]);
  const [selected, setSelected] = useState<Action | null>(null);

  useEffect(() => {
    async function fetchInbox() {
      try {
        const res = await fetch(`${API_URL}/api/inbox`);
        if (res.ok) {
          const json = await res.json();
          const mapped = json.inbox.map((log: any) => ({
            id: log.id,
            title: log.actionType,
            subtitle: log.summary,
            priority: log.priority,
            emailDraft: "Drafting via Gemini...", 
            steps: log.chainOfThought ? [
              { label: "Reasoning", detail: log.chainOfThought.reason },
              { label: "Projected Horizon", detail: log.chainOfThought.horizon }
            ] : []
          }));
          setActions(mapped);
        }
      } catch (err) {
        console.error("Failed to fetch inbox:", err);
      }
    }
    fetchInbox();
  }, [refreshKey]);

  const dismiss = async (id: string) => {
    setActions((prev) => prev.filter((a) => a.id !== id));
    setSelected(null);
    // Real app would POST to resolve the action in DB here
  };

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Action Inbox</h1>
        <p className="text-sm text-gray-400 mt-1">AI-generated interventions awaiting your approval</p>
      </div>

      {/* Inbox list */}
      <div className="flex flex-col gap-3">
        {actions.length === 0 && (
          <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center">
            <CheckCircle2 size={28} className="text-emerald-400 mx-auto mb-3" />
            <p className="text-sm font-semibold text-gray-600">All clear — no pending actions</p>
          </div>
        )}
        {actions.map((action, i) => {
          const style = priorityStyles[action.priority];
          return (
            <motion.button
              key={action.id}
              layout
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => setSelected(action)}
              className="bg-white rounded-2xl border border-gray-200 shadow-sm px-5 py-4 flex items-center gap-4 text-left hover:border-indigo-200 hover:shadow-md transition-all w-full"
            >
              <span className={`w-2 h-2 rounded-full shrink-0 ${style.dot}`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-800">{action.title}</p>
                <p className="text-xs text-gray-400 mt-0.5">{action.subtitle}</p>
              </div>
              <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full border uppercase tracking-wide shrink-0 ${style.badge}`}>
                {action.priority}
              </span>
              <ChevronRight size={15} className="text-gray-300 shrink-0" />
            </motion.button>
          );
        })}
      </div>

      {/* Full-page modal overlay */}
      <AnimatePresence>
        {selected && (
          <motion.div
            key="overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 flex items-center justify-center p-6"
            onClick={(e) => { if (e.target === e.currentTarget) setSelected(null); }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.96, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.96, y: 20 }}
              transition={{ type: "spring", stiffness: 300, damping: 28 }}
              className="bg-white rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden"
            >
              {/* Modal header */}
              <div className="flex items-start justify-between px-8 py-6 border-b border-gray-100">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Zap size={14} className="text-indigo-500" />
                    <span className="text-[10px] font-bold text-indigo-500 uppercase tracking-widest">AI Intervention</span>
                  </div>
                  <h2 className="text-xl font-bold text-gray-900">{selected.title}</h2>
                  <p className="text-sm text-gray-400 mt-0.5">{selected.subtitle}</p>
                </div>
                <button onClick={() => setSelected(null)} className="p-2 rounded-xl hover:bg-gray-100 transition-colors">
                  <X size={18} className="text-gray-400" />
                </button>
              </div>

              {/* Modal body — two columns */}
              <div className="flex-1 overflow-y-auto">
                <div className="grid grid-cols-2 divide-x divide-gray-100 min-h-full">
                  {/* Left: AI draft */}
                  <div className="p-8">
                    <div className="flex items-center gap-2 mb-4">
                      <Mail size={14} className="text-gray-400" />
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest">AI Drafted Email</p>
                    </div>
                    <div className="bg-gray-50 rounded-2xl p-5 text-xs text-gray-600 leading-relaxed whitespace-pre-wrap font-mono border border-gray-100">
                      {selected.emailDraft}
                    </div>
                  </div>

                  {/* Right: Chain-of-thought stepper */}
                  <div className="p-8">
                    <div className="flex items-center gap-2 mb-6">
                      <Zap size={14} className="text-indigo-400" />
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest">Chain-of-Thought Audit Trail</p>
                    </div>
                    <div className="flex flex-col gap-0">
                      {selected.steps.map((step, idx) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, x: 10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.1 }}
                          className="flex gap-4"
                        >
                          {/* Stepper line */}
                          <div className="flex flex-col items-center">
                            <div className="w-7 h-7 rounded-full bg-indigo-50 border-2 border-indigo-200 flex items-center justify-center text-indigo-600 text-xs font-bold shrink-0">
                              {idx + 1}
                            </div>
                            {idx < selected.steps.length - 1 && (
                              <div className="w-px flex-1 bg-indigo-100 my-1" />
                            )}
                          </div>
                          {/* Step content */}
                          <div className={`pb-6 ${idx === selected.steps.length - 1 ? "pb-0" : ""}`}>
                            <p className="text-sm font-semibold text-gray-800 mb-0.5">{step.label}</p>
                            <p className="text-xs text-gray-500 leading-relaxed">{step.detail}</p>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Sticky footer */}
              <div className="px-8 py-5 border-t border-gray-100 bg-white flex gap-4">
                <button
                  onClick={() => dismiss(selected.id)}
                  className="flex-1 py-3.5 rounded-2xl bg-emerald-500 hover:bg-emerald-600 text-white font-bold text-sm flex items-center justify-center gap-2 transition-colors shadow-sm"
                >
                  <CheckCircle2 size={17} />
                  Approve &amp; Execute
                </button>
                <button
                  onClick={() => dismiss(selected.id)}
                  className="flex-1 py-3.5 rounded-2xl bg-red-50 hover:bg-red-100 text-red-600 font-bold text-sm flex items-center justify-center gap-2 transition-colors border border-red-200"
                >
                  <XCircle size={17} />
                  Reject
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
