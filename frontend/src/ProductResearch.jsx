import { useState } from "react";
import { Search, ArrowRight, RefreshCw, TrendingUp, DollarSign, Star, Globe, Database, ExternalLink, MapPin } from "lucide-react";
import AnalysisDetail from "./components/AnalysisDetail";

const API = "https://niklinx-engine-v2.onrender.com";

const REGIONS = [
  { value: "usa", label: "USA", flag: "🇺🇸" },
  { value: "europe", label: "Europe", flag: "🇪🇺" },
  { value: "gcc", label: "Gulf (GCC)", flag: "🇦🇪" },
];

const SOURCE_BADGES = {
  aliexpress: { label: "AliExpress", color: "bg-orange-100 text-orange-700" },
  amazon: { label: "Amazon", color: "bg-yellow-100 text-yellow-700" },
  google_shopping: { label: "Shopping", color: "bg-blue-100 text-blue-700" },
  local: { label: "Local DB", color: "bg-gray-100 text-gray-600" },
};

export default function ProductResearch() {
  const [query, setQuery] = useState("");
  const [region, setRegion] = useState("usa");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(null);
  const [analyzedProduct, setAnalyzedProduct] = useState(null);

  const doSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setAnalyzedProduct(null);
    setResults(null);
    try {
      const r = await fetch(`${API}/api/research/search`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ max_price: 500, category: query }),
      });
      const data = await r.json();
      if (data.products?.length < 5) {
        try {
          const r2 = await fetch(`${API}/api/search`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, region, max_results: 20 }),
          });
          const live = await r2.json();
          if (live.results?.length > 0) {
            setResults({ products: live.results, source: "live", total: live.total, health: live.health });
            return;
          }
        } catch {}
      }
      setResults(data);
    } catch { setResults(null) }
    setLoading(false);
  };

  const doAnalyze = async (productId) => {
    setAnalyzing(productId);
    try {
      const r = await fetch(`${API}/api/research/analyze`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: productId }),
      });
      const data = await r.json();
      setAnalyzedProduct(data);
    } catch {}
    setAnalyzing(null);
  };

  if (analyzedProduct) {
    return <AnalysisDetail data={analyzedProduct} onBack={() => setAnalyzedProduct(null)} />;
  }

  const isLiveSource = results?.source === "live";

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold text-[#111111] tracking-tight">Product Research</h1>
        <p className="text-[#6B6B6B] mt-1">Live global product discovery across Amazon, AliExpress, and Google Shopping</p>
      </div>

      <div className="rounded-[24px] p-4 bg-[#F5F5F7] shadow-sm space-y-3">
        <div className="flex items-center gap-3">
          <Search size={18} className="text-[#6B6B6B]" />
          <input
            type="text" placeholder="Scan global markets for winning products..."
            value={query} onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && doSearch()}
            className="flex-1 bg-transparent border-none outline-none text-sm text-[#111111] placeholder:text-[#6B6B6B]"
          />
          <button onClick={doSearch} disabled={loading}
            className="px-4 py-2 rounded-xl bg-[#2563EB] text-white text-sm font-medium hover:bg-[#1d4ed8] transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? <RefreshCw size={14} className="animate-spin" /> : <ArrowRight size={14} />}
            Search
          </button>
        </div>
        <div className="flex items-center gap-2">
          <MapPin size={14} className="text-[#6B6B6B]" />
          <span className="text-xs text-[#6B6B6B]">Market:</span>
          <div className="flex gap-1">
            {REGIONS.map((r) => (
              <button key={r.value} onClick={() => setRegion(r.value)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  region === r.value
                    ? "bg-[#2563EB] text-white"
                    : "bg-white text-[#6B6B6B] hover:text-[#111111]"
                }`}
              >
                {r.flag} {r.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading && (
        <div className="rounded-[24px] p-10 bg-[#F5F5F7] shadow-sm flex flex-col items-center justify-center gap-5">
          <div className="relative">
            <RefreshCw size={32} className="text-[#2563EB] animate-spin" />
            <Globe size={16} className="text-[#6B6B6B] absolute -top-1 -right-1 animate-pulse" />
          </div>
          <div className="text-center">
            <p className="text-base font-semibold text-[#111111]">Scanning Global Markets for Winning Products...</p>
            <p className="text-xs text-[#6B6B6B] mt-1.5">Searching Amazon, AliExpress, and Google Shopping across {REGIONS.find(r => r.value === region)?.label}</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-100 text-orange-700 text-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-orange-500 animate-pulse" /> AliExpress
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-yellow-100 text-yellow-700 text-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-yellow-500 animate-pulse" style={{ animationDelay: "0.2s" }} /> Amazon
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" style={{ animationDelay: "0.4s" }} /> Shopping
            </span>
          </div>
        </div>
      )}

      {results && !loading && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-[#111111]">{results.products?.length || 0} products found</h3>
            <div className="flex items-center gap-2">
              {isLiveSource ? (
                <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                  <Globe size={12} /> Live Markets
                </span>
              ) : (
                <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                  <Database size={12} /> Local Database
                </span>
              )}
              <span className="text-xs text-[#6B6B6B]">{REGIONS.find(r => r.value === region)?.flag} {REGIONS.find(r => r.value === region)?.label}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(results.products || []).slice(0, 20).map((p, i) => {
              const title = p.title || p.name || "";
              const price = p.price || p.sale_price || 0;
              const rating = p.rating || 0;
              const source = p.supplier || p.source || "local";
              const badge = SOURCE_BADGES[source] || SOURCE_BADGES.local;
              const score = p.ai_score || p.winning_score;
              const margin = p.profit_margin;
              const image = p.image || "";
              const orders = p.orders || p.reviews || 0;
              return (
                <div key={p.id || `live-${i}`} className="rounded-[24px] p-5 bg-[#F5F5F7] shadow-sm hover:shadow-md transition-all duration-200">
                  {image && (
                    <div className="rounded-xl overflow-hidden mb-3 bg-white h-32 flex items-center justify-center">
                      <img src={image} alt={title} className="max-h-full max-w-full object-contain" loading="lazy" onError={(e) => { e.target.style.display = "none" }} />
                    </div>
                  )}
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-[#111111] line-clamp-2">{title}</div>
                      <div className="flex items-center gap-1.5 mt-1">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${badge.color}`}>
                          {badge.label}
                        </span>
                        {orders > 0 && <span className="text-[10px] text-[#6B6B6B]">{orders.toLocaleString()} orders</span>}
                      </div>
                    </div>
                    <div className="flex items-center gap-1 text-xs text-green-600 shrink-0 ml-2">
                      <Star size={12} /> {rating}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <DollarSign size={14} className="text-[#2563EB]" />
                      <span className="text-lg font-bold text-[#111111]">${price}</span>
                    </div>
                  </div>

                  {(score || margin) && (
                    <div className="flex items-center gap-3 mt-2">
                      {score && (
                        <div className="flex items-center gap-1">
                          <TrendingUp size={12} className={score >= 70 ? "text-green-500" : score >= 50 ? "text-orange-400" : "text-red-400"} />
                          <span className="text-xs font-medium text-[#111111]">{score}</span>
                        </div>
                      )}
                      {margin && <span className="text-xs text-green-600 font-medium">{margin}% margin</span>}
                    </div>
                  )}

                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/50">
                    {p.id && p.id.startsWith("prod_") ? (
                      <button onClick={() => doAnalyze(p.id)} disabled={analyzing === p.id}
                        className="text-xs px-3 py-1.5 rounded-xl bg-[#2563EB] text-white hover:bg-[#1d4ed8] transition-colors disabled:opacity-50 flex items-center gap-1"
                      >
                        {analyzing === p.id ? <RefreshCw size={12} className="animate-spin" /> : <TrendingUp size={12} />}
                        Analyze
                      </button>
                    ) : (
                      <a href={p.product_url || p.source_url || `https://www.google.com/search?q=${encodeURIComponent(title)}`}
                        target="_blank" rel="noopener noreferrer"
                        className="text-xs px-3 py-1.5 rounded-xl bg-white text-[#111111] hover:bg-gray-50 transition-colors flex items-center gap-1 border border-gray-200"
                      >
                        <ExternalLink size={12} />
                        View Source
                      </a>
                    )}
                    {p.region && <span className="text-[10px] text-[#6B6B6B]">{p.currency} {p.region.toUpperCase()}</span>}
                  </div>

                  {p.ai_insight && (
                    <div className="mt-3 text-xs text-[#6B6B6B] bg-white rounded-xl p-3">{p.ai_insight}</div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
