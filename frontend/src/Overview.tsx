import { useState, useEffect, useCallback } from "react";
import {
  Activity, Image, Video, ShoppingBag, TrendingUp,
  Target, Zap, Search, ArrowRight, RefreshCw
} from "lucide-react";
import StatCard from "./components/StatCard";
import ProgressRing from "./components/ProgressRing";
import { useActiveProduct, type AnalyticsData } from "./context/ProductContext";

const API = "https://niklinx-engine-v2.onrender.com";
const FETCH_TIMEOUT = 10000;

interface SystemStatus {
  ai_confidence: number;
  active_modules: string[];
  module_count: number;
  ai_service: string;
  has_openai: boolean;
  has_claude: boolean;
}

interface MediaStats {
  images_generated: number;
  videos_generated: number;
}

interface HealthData {
  status: string;
  ai_service: string;
  licensed: boolean;
  modules: string[];
  search_engine: string;
  search_providers: Record<string, unknown>;
}

function SkeletonCard() {
  return (
    <div className="rounded-[24px] p-5 bg-[#F5F5F7] shadow-sm animate-pulse">
      <div className="h-3 bg-gray-200 rounded w-20 mb-2" />
      <div className="h-6 bg-gray-200 rounded w-16" />
    </div>
  );
}

function SkeletonRing() {
  return (
    <div className="rounded-[24px] p-8 flex items-center justify-center bg-[#F5F5F7] shadow-sm animate-pulse">
      <div className="rounded-full bg-gray-200" style={{ width: 160, height: 160 }} />
    </div>
  );
}

async function fetchJson<T>(url: string, options?: RequestInit, signal?: AbortSignal): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT);
  const combinedSignal = signal
    ? anySignal([signal, controller.signal])
    : controller.signal;

  try {
    const r = await fetch(url, { ...options, signal: combinedSignal });
    clearTimeout(timeoutId);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (err) {
    clearTimeout(timeoutId);
    throw err;
  }
}

function anySignal(signals: AbortSignal[]): AbortSignal {
  const controller = new AbortController();
  for (const s of signals) {
    if (s.aborted) {
      controller.abort(s.reason);
      return controller.signal;
    }
    s.addEventListener("abort", () => controller.abort(s.reason), { once: true });
  }
  return controller.signal;
}

export default function Overview({ onNavigate }: { onNavigate: (view: string) => void }) {
  const { activeProduct } = useActiveProduct();
  const [health, setHealth] = useState<HealthData | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [mediaStats, setMediaStats] = useState<MediaStats | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [date] = useState(new Date());
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Record<string, unknown> | null>(null);
  const [searching, setSearching] = useState(false);

  const load = useCallback(async (signal: AbortSignal) => {
    setLoading(true);
    console.log("[Overview] Fetching dashboard data");

    try {
      const [healthData, statusData, mediaData, analyticsData] = await Promise.all([
        fetchJson<HealthData>(`${API}/api/health`, { cache: "no-store" }, signal),
        fetchJson<{ success: boolean; data: SystemStatus }>(`${API}/api/v1/system/status`, {}, signal),
        fetchJson<{ success: boolean; data: MediaStats }>(`${API}/api/v1/media/stats`, {}, signal),
        (async () => {
          const body = activeProduct?.id ? { product_id: activeProduct.id } : {};
          try {
            const r = await fetchJson<{ success: boolean; data: AnalyticsData }>(
              `${API}/api/v1/analytics`,
              { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) },
              signal
            );
            return r.data;
          } catch {
            return null;
          }
        })(),
      ]);

      if (signal.aborted) return;

      console.log("[Overview] Health:", healthData);
      console.log("[Overview] System Status:", statusData);
      console.log("[Overview] Media Stats:", mediaData);

      setHealth(healthData);
      setSystemStatus(statusData.data);
      setMediaStats(mediaData.data);
      setAnalytics(analyticsData);
      setLoading(false);
    } catch (err) {
      if (signal.aborted) return;
      console.log("[Overview] Load error:", err);
      setHealth(null);
      setSystemStatus(null);
      setMediaStats(null);
      setAnalytics(null);
      setLoading(false);
    }
  }, [activeProduct?.id]);

  useEffect(() => {
    const controller = new AbortController();
    load(controller.signal);
    const id = setInterval(() => load(controller.signal), 15000);
    return () => {
      controller.abort();
      clearInterval(id);
    };
  }, [load]);

  const live = health?.status === "healthy" && health?.ai_service === "production";
  const a = analytics;
  const ss = systemStatus;
  const ms = mediaStats;

  const doSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const r = await fetch(`${API}/api/research/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ max_price: 100, category: searchQuery }),
      });
      const data = await r.json();
      setSearchResults(data);
    } catch {
      setSearchResults(null);
    }
    setSearching(false);
  };

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-[#111111] tracking-tight">
            Empower Your Brand with Autonomous AI Intelligence.
          </h1>
          <p className="text-[#6B6B6B] mt-2 max-w-xl">
            Discover, analyze, and launch winning products using real-time AI-powered market intelligence across global markets.
          </p>
          <p className="text-xs text-[#6B6B6B] mt-1.5">
            {date.toLocaleDateString("en-US", {
              weekday: "long", year: "numeric", month: "long", day: "numeric",
            })}
          </p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#F5F5F7] shrink-0">
          <span className="relative flex h-2.5 w-2.5">
            {live && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
            )}
            <span
              className={`relative inline-flex rounded-full h-2.5 w-2.5 ${live ? "bg-green-500" : "bg-yellow-400"}`}
            />
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
            <h3 className="text-lg font-semibold text-[#111111]">
              Search Results ({(searchResults.products as unknown[] | undefined)?.length ?? 0})
            </h3>
            {(searchResults.health as Record<string, string> | undefined)?.status && (
              <span
                className={`text-[10px] px-2 py-0.5 rounded-full ${
                  (searchResults.health as Record<string, string>).status === "green"
                    ? "bg-green-100 text-green-700"
                    : (searchResults.health as Record<string, string>).status === "yellow"
                      ? "bg-yellow-100 text-yellow-700"
                      : "bg-red-100 text-red-700"
                }`}
              >
                {(searchResults.health as Record<string, string>).status === "green"
                  ? "Live"
                  : (searchResults.health as Record<string, string>).status === "yellow"
                    ? "Partial"
                    : "Offline"}
              </span>
            )}
            <button onClick={() => setSearchResults(null)} className="text-xs text-[#6B6B6B] hover:text-[#111111]">
              Clear
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {((searchResults.products as Record<string, unknown>[]) ?? []).slice(0, 6).map((p, idx) => (
              <div
                key={(p.id as string) ?? `sr-${idx}`}
                className="rounded-2xl p-4 bg-white shadow-sm hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="text-sm font-semibold text-[#111111] truncate flex-1">{p.name as string}</div>
                  {p.source === "live" && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-green-100 text-green-700 shrink-0 ml-1">
                      Live
                    </span>
                  )}
                </div>
                <div className="text-xs text-[#6B6B6B] mt-0.5">
                  {(p.category as string) ?? ((p.source as string)?.replace("_", " ") ?? "")}
                </div>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-sm font-bold text-[#111111]">${p.sale_price ?? p.price}</span>
                  <span className="text-xs text-green-600">{p.rating as string}/5</span>
                </div>
                {p.winning_score && (
                  <div className="mt-1 text-[10px] text-[#2563EB] font-medium">Score: {p.winning_score as string}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {loading ? (
          <>
            <SkeletonRing />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            <div className="lg:col-span-1 rounded-[24px] p-8 flex items-center justify-center relative bg-[#F5F5F7] shadow-sm">
              <ProgressRing
                value={ss?.ai_confidence ?? 0}
                size={160}
                strokeWidth={8}
                label="Confidence"
                sublabel="AI Accuracy"
                color="#2563EB"
              />
              {live && (
                <span className="absolute top-3 right-3 flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#2563EB] opacity-40" />
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-[#2563EB]" />
                </span>
              )}
            </div>
            <StatCard icon={Image} label="Images Generated" value={ms?.images_generated ?? 0} color="#2563EB" />
            <StatCard icon={Video} label="Videos Generated" value={ms?.videos_generated ?? 0} color="#D4AF37" />
            <StatCard icon={Activity} label="Active Modules" value={health?.modules.length ?? 0} color="#2563EB" />
          </>
        )}
      </div>

      <div>
        <h2 className="text-xl font-semibold text-[#111111] mb-4 tracking-tight">
          Store Analytics
          {activeProduct && (
            <span className="text-sm font-normal text-[#6B6B6B] ml-2">
              — projecting for {activeProduct.name}
            </span>
          )}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {loading ? (
            <>
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : (
            <>
              <StatCard
                icon={ShoppingBag}
                label={activeProduct ? "Projected Orders" : "Total Orders"}
                value={a?.total_orders ?? 0}
                trend={a?.weekly_growth_pct ?? 0}
                trendUp={(a?.growth_direction ?? "up") === "up"}
                color="#2563EB"
              />
              <StatCard
                icon={TrendingUp}
                label={activeProduct ? "Projected Revenue" : "Revenue"}
                value={a?.total_revenue ?? 0}
                prefix="$"
                trend={a?.monthly_growth_pct ?? 0}
                trendUp={(a?.growth_direction ?? "up") === "up"}
                color="#2563EB"
              />
              <StatCard
                icon={Target}
                label="Conversion Rate"
                value={a?.conversion_rate ?? 0}
                suffix="%"
                trend={a?.growth_percentage ?? 0}
                trendUp={(a?.growth_direction ?? "up") === "up"}
                color="#2563EB"
              />
              <StatCard
                icon={Activity}
                label="AI Engine"
                value={health?.ai_service ?? "unknown"}
                color="#2563EB"
              />
            </>
          )}
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold text-[#111111] mb-4 tracking-tight">System Modules</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {(health?.modules ?? []).map((mod: string) => (
            <button
              key={mod}
              onClick={() =>
                onNavigate(
                  mod === "research"
                    ? "research"
                    : mod === "store"
                      ? "store"
                      : mod === "images" || mod === "copywriting"
                        ? "media"
                        : "overview"
                )
              }
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
          <span className="text-sm font-semibold text-[#111111] capitalize">{health?.ai_service ?? "unknown"}</span>
        </div>
        <span className="text-xs text-[#6B6B6B]">Auto-refreshes every 15s</span>
      </div>
    </div>
  );
}
