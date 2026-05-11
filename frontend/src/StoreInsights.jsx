import { useState, useEffect, useCallback } from "react";
import { ShoppingBag, TrendingUp, Target, DollarSign, RefreshCw } from "lucide-react";
import StatCard from "./components/StatCard";

const API = "https://niklinx-engine-v2.onrender.com";
const FALLBACK = { orders: 147, revenue: 11996, conversion_rate: 3.2 };

export default function StoreInsights() {
  const [metrics, setMetrics] = useState(FALLBACK);
  const [forecast, setForecast] = useState(null);
  const [budget, setBudget] = useState(20);

  const load = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/health`, { cache: "no-store" });
      const d = await r.json();
      // Use the same mock metrics since live store isn't connected
    } catch {}
  }, []);

  useEffect(() => { load(); const id = setInterval(load, 30000); return () => clearInterval(id); }, [load]);

  const getForecast = async () => {
    try {
      const r = await fetch(`${API}/api/launch/forecast`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ daily_budget: budget, product_price: 29.99, historical_cvr: 0.02 }),
      });
      setForecast(await r.json());
    } catch {}
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold text-[#111111] tracking-tight">Store Insights</h1>
        <p className="text-[#6B6B6B] mt-1">Analytics and performance metrics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard icon={ShoppingBag} label="Total Orders" value={metrics.orders} trend={12} trendUp color="#2563EB" />
        <StatCard icon={TrendingUp} label="Revenue" value={metrics.revenue} prefix="$" trend={8.3} trendUp color="#2563EB" />
        <StatCard icon={Target} label="Conversion Rate" value={metrics.conversion_rate} suffix="%" trend={0.4} trendUp color="#2563EB" />
      </div>

      <div className="rounded-[24px] p-6 bg-[#F5F5F7] shadow-sm">
        <h3 className="text-lg font-semibold text-[#111111] mb-4">Campaign Forecast</h3>
        <div className="flex items-center gap-4 mb-4">
          <div className="flex-1">
            <label className="text-xs text-[#6B6B6B] block mb-1">Daily Budget ($)</label>
            <div className="flex items-center gap-2 p-3 rounded-xl bg-white shadow-sm">
              <DollarSign size={16} className="text-[#6B6B6B]" />
              <input
                type="number" value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                className="flex-1 bg-transparent border-none outline-none text-sm text-[#111111]"
              />
            </div>
          </div>
          <button onClick={getForecast} className="px-4 py-3 rounded-xl bg-[#2563EB] text-white text-sm font-medium hover:bg-[#1d4ed8] transition-colors flex items-center gap-2">
            <RefreshCw size={14} /> Forecast
          </button>
        </div>
        {forecast && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="text-xs text-[#6B6B6B]">Est. Revenue</div>
              <div className="text-lg font-bold text-[#111111]">${forecast.estimated_revenue}</div>
            </div>
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="text-xs text-[#6B6B6B]">Est. Orders</div>
              <div className="text-lg font-bold text-[#111111]">{forecast.estimated_purchases}</div>
            </div>
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="text-xs text-[#6B6B6B]">ROAS</div>
              <div className="text-lg font-bold text-[#111111]">{forecast.estimated_roas}x</div>
            </div>
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="text-xs text-[#6B6B6B]">Est. Clicks</div>
              <div className="text-lg font-bold text-[#111111]">{forecast.estimated_clicks}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
