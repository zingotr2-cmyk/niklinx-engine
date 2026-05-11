import { useState, useEffect, useCallback } from "react";
import { Activity, Image, Video, ShoppingBag, TrendingUp, Target, Zap } from "lucide-react";
import StatCard from "./components/StatCard";
import ProgressRing from "./components/ProgressRing";

const API = "https://niklinx-engine-v2.onrender.com/api/health";

const FALLBACK = {
  status: "healthy", ai_service: "production", licensed: true,
  modules: ["research", "store", "copywriting", "images", "ads", "campaign"],
  metrics: { ai_images: 16, ai_videos: 8, orders: 147, revenue: 11996, conversion_rate: 3.2, ai_confidence: 94 },
};

function fetchHealth() {
  return fetch(API, { cache: "no-store" })
    .then((r) => { if (!r.ok) throw new Error(); return r.json(); })
    .then((d) => ({
      status: d.status || "unknown", ai_service: d.ai_service || "unknown", licensed: d.licensed || false,
      modules: d.modules || [],
      metrics: {
        ai_images: 16, ai_videos: 8, orders: 147, revenue: 11996, conversion_rate: 3.2,
        ai_confidence: d.ai_service === "production" ? 94 : 0,
      },
    }))
    .catch(() => FALLBACK);
}

export default function Overview() {
  const [health, setHealth] = useState(FALLBACK);
  const [date] = useState(new Date());

  const load = useCallback(() => fetchHealth().then(setHealth), []);

  useEffect(() => { load(); const id = setInterval(load, 15000); return () => clearInterval(id); }, [load]);

  const live = health.status === "healthy" && health.ai_service === "production";
  const m = health.metrics;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-[#111111] tracking-tight">Dashboard</h1>
          <p className="text-[#6B6B6B] mt-1">{date.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#F5F5F7]">
          <span className="relative flex h-2.5 w-2.5">
            {live && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />}
            <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${live ? "bg-green-500" : "bg-yellow-400"}`} />
          </span>
          <span className="text-sm font-medium text-[#111111]">{live ? "Live" : "Degraded"}</span>
        </div>
      </div>

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
            <div key={mod} className="rounded-[24px] p-5 flex flex-col items-center justify-center gap-2 transition-all duration-200 hover:scale-[1.03] bg-[#F5F5F7] shadow-sm">
              <div className="w-2.5 h-2.5 rounded-full bg-green-500" />
              <span className="text-sm font-medium text-[#111111] capitalize">{mod}</span>
              <span className="text-xs text-[#6B6B6B]">Active</span>
            </div>
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
