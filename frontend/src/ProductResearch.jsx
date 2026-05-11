import { useState } from "react";
import { Search, ArrowRight, RefreshCw, TrendingUp, DollarSign, Star, ExternalLink } from "lucide-react";
import AnalysisDetail from "./components/AnalysisDetail";

const API = "https://niklinx-engine-v2.onrender.com";

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
    try {
      const r = await fetch(`${API}/api/research/search`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ max_price: 100, category: query }),
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

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold text-[#111111] tracking-tight">Product Research</h1>
        <p className="text-[#6B6B6B] mt-1">AI-powered product discovery and analysis</p>
      </div>

      <div className="flex items-center gap-3 p-4 rounded-[24px] bg-[#F5F5F7] shadow-sm">
        <Search size={18} className="text-[#6B6B6B]" />
        <input
          type="text" placeholder="Search winning products..."
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

      {results && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-[#111111]">{results.products?.length || 0} products found</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(results.products || []).slice(0, 9).map((p) => (
              <div key={p.id} className="rounded-[24px] p-5 bg-[#F5F5F7] shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="text-sm font-semibold text-[#111111]">{p.name}</div>
                    <div className="text-xs text-[#6B6B6B] mt-0.5">{p.category}</div>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-green-600">
                    <Star size={12} /> {p.rating}
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <DollarSign size={14} className="text-[#2563EB]" />
                    <span className="text-lg font-bold text-[#111111]">${p.sale_price || p.price}</span>
                    {p.sale_price && <span className="text-xs text-[#6B6B6B] line-through">${p.price}</span>}
                  </div>
                  <button
                    onClick={() => doAnalyze(p.id)}
                    disabled={analyzing === p.id}
                    className="text-xs px-3 py-1.5 rounded-xl bg-[#2563EB] text-white hover:bg-[#1d4ed8] transition-colors disabled:opacity-50 flex items-center gap-1"
                  >
                    {analyzing === p.id ? <RefreshCw size={12} className="animate-spin" /> : <TrendingUp size={12} />}
                    Analyze
                  </button>
                </div>
                {p.ai_insight && (
                  <div className="mt-3 text-xs text-[#6B6B6B] bg-white rounded-xl p-3">{p.ai_insight}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
