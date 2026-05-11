import { useState } from "react";
import { Search, ArrowRight, RefreshCw, TrendingUp, DollarSign, Star, Globe, Database, ExternalLink } from "lucide-react";
import AnalysisDetail from "./components/AnalysisDetail";

const API = "https://niklinx-engine-v2.onrender.com";

const SOURCE_BADGES = {
  aliexpress: { label: "AliExpress", color: "bg-orange-100 text-orange-700" },
  amazon: { label: "Amazon", color: "bg-yellow-100 text-yellow-700" },
  google_shopping: { label: "Shopping", color: "bg-blue-100 text-blue-700" },
  local: { label: "Local DB", color: "bg-gray-100 text-gray-600" },
};

export default function ProductResearch() {
  const [query, setQuery] = useState("");
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
      setResults(await r.json());
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
        <p className="text-[#6B6B6B] mt-1">AI-powered product discovery and analysis</p>
      </div>

      <div className="flex items-center gap-3 p-4 rounded-[24px] bg-[#F5F5F7] shadow-sm">
        <Search size={18} className="text-[#6B6B6B]" />
        <input
          type="text" placeholder="Search global markets for winning products..."
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

      {loading && (
        <div className="rounded-[24px] p-8 bg-[#F5F5F7] shadow-sm flex flex-col items-center justify-center gap-4">
          <RefreshCw size={28} className="text-[#2563EB] animate-spin" />
          <div className="text-center">
            <p className="text-sm font-medium text-[#111111]">Searching Global Markets...</p>
            <p className="text-xs text-[#6B6B6B] mt-1">Scanning AliExpress, Amazon, and Google Shopping</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-orange-400 animate-pulse" />
            <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" style={{ animationDelay: "0.2s" }} />
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" style={{ animationDelay: "0.4s" }} />
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
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(results.products || []).slice(0, 12).map((p, i) => {
              const badge = SOURCE_BADGES[p.source] || SOURCE_BADGES.local;
              return (
                <div key={p.id || `live-${i}`} className="rounded-[24px] p-5 bg-[#F5F5F7] shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-[#111111] truncate">{p.name}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${badge.color}`}>
                          {badge.label}
                        </span>
                        {p.category && <span className="text-xs text-[#6B6B6B] truncate">{p.category}</span>}
                      </div>
                    </div>
                    <div className="flex items-center gap-1 text-xs text-green-600 shrink-0 ml-2">
                      <Star size={12} /> {p.rating}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <DollarSign size={14} className="text-[#2563EB]" />
                      <span className="text-lg font-bold text-[#111111]">${p.sale_price || p.price}</span>
                      {p.sale_price && <span className="text-xs text-[#6B6B6B] line-through">${p.price}</span>}
                    </div>
                  </div>

                  {isLiveSource && (
                    <div className="flex items-center gap-3 mt-2">
                      {p.winning_score && (
                        <div className="flex items-center gap-1">
                          <TrendingUp size={12} className={p.winning_score >= 70 ? "text-green-500" : p.winning_score >= 50 ? "text-orange-400" : "text-red-400"} />
                          <span className="text-xs font-medium text-[#111111]">{p.winning_score}</span>
                        </div>
                      )}
                      {p.profit_margin && (
                        <div className="flex items-center gap-1">
                          <span className="text-xs text-green-600 font-medium">{p.profit_margin}%</span>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/50">
                    {p.id && p.id.startsWith("prod_") ? (
                      <button
                        onClick={() => doAnalyze(p.id)}
                        disabled={analyzing === p.id}
                        className="text-xs px-3 py-1.5 rounded-xl bg-[#2563EB] text-white hover:bg-[#1d4ed8] transition-colors disabled:opacity-50 flex items-center gap-1"
                      >
                        {analyzing === p.id ? <RefreshCw size={12} className="animate-spin" /> : <TrendingUp size={12} />}
                        Analyze
                      </button>
                    ) : (
                      <a
                        href={p.source_url || `https://www.google.com/search?q=${encodeURIComponent(p.name)}`}
                        target="_blank" rel="noopener noreferrer"
                        className="text-xs px-3 py-1.5 rounded-xl bg-white text-[#111111] hover:bg-gray-50 transition-colors flex items-center gap-1 border border-gray-200"
                      >
                        <ExternalLink size={12} />
                        View Source
                      </a>
                    )}
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
