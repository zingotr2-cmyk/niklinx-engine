import { useState, useEffect, useCallback } from "react";
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
  green: { label: "All Systems Go", ping: true, dot: "bg-green-500", pingColor: "bg-green-400" },
  yellow: { label: "Partial Connectivity", ping: false, dot: "bg-yellow-400", pingColor: "" },
  red: { label: "Reconnecting...", ping: false, dot: "bg-red-400", pingColor: "" },
};

export default function Sidebar({ activeView, onNavigate }) {
  const [status, setStatus] = useState("yellow");
  const [searchProviders, setSearchProviders] = useState({});

  const poll = useCallback(() => {
    fetch(API, { cache: "no-store" })
      .then((r) => r.json())
      .then((d) => {
        if (d.status === "healthy") {
          const se = d.search_engine || "yellow";
          setStatus(se);
          setSearchProviders(d.search_providers || {});
        } else {
          setStatus("yellow");
        }
      })
      .catch(() => setStatus("red"));
  }, []);

  useEffect(() => {
    poll();
    const id = setInterval(poll, 15000);
    return () => clearInterval(id);
  }, [poll]);

  const s = STATUS_MAP[status] || STATUS_MAP.yellow;
  const providerNames = Object.keys(searchProviders);

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
          Sign Out
        </button>
      </div>

      <div className="px-6 pb-6 space-y-2">
        <div className="rounded-2xl p-4 bg-[#F5F5F7]">
          <div className="text-xs font-medium text-[#6B6B6B] mb-1">System Status</div>
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              {s.ping && <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${s.pingColor} opacity-75`} />}
              <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${s.dot}`} />
            </span>
            <span className="text-sm font-medium text-[#111111]">{s.label}</span>
          </div>
          {providerNames.length > 0 && (
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
          <span className="text-[10px] text-[#6B6B6B]">Global Search: <span className={status === "green" ? "text-green-600" : status === "yellow" ? "text-yellow-600" : "text-red-500"}>{status === "green" ? "Active" : status === "yellow" ? "Partial" : "Offline"}</span></span>
        </div>
      </div>
    </aside>
  );
}
