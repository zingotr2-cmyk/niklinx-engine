import { useState, useEffect, useCallback, useRef } from "react";
import { LayoutDashboard, Search, Image, ShoppingCart, BarChart3, Settings, LogOut, Globe } from "lucide-react";

const API = "https://niklinx-engine-v2.onrender.com/api/health";

const NAV = [
  { icon: LayoutDashboard, label: "Overview", view: "overview" },
  { icon: Search, label: "Product Research", view: "research" },
  { icon: Image, label: "Media Studio", view: "media" },
  { icon: ShoppingCart, label: "Store Insights", view: "store" },
  { icon: BarChart3, label: "Analytics", view: "analytics" },
  { icon: Settings, label: "Settings", view: "settings" },
];

const STATUS_MAP = {
  green: { label: "All Systems Operational", ping: true, dot: "bg-green-500", pingColor: "bg-green-400" },
  yellow: { label: "Reconnecting...", ping: true, dot: "bg-yellow-400", pingColor: "bg-yellow-300" },
  red: { label: "Connection Lost", ping: false, dot: "bg-red-400", pingColor: "" },
};

const INITIAL_INTERVAL = 15000;
const MAX_INTERVAL = 30000;
const BACKOFF_BASE = 1000;

export default function Sidebar({ activeView, onNavigate }) {
  const [status, setStatus] = useState("yellow");
  const [searchEngine, setSearchEngine] = useState("yellow");
  const [searchProviders, setSearchProviders] = useState({});
  const [consecutiveFails, setConsecutiveFails] = useState(0);
  const [retryCountdown, setRetryCountdown] = useState(null);
  const intervalRef = useRef(null);
  const timerRef = useRef(null);

  const poll = useCallback(() => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    fetch(API, { cache: "no-store", signal: controller.signal })
      .then((r) => {
        clearTimeout(timeoutId);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((d) => {
        clearTimeout(timeoutId);
        setConsecutiveFails(0);
        setRetryCountdown(null);
        if (d.status === "healthy") {
          setStatus("green");
          setSearchEngine(d.search_engine || "yellow");
          setSearchProviders(d.search_providers || {});
        } else {
          setStatus("yellow");
        }
      })
      .catch(() => {
        setConsecutiveFails((prev) => {
          const next = prev + 1;
          const delay = Math.min(BACKOFF_BASE * Math.pow(2, next), MAX_INTERVAL);
          setRetryCountdown(Math.ceil(delay / 1000));
          return next;
        });
        setStatus("yellow");
      });
  }, []);

  useEffect(() => {
    poll();
    intervalRef.current = setInterval(poll, INITIAL_INTERVAL);
    return () => {
      clearInterval(intervalRef.current);
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [poll]);

  const s = STATUS_MAP[status] || STATUS_MAP.yellow;
  const providerNames = Object.keys(searchProviders);
  const reconnecting = status === "yellow" && consecutiveFails > 0;

  return (
    <aside className="fixed left-0 top-0 h-full w-64 flex flex-col z-50 backdrop-blur-xl bg-white/70 border-r border-white/20 shadow-sm">
      <div className="px-6 pt-8 pb-6">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#2563EB] flex items-center justify-center">
            <span className="text-white font-bold text-sm">N</span>
          </div>
          <span className="text-lg font-semibold text-[#111111] tracking-tight">NikLinx</span>
        </div>
      </div>

      <nav className="flex-1 px-3 space-y-1">
        {NAV.map((item) => (
          <button
            key={item.view}
            onClick={() => onNavigate(item.view)}
            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
              activeView === item.view
                ? "bg-[#2563EB] text-white shadow-sm"
                : "text-[#6B6B6B] hover:text-[#111111] hover:bg-[#F5F5F7]"
            }`}
          >
            <item.icon size={18} strokeWidth={activeView === item.view ? 2.5 : 1.5} />
            {item.label}
          </button>
        ))}
      </nav>

      <div className="px-3 pb-6">
        <button className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium text-[#6B6B6B] hover:text-[#111111] hover:bg-[#F5F5F7] transition-all duration-200">
          <LogOut size={18} strokeWidth={1.5} />
          Sign out
        </button>
      </div>

      <div className="px-6 pb-6 space-y-2">
        <div className="rounded-2xl p-4 bg-[#F5F5F7]">
          <div className="text-xs font-medium text-[#6B6B6B] mb-1">System Status</div>
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              {s.ping && (
                <span
                  className={`animate-ping absolute inline-flex h-full w-full rounded-full ${s.pingColor} opacity-75`}
                  style={{ animationDuration: reconnecting ? "0.8s" : "1.5s" }}
                />
              )}
              <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${s.dot}`} />
            </span>
            <span className="text-sm font-medium text-[#111111]">{s.label}</span>
            {reconnecting && retryCountdown !== null && (
              <span className="text-[10px] text-[#6B6B6B] ml-auto animate-pulse">
                retry in {retryCountdown}s
              </span>
            )}
          </div>
          {reconnecting && (
            <p className="text-[10px] text-yellow-600 mt-1.5 animate-pulse">
              {consecutiveFails <= 2
                ? "Backend waking up..."
                : "Connection interrupted — auto-recovering..."}
            </p>
          )}
          {providerNames.length > 0 && !reconnecting && (
            <div className="mt-2 flex flex-wrap gap-1">
              {providerNames.map((name) => {
                const h = searchProviders[name];
                return (
                  <span key={name} className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                    h?.healthy ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
                  }`}>
                    {name}
                  </span>
                );
              })}
            </div>
          )}
        </div>
        <div className="rounded-2xl p-3 bg-[#F5F5F7] flex items-center gap-2">
          <Globe size={12} className="text-[#6B6B6B]" />
          <span className="text-[10px] text-[#6B6B6B]">
            Global Search:{" "}
            <span className={
              searchEngine === "green" ? "text-green-600" :
              reconnecting ? "text-yellow-500 animate-pulse" :
              searchEngine === "yellow" ? "text-yellow-600" : "text-red-500"
            }>
              {searchEngine === "green" ? "Active" : reconnecting ? "Reconnecting..." : searchEngine === "yellow" ? "Partial" : "Offline"}
            </span>
          </span>
        </div>
      </div>
    </aside>
  );
}
