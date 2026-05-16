import { useState, useEffect, useCallback } from "react";
import {
  ShoppingBag, TrendingUp, Target, DollarSign,
  RefreshCw, Globe, ExternalLink, CheckCircle,
  BarChart3, Users, Star, Activity
} from "lucide-react";
import StatCard from "./components/StatCard";
import { toast } from "./components/Toast";
import { useActiveProduct, type AnalyticsState, type AnalyticsResponse } from "./context/ProductContext";

const API = "https://niklinx-engine-v2.onrender.com";
const FETCH_TIMEOUT = 15000;
const MAX_RETRIES = 2;

interface CloneResult {
  store?: { name?: string };
  brand_name?: string;
  cloned_from_template?: boolean;
  sections?: string[];
  design_specs?: {
    font_family?: string;
    color_palette?: string[];
  };
}

interface ForecastData {
  estimated_revenue?: number;
  estimated_purchases?: number;
  estimated_roas?: number;
  estimated_clicks?: number;
}

function isValidUrl(str: string): boolean {
  try {
    const url = new URL(str);
    return ["http:", "https:"].includes(url.protocol);
  } catch {
    return false;
  }
}

function SkeletonCard() {
  return (
    <div className="rounded-[24px] p-5 bg-[#F5F5F7] shadow-sm animate-pulse">
      <div className="h-3 bg-gray-200 rounded w-20 mb-2" />
      <div className="h-6 bg-gray-200 rounded w-16" />
    </div>
  );
}

const INITIAL_STATE: AnalyticsState = {
  data: null,
  loading: true,
  error: null,
  lastUpdated: null,
  isStale: false,
};

export default function StoreInsights() {
  const { activeProduct, markSynced } = useActiveProduct();
  const [state, setState] = useState<AnalyticsState>(INITIAL_STATE);
  const [refetchTrigger, setRefetchTrigger] = useState(0);
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [budget, setBudget] = useState(20);
  const [cloneUrl, setCloneUrl] = useState("");
  const [cloning, setCloning] = useState(false);
  const [cloneResult, setCloneResult] = useState<CloneResult | null>(null);

  const fetchAnalytics = useCallback(async (product: typeof activeProduct, signal: AbortSignal) => {
    setState({ data: null, loading: true, error: null, lastUpdated: null, isStale: true });

    const body: Record<string, string> = {};
    if (product?.id) {
      body.product_id = product.id;
    }

    console.log("[StoreInsights] Request:", product?.id ?? "no product");

    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT);

        const response = await fetch(`${API}/api/v1/analytics`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
          signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const json: AnalyticsResponse = await response.json();

        if (signal.aborted) return;

        console.log("[StoreInsights] Response:", json);

        setState({
          data: json.data,
          loading: false,
          error: null,
          lastUpdated: Date.now(),
          isStale: false,
        });

        if (product?.id) markSynced("store", product.id);
        return;
      } catch (err: unknown) {
        if (signal.aborted) return;
        if (attempt === MAX_RETRIES) {
          const message = err instanceof Error ? err.message : "Unable to load analytics";
          console.log("[StoreInsights] Error:", message);
          setState({
            data: null,
            loading: false,
            error: "Unable to load analytics. Please try again.",
            lastUpdated: null,
            isStale: false,
          });
        } else {
          await new Promise((r) => setTimeout(r, 1000 * (attempt + 1)));
        }
      }
    }
  }, [markSynced]);

  useEffect(() => {
    const controller = new AbortController();
    fetchAnalytics(activeProduct, controller.signal);
    return () => controller.abort();
  }, [activeProduct, refetchTrigger, fetchAnalytics]);

  useEffect(() => {
    if (activeProduct?.price) {
      setBudget(Math.max(10, Math.round(Number(activeProduct.price) * 0.5)));
      getForecast(Number(activeProduct.price));
    }
  }, [activeProduct?.price, activeProduct?.id]);

  const getForecast = async (productPrice: number) => {
    const pPrice = productPrice ?? 29.99;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT);
    try {
      const r = await fetch(`${API}/api/launch/forecast`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ daily_budget: budget, product_price: pPrice, historical_cvr: 0.02 }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      const data: ForecastData = await r.json();
      setForecast(data);
    } catch {
      clearTimeout(timeoutId);
    }
  };

  const repairConnection = useCallback(() => {
    console.log("[StoreInsights] Repairing connection — resetting all state and refetching");
    setState(INITIAL_STATE);
    setForecast(null);
    setCloneResult(null);
    setCloneUrl("");
    setRefetchTrigger((prev) => prev + 1);
  }, []);

  const doManualClone = async () => {
    const url = cloneUrl.trim();
    if (!url || !isValidUrl(url)) {
      toast("Please enter a valid store URL (https://...)", "error");
      return;
    }
    setCloning(true);
    setCloneResult(null);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT);
    try {
      const r = await fetch(`${API}/api/store/analyze`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      const data: CloneResult = await r.json();
      setCloneResult(data);
      toast("Store cloned successfully", "success");
    } catch {
      clearTimeout(timeoutId);
      toast("Unable to clone store. Retrying with template...", "error");
      try {
        const r = await fetch(`${API}/api/store/analyze`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: "" }),
        });
        const data: CloneResult = await r.json();
        setCloneResult(data);
      } catch {
        toast("Clone failed. Check URL and try again.", "error");
      }
    }
    setCloning(false);
  };

  const data = state.data;
  const activeProductData = data?.active_product ?? null;
  const categories = data?.categories ?? null;
  const topProducts = data?.top_products ?? null;
  const customerInsights = data?.customer_insights ?? null;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-[#111111] tracking-tight">Store Insights</h1>
          <p className="text-[#6B6B6B] mt-1">Real-time store analytics, revenue tracking, and campaign forecasting.</p>
        </div>
        <button
          onClick={repairConnection}
          disabled={state.loading}
          className="px-4 py-2 rounded-xl border border-[#D4D4D4] text-sm text-[#6B6B6B] hover:bg-[#F5F5F7] transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          <RefreshCw size={14} className={state.loading ? "animate-spin" : ""} />
          {state.loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {activeProductData && (
        <div className="rounded-2xl px-5 py-3 bg-gradient-to-r from-[#2563EB]/5 to-white border border-[#2563EB]/10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp size={14} className="text-[#2563EB]" />
            <span className="text-xs text-[#6B6B6B]">
              Projecting for <strong className="text-[#111111]">{activeProductData.name}</strong>
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-[#2563EB]/10 text-[#2563EB] font-medium">
              {activeProductData.category} · {activeProductData.profit_margin}% margin
            </span>
          </div>
          <span className="text-[10px] text-[#6B6B6B]">{activeProductData.competitor_count} competitors</span>
        </div>
      )}

      {state.error && !state.loading && (
        <div className="rounded-[24px] p-6 bg-red-50 border border-red-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Activity size={18} className="text-red-400" />
            <span className="text-sm text-red-700">{state.error}</span>
          </div>
          <button
            onClick={repairConnection}
            className="text-xs px-3 py-1.5 rounded-xl bg-red-100 text-red-700 hover:bg-red-200 transition-colors flex items-center gap-1"
          >
            <RefreshCw size={12} /> Retry
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {state.loading ? (
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
              label={activeProductData ? "Projected Orders" : "Total Orders"}
              value={activeProductData?.projected_orders ?? data?.total_orders ?? 0}
              trend={data?.weekly_growth_pct ?? 0}
              trendUp={(data?.growth_direction ?? "up") === "up"}
              color="#2563EB"
            />
            <StatCard
              icon={TrendingUp}
              label={activeProductData ? "Projected Revenue" : "Revenue"}
              value={activeProductData?.projected_revenue ?? data?.total_revenue ?? 0}
              prefix="$"
              trend={data?.monthly_growth_pct ?? 0}
              trendUp={(data?.growth_direction ?? "up") === "up"}
              color="#2563EB"
            />
            <StatCard
              icon={Target}
              label="Conversion Rate"
              value={data?.conversion_rate ?? 0}
              suffix="%"
              trend={data?.growth_percentage ?? 0}
              trendUp={(data?.growth_direction ?? "up") === "up"}
              color="#2563EB"
            />
            <StatCard
              icon={Users}
              label="Traffic"
              value={data?.total_traffic ?? 0}
              color="#2563EB"
            />
          </>
        )}
      </div>

      {categories && categories.length > 0 && !state.loading && (
        <div className="rounded-[24px] p-6 bg-[#F5F5F7] shadow-sm">
          <h3 className="text-lg font-semibold text-[#111111] mb-4 flex items-center gap-2">
            <BarChart3 size={18} className="text-[#2563EB]" />
            Category Performance
          </h3>
          <div className="space-y-2">
            {categories.slice(0, 6).map((cat) => (
              <div key={cat.name} className="flex items-center gap-3">
                <span className="text-xs text-[#6B6B6B] w-32 truncate">{cat.name}</span>
                <div className="flex-1 h-2 rounded-full bg-white overflow-hidden">
                  <div
                    className="h-full rounded-full bg-[#2563EB] transition-all duration-500"
                    style={{ width: `${Math.min(cat.market_share * 2, 100)}%` }}
                  />
                </div>
                <span className="text-xs font-medium text-[#111111] w-16 text-right">{cat.market_share}%</span>
                <span className="text-[10px] text-[#6B6B6B] w-20 text-right">{cat.product_count} products</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {topProducts && topProducts.length > 0 && !state.loading && (
        <div className="rounded-[24px] p-6 bg-[#F5F5F7] shadow-sm">
          <h3 className="text-lg font-semibold text-[#111111] mb-4 flex items-center gap-2">
            <Star size={18} className="text-[#2563EB]" />
            Top Performing Products
          </h3>
          <div className="space-y-2">
            {topProducts.slice(0, 5).map((p, i) => (
              <div key={p.id || i} className="flex items-center justify-between p-3 rounded-xl bg-white shadow-sm">
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <span className="text-xs font-medium text-[#6B6B6B] w-4">#{i + 1}</span>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-[#111111] truncate">{p.name}</p>
                    <p className="text-[10px] text-[#6B6B6B]">{p.category} · ${p.price} · {p.rating}★</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 shrink-0 ml-4">
                  <div className="text-right">
                    <p className="text-xs text-[#6B6B6B]">Sales</p>
                    <p className="text-sm font-semibold text-[#111111]">${(p.estimated_monthly_sales / 1000000).toFixed(1)}M</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-[#6B6B6B]">Traffic</p>
                    <p className="text-sm font-semibold text-[#111111]">{(p.estimated_monthly_traffic / 1000000).toFixed(1)}M</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {customerInsights && !state.loading && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="rounded-2xl p-4 bg-[#F5F5F7] shadow-sm">
            <div className="flex items-center gap-1.5 mb-1">
              <Star size={12} className="text-yellow-500" />
              <span className="text-[10px] text-[#6B6B6B]">Avg Rating</span>
            </div>
            <span className="text-lg font-bold text-[#111111]">{customerInsights.avg_rating}</span>
          </div>
          <div className="rounded-2xl p-4 bg-[#F5F5F7] shadow-sm">
            <div className="flex items-center gap-1.5 mb-1">
              <Activity size={12} className="text-[#2563EB]" />
              <span className="text-[10px] text-[#6B6B6B]">Total Reviews</span>
            </div>
            <span className="text-lg font-bold text-[#111111]">{(customerInsights.total_reviews / 1000).toFixed(1)}K</span>
          </div>
          <div className="rounded-2xl p-4 bg-[#F5F5F7] shadow-sm">
            <div className="flex items-center gap-1.5 mb-1">
              <Users size={12} className="text-green-500" />
              <span className="text-[10px] text-[#6B6B6B]">Repeat Rate</span>
            </div>
            <span className="text-lg font-bold text-[#111111]">{(customerInsights.repeat_rate * 100).toFixed(0)}%</span>
          </div>
          <div className="rounded-2xl p-4 bg-[#F5F5F7] shadow-sm">
            <div className="flex items-center gap-1.5 mb-1">
              <TrendingUp size={12} className="text-purple-500" />
              <span className="text-[10px] text-[#6B6B6B]">Top Category</span>
            </div>
            <span className="text-lg font-bold text-[#111111] truncate block">{customerInsights.top_category}</span>
          </div>
        </div>
      )}

      <div className="rounded-[24px] p-6 bg-[#F5F5F7] shadow-sm">
        <h3 className="text-lg font-semibold text-[#111111] mb-4 flex items-center gap-2">
          <Globe size={18} className="text-[#2563EB]" />
          Manual Clone
        </h3>
        <p className="text-xs text-[#6B6B6B] mb-4">Use manual cloning when automated store detection is unavailable.</p>
        <div className="flex items-center gap-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 p-3 rounded-xl bg-white shadow-sm">
              <ExternalLink size={16} className="text-[#6B6B6B]" />
              <input
                type="url" value={cloneUrl}
                onChange={(e) => setCloneUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !cloning && doManualClone()}
                placeholder="Paste competitor Shopify URL..."
                disabled={cloning}
                className="flex-1 bg-transparent border-none outline-none text-sm text-[#111111] placeholder:text-[#6B6B6B] disabled:opacity-50"
              />
            </div>
          </div>
          <button onClick={doManualClone} disabled={cloning || !cloneUrl.trim()}
            className="px-5 py-3 rounded-xl bg-[#2563EB] text-white text-sm font-medium hover:bg-[#1d4ed8] transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            {cloning ? <RefreshCw size={14} className="animate-spin" /> : <CheckCircle size={14} />}
            {cloning ? "Cloning..." : "Clone"}
          </button>
        </div>
        {cloneResult && (
          <div className="mt-4 rounded-2xl p-4 bg-white shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-[#111111]">{cloneResult.store?.name ?? cloneResult.brand_name}</span>
                {cloneResult.cloned_from_template && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-100 text-gray-600" title="Automatically used optimized template">
                    Cloned from optimized template
                  </span>
                )}
              </div>
              <span className="text-xs text-[#6B6B6B]">{cloneResult.sections?.length ?? 0} sections</span>
            </div>
            {cloneResult.design_specs && (
              <div className="flex items-center gap-2 text-[11px] text-[#6B6B6B]">
                <span>Font: {cloneResult.design_specs.font_family}</span>
                <span className="w-1 h-1 rounded-full bg-gray-300" />
                <span>Palette: {cloneResult.design_specs.color_palette?.join(", ")}</span>
              </div>
            )}
            {cloneResult.sections && (
              <div className="mt-2 flex flex-wrap gap-1">
                {cloneResult.sections.map((s) => (
                  <span key={s} className="text-[10px] px-2 py-0.5 rounded-full bg-[#F5F5F7] text-[#6B6B6B]">{s}</span>
                ))}
              </div>
            )}
          </div>
        )}
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
          <button onClick={() => getForecast(Number(activeProduct?.price ?? 29.99))} className="px-4 py-3 rounded-xl bg-[#2563EB] text-white text-sm font-medium hover:bg-[#1d4ed8] transition-colors flex items-center gap-2">
            <RefreshCw size={14} /> Forecast
          </button>
        </div>
        {forecast && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="text-xs text-[#6B6B6B]">Est. Revenue</div>
              <div className="text-lg font-bold text-[#111111]">${forecast.estimated_revenue ?? 0}</div>
            </div>
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="text-xs text-[#6B6B6B]">Est. Orders</div>
              <div className="text-lg font-bold text-[#111111]">{forecast.estimated_purchases ?? 0}</div>
            </div>
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="text-xs text-[#6B6B6B]">ROAS</div>
              <div className="text-lg font-bold text-[#111111]">{forecast.estimated_roas ?? 0}x</div>
            </div>
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="text-xs text-[#6B6B6B]">Est. Clicks</div>
              <div className="text-lg font-bold text-[#111111]">{forecast.estimated_clicks ?? 0}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
