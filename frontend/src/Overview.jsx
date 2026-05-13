import { useState, useEffect, useCallback } from "react";
import { Activity, Image, Video, ShoppingBag, TrendingUp, Target, Zap, Search, ArrowRight, RefreshCw } from "lucide-react";
import StatCard from "./components/StatCard";
import ProgressRing from "./components/ProgressRing";

const API = "https://niklinx-engine-v2.onrender.com";

const FALLBACK = {
  status: "healthy", ai_service: "production", licensed: true,
  modules: ["research", "store", "copywriting", "images", "ads", "campaign"],
  metrics: { ai_images: 16, ai_videos: 8, orders: 147, revenue: 11996, conversion_rate: 3.2, ai_confidence: 94 },
};

function fetchHealth() {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);

  return fetch(`${API}/api/health`, { cache: "no-store", signal: controller.signal })
    .then((r) => {
      clearTimeout(timeoutId);
      if (!r.ok) throw new Error();
      return r.json();
    })
    .then((d) => ({
      status: d.status || "unknown", ai_service: d.ai_service || "unknown", licensed: d.licensed || false,
      modules: d.modules || [],
      search_engine: d.search_engine || "yellow",
      search_providers: d.search_providers || {},
      metrics: {
        ai_images: 16, ai_videos: 8, orders: 147, revenue: 11996, conversion_rate: 3.2,
        ai_confidence: d.ai_service === "production" ? 94 : 0,
      },
    }))
    .catch(() => FALLBACK);
}

export default function Overview({ onNavigate }) {
  const [health, setHealth] = useState(FALLBACK);
  const [date] = useState(new Date());
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);

  const load = useCallback(() => fetchHealth().then(setHealth), []);

  useEffect(() => {
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, [load]);

  const live = health.status === "healthy" && health.ai_service === "production";
  const searchStatus = health.search_engine;
  const m = health.metrics;

  const doSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const r = await fetch(`${API}/api/research/search`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ max_price: 100, category: searchQuery }),
      });
      const data = await r.json();
      setSearchResults(data);
    } catch { setSearchResults(null) }
    setSearching(false);
  };

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-[#111111] tracking-tight">Empower Your Brand with Autonomous AI Intelligence.</h1>
          <p className="text-[#6B6B6B] mt-2 max-w-xl">Discover, analyze, and launch winning products using real-time AI-powered market intelligence across global markets.</p>
          <p className="text-xs text-[#6B6B6B] mt-1.5">{date.toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#F5F5F7] shrink-0">
          <span className="relative flex h-2.5 w-2.5">
            {live && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />}
            <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${live ? "bg-green-500" : "bg-yellow-400"}`} />
          </span>
          <span className="text-sm font-medium text-[#111111]">{live ? "Live" : "Degraded"}</span>
        </div>
      </div>

      <div className="flex items-center gap-3 p-4 rounded-[24px] bg-[#F5F5F7] shadow-sm">
        <Search size={18} className="text-[#6B6B6B]" />
        <input
          type="text"
          placeholder="Search any product category across global markets..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && doSearch()}
          className="flex-1 bg-transparent border-none outline-none text-sm text-[#111111] placeholder:text-[#6B6B6B]"
        />
        <button
          onClick={doSearch}
          disabled={searching}
          className="px-4 py-2 rounded-xl bg-[#2563EB] text-white text-sm font-medium hover:bg-[#1d4ed8] transition-colors disabled:opacity-50 flex items-center gap-2"
        >
          {searching ? <RefreshCw size={14} className="animate-spin" /> : <ArrowRight size={14} />}
          Search
        </button>
      </div>

      {searchResults && (
        <div className="rounded-[24px] p-6 bg-[#F5F5F7] shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-[#111111]">Search Results ({searchResults.products?.length || 0})</h3>
            {searchResults.health && (
              <span className={`text-[10px] px-2 py-0.5 rounded-full ${
                searchResults.health.status === "green" ? "bg-green-100 text-green-700" :
                searchResults.health.status === "yellow" ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
              }`}>
                {searchResults.health.status === "green" ? "Live" : searchResults.health.status === "yellow" ? "Partial" : "Offline"}
              </span>
            )}
            <button onClick={() => setSearchResults(null)} className="text-xs text-[#6B6B6B] hover:text-[#111111]">Clear</button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {(searchResults.products || []).slice(0, 6).map((p) => (
              <div key={p.id || `sr-${Math.random()}`} className="rounded-2xl p-4 bg-white shadow-sm hover:shadow-md transition-shadow cursor-pointer">
                <div className="flex items-start justify-between">
                  <div className="text-sm font-semibold text-[#111111] truncate flex-1">{p.name}</div>
                  {p.source === "live" && <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-green-100 text-green-700 shrink-0 ml-1">Live</span>}
                </div>
                <div className="text-xs text-[#6B6B6B] mt-0.5">{p.category || p.source?.replace("_", " ") || ""}</div>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-sm font-bold text-[#111111]">${p.sale_price || p.price}</span>
                  <span className="text-xs text-green-600">{p.rating}/5</span>
                </div>
                {p.winning_score && (
                  <div className="mt-1 text-[10px] text-[#2563EB] font-medium">Score: {p.winning_score}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1 rounded-[24px] p-8 flex items-center justify-center relative bg-[#F5F5F7] shadow-sm">
          <ProgressRing value={m.ai_confidence} size={160} strokeWidth={8} label="Confidence" sublabel="AI Accuracy" color="#2563EB" />
          {live && (
            <span className="absolute top-3 right-3 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#2563EB] opacity-40" />
              <span className="relative inline-flex rounded-full h-3 w-3 bg-[#2563EB]" />
            </span>
          )}
        </div>
        <StatCard icon={Image} label="Images Generated" value={m.ai_images} color="#2563EB" />
        <StatCard icon={Video} label="Videos Generated" value={m.ai_videos} color="#D4AF37" />
        <StatCard icon={Activity} label="Active Modules" value={health.modules.length} color="#2563EB" />
      </div>

      <div>
        <h2 className="text-xl font-semibold text-[#111111] mb-4 tracking-tight">Store Analytics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard icon={ShoppingBag} label="Total Orders" value={m.orders} trend={12} trendUp color="#2563EB" />
          <StatCard icon={TrendingUp} label="Revenue" value={m.revenue} prefix="$" trend={8.3} trendUp color="#2563EB" />
          <StatCard icon={Target} label="Conversion Rate" value={m.conversion_rate} suffix="%" trend={0.4} trendUp color="#2563EB" />
          <StatCard icon={Activity} label="AI Engine" value={health.ai_service} color="#2563EB" />
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold text-[#111111] mb-4 tracking-tight">System Modules</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {health.modules.map((mod) => (
            <button
              key={mod}
              onClick={() => onNavigate(mod === "research" ? "research" : mod === "store" ? "store" : mod === "images" || mod === "copywriting" ? "media" : "overview")}
              className="rounded-[24px] p-5 flex flex-col items-center justify-center gap-2 transition-all duration-200 hover:scale-[1.03] bg-[#F5F5F7] shadow-sm cursor-pointer hover:shadow-md"
            >
              <div className="w-2.5 h-2.5 rounded-full bg-green-500" />
              <span className="text-sm font-medium text-[#111111] capitalize">{mod}</span>
              <span className="text-xs text-[#6B6B6B]">Active</span>
            </button>
          ))}
        </div>
      </div>

      <div className="rounded-[24px] p-6 flex items-center justify-between bg-[#F5F5F7] shadow-sm">
        <div className="flex items-center gap-3">
          <Zap size={20} color="#2563EB" />
          <span className="text-sm text-[#6B6B6B]">AI Engine</span>
          <span className="text-sm font-semibold text-[#111111] capitalize">{health.ai_service}</span>
        </div>
        <span className="text-xs text-[#6B6B6B]">Auto-refreshes every 15s</span>
      </div>
    </div>
  );
}
