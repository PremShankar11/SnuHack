"use client";
import { useState } from "react";
import { mockState } from "../mockState";
import { Upload, CheckCircle2, Link2, AlertCircle, Wifi } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const { ingestion } = mockState;

export default function IngestionPage() {
  const [dragging, setDragging] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [scanned, setScanned] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    setScanning(true);
    setTimeout(() => { setScanning(false); setScanned(true); }, 2800);
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Data Ingestion</h1>
        <p className="text-sm text-gray-400 mt-1">Sensors · OCR · Bank sync · Reconciliation</p>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`relative bg-white rounded-2xl border-2 border-dashed transition-all mb-6 p-10 flex flex-col items-center justify-center gap-3 cursor-pointer
          ${dragging ? "border-indigo-400 bg-indigo-50" : "border-gray-200 hover:border-indigo-300 hover:bg-gray-50"}`}
      >
        <AnimatePresence mode="wait">
          {scanning ? (
            <motion.div
              key="scanning"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-3"
            >
              <motion.div
                animate={{ scale: [1, 1.15, 1], opacity: [0.6, 1, 0.6] }}
                transition={{ repeat: Infinity, duration: 1.4 }}
                className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center"
              >
                <Upload size={20} className="text-indigo-600" />
              </motion.div>
              <p className="text-sm font-semibold text-indigo-700">Gemini Vision OCR Processing…</p>
              <p className="text-xs text-indigo-400">Extracting line items, amounts, and vendor metadata</p>
              <motion.div className="w-48 h-1 bg-indigo-100 rounded-full overflow-hidden mt-1">
                <motion.div
                  className="h-full bg-indigo-500 rounded-full"
                  animate={{ x: ["-100%", "100%"] }}
                  transition={{ repeat: Infinity, duration: 1.2, ease: "easeInOut" }}
                />
              </motion.div>
            </motion.div>
          ) : scanned ? (
            <motion.div key="done" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col items-center gap-2">
              <CheckCircle2 size={28} className="text-emerald-500" />
              <p className="text-sm font-semibold text-emerald-700">Receipt scanned &amp; queued for reconciliation</p>
            </motion.div>
          ) : (
            <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center gap-2">
              <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center">
                <Upload size={20} className="text-gray-400" />
              </div>
              <p className="text-sm font-semibold text-gray-700">Drag &amp; drop receipts or PDFs here</p>
              <p className="text-xs text-gray-400">Supports JPG, PNG, PDF · Powered by Gemini Vision OCR</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Live connections */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {[
          { name: "Plaid API", sub: "Bank Sync · Last synced 2 min ago", status: "live" },
          { name: "Stripe API", sub: "Receivables · 3 new events", status: "live" },
        ].map(({ name, sub, status }) => (
          <div key={name} className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4 flex items-center gap-4">
            <div className="w-9 h-9 rounded-xl bg-emerald-50 flex items-center justify-center">
              <Wifi size={16} className="text-emerald-500" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-gray-800">{name}</p>
              <p className="text-xs text-gray-400">{sub}</p>
            </div>
            <span className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              {status === "live" ? "Live" : "Error"}
            </span>
          </div>
        ))}
      </div>

      {/* Reconciliation ledger */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-gray-800">Reconciliation Ledger</p>
            <p className="text-xs text-gray-400 mt-0.5">N-Way fuzzy match · AI confidence scoring</p>
          </div>
          <span className="text-[10px] bg-indigo-50 text-indigo-600 font-semibold px-2.5 py-1 rounded-full border border-indigo-100 uppercase tracking-wide">
            {ingestion.recentItems.filter((r) => r.matched).length} matched
          </span>
        </div>
        <div className="divide-y divide-gray-50">
          {ingestion.recentItems.map((item) => (
            <div key={item.id} className="px-6 py-4 flex items-center gap-4">
              {/* Source badge */}
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-gray-100 text-gray-500 shrink-0 w-16 text-center">
                {item.source}
              </span>

              {/* Description + amount */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 truncate">{item.description}</p>
                <p className="text-xs text-gray-400">{item.date}</p>
              </div>
              <p className={`text-sm font-bold shrink-0 ${item.amount < 0 ? "text-red-500" : "text-emerald-600"}`}>
                {item.amount < 0 ? "-" : "+"}${Math.abs(item.amount).toLocaleString("en-US", { minimumFractionDigits: 2 })}
              </p>

              {/* Match indicator */}
              {item.matched ? (
                <div className="flex items-center gap-2 shrink-0">
                  <Link2 size={13} className="text-indigo-400" />
                  <div>
                    <p className="text-[10px] text-gray-500 truncate max-w-[140px]">{item.matchedWith}</p>
                    <div className="flex items-center gap-1 mt-0.5">
                      <div className="h-1 w-20 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-emerald-400 rounded-full"
                          style={{ width: `${item.confidence}%` }}
                        />
                      </div>
                      <span className="text-[10px] font-bold text-emerald-600">{item.confidence}%</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-1.5 shrink-0 text-amber-500">
                  <AlertCircle size={13} />
                  <span className="text-[11px] font-medium">Unmatched</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
