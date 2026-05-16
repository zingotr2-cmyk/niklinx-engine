import { useState, useEffect, useCallback, useRef } from "react";
import { Search, ArrowRight, RefreshCw, TrendingUp, DollarSign, Star, Globe, Database, ExternalLink, MapPin, Music, Zap, Copy } from "lucide-react";
import AnalysisDetail from "./components/AnalysisDetail";
import { toast } from "./components/Toast";
import { useActiveProduct } from "./context/ProductContext";

const API = "https://niklinx-engine-v2.onrender.com";

const REGION_GROUPS = [
  {
    label: "North America",
    countries: [
      { value: "usa", label: "USA", flag: "🇺🇸" },
      { value: "canada", label: "Canada", flag: "🇨🇦" },
    ],
  },
  {
    label: "Europe",
    countries: [
      { value: "uk", label: "UK", flag: "🇬🇧" },
      { value: "germany", label: "Germany", flag: "🇩🇪" },
      { value: "france", label: "France", flag: "🇫🇷" },
    ],
  },
  {
    label: "GCC",
    countries: [
      { value: "uae", label: "UAE", flag: "🇦🇪" },
      { value: "saudi_arabia", label: "Saudi Arabia", flag: "🇸🇦" },
      { value: "algeria", label: "Algeria", flag: "🇩🇿" },
    ],
  },
];

const FLAT_REGIONS = REGION_GROUPS.flatMap((g) => g.countries);

const SOURCE_BADGES = {
  aliexpress: { label: "AliExpress", color: "bg-orange-100 text-orange-700" },
  amazon: { label: "Amazon", color: "bg-yellow-100 text-yellow-700" },
  google_shopping: { label: "Shopping", color: "bg-blue-100 text-blue-700" },
  local: { label: "Local DB", color: "bg-gray-100 text-gray-600" },
};

function getSocialBadge(score) {
  if (!score) return null;
  if (score >= 85) return { label: "Viral", icon: "🔥", color: "bg-red-100 text-red-600" };
  if (score >= 70) return { label: "Trending", icon: "📈", color: "bg-green-100 text-green-700" };
  if (score >= 50) return { label: "Rising", icon: "⚡", color: "bg-yellow-100 text-yellow-700" };
  if (score >= 30) return { label: "Emerging", icon: "🌱", color: "bg-blue-100 text-blue-700" };
  return { label: "Normal", icon: "💤", color: "bg-gray-100 text-gray-500" };
}

export default function ProductResearch() {
  const [query, setQuery] = useState("");
  const [region, setRegion] = useState("usa");
  const [showRegionPicker, setShowRegionPicker] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [socialScores, setSocialScores] = useState({});
  const [analyzing, setAnalyzing] = useState(null);
  const [analyzedProduct, setAnalyzedProduct] = useState(null);
  const [regionTransition, setRegionTransition] = useState(false);
  const { setActiveProduct, markSynced } = useActiveProduct();
  const pendingQuery = useRef("");

  const activeRegion = FLAT_REGIONS.find((r) => r.value === region);

  const fetchSocialScores = useCallback(async (q, products) => {
    if (!products?.length) return;
    const firstFew = products.slice(0, 6);
    const scores = {};
    await Promise.all(
      firstFew.map(async (p) => {
        const searchTerm = p.title || p.name || q;
        try {
          const r = await fetch(`${API}/api/social/proof`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: searchTerm, region, max_results: 5 }),
          });
          const data = await r.json();
          const key = p.id || p.title || searchTerm;
          scores[key] = {
            score: data.social_proof_score,
            classification: data.classification,
            icon: data.icon,
            label: data.label,
            tiktokVideos: data.tiktok_summary?.total_videos || 0,
            facebookAds: data.facebook_summary?.total_ads || 0,
          };
        } catch {}
      })
    );
    setSocialScores(scores);
  }, [region]);

  const doSearch = useCallback(async (searchQuery, searchRegion) => {
    const q = searchQuery || query;
    const r = searchRegion || region;
    if (!q.trim()) return;
    pendingQuery.current = q;
    setLoading(true);
    setAnalyzedProduct(null);
    setResults(null);
    setSocialScores({});
    try {
      const body = JSON.stringify({ max_price: 500, category: q, region: r });
      const resp = await fetch(`${API}/api/research/search`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body,
      });
      const data = await resp.json();
      if (data.products?.length < 5) {
        try {
          const r2 = await fetch(`${API}/api/search`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: q, region: r, max_results: 20 }),
          });
          const live = await r2.json();
          if (live.results?.length > 0) {
            setResults({ products: live.results, source: "live", total: live.total, health: live.health, region: r });
            setLoading(false);
            fetchSocialScores(q, live.results);
            return;
          }
        } catch {}
      }
      setResults({ ...data, region: r });
      setLoading(false);
      fetchSocialScores(q, data.products || []);
    } catch { setResults(null); setLoading(false) }
  }, [query, region, fetchSocialScores]);

  // Mark research as synced when results are ready
  useEffect(() => {
    if (results?.products?.length) {
      const first = results.products[0];
      const id = first.id || first.title || "";
      if (id) markSynced("research", id);
    }
  }, [results, markSynced]);

  // Phase 3: Auto-refresh when region changes (if there's an active query)
  useEffect(() => {
    if (pendingQuery.current && !loading) {
      setRegionTransition(true);
      const timer = setTimeout(() => {
        doSearch(pendingQuery.current, region);
        setTimeout(() => setRegionTransition(false), 400);
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [region]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleRegionChange = (newRegion) => {
    setRegion(newRegion);
    setShowRegionPicker(false);
    if (pendingQuery.current) {
      setRegionTransition(true);
    }
  };

  const copySourceUrl = async (url, title) => {
    const sourceUrl = url || `https://www.google.com/search?q=${encodeURIComponent(title)}`;
    try {
      await navigator.clipboard.writeText(sourceUrl);
      toast("URL copied. Paste in Store Insights to begin manual cloning");
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = sourceUrl;
      textarea.style.position = "fixed";
      textarea.style.opacity = 0;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      toast("URL copied. Paste in Store Insights to begin manual cloning");
    }
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
        <p className="text-[#6B6B6B] mt-1">Discover trending products across 9 global markets with real-time social proof intelligence.</p>
      </div>

      <div className="rounded-[24px] p-4 bg-[#F5F5F7] shadow-sm space-y-3">
        <div className="flex items-center gap-3">
          <Search size={18} className="text-[#6B6B6B]" />
          <input
            type="text" placeholder="Search any product, trend, or category across 9 global markets..."
            value={query} onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && doSearch()}
            className="flex-1 bg-transparent border-none outline-none text-sm text-[#111111] placeholder:text-[#6B6B6B]"
          />
          <button onClick={() => doSearch()} disabled={loading}
            className="px-4 py-2 rounded-xl bg-[#2563EB] text-white text-sm font-medium hover:bg-[#1d4ed8] transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? <RefreshCw size={14} className="animate-spin" /> : <ArrowRight size={14} />}
            Search
          </button>
        </div>
        <div className="flex items-center gap-2 relative">
          <MapPin size={14} className="text-[#6B6B6B]" />
          <span className="text-xs text-[#6B6B6B]">Target Market:</span>
          <button
            onClick={() => setShowRegionPicker(!showRegionPicker)}
            className="px-3 py-1 rounded-full text-xs font-medium bg-[#2563EB] text-white flex items-center gap-1.5"
          >
            {activeRegion?.flag} {activeRegion?.label}
          </button>
          {showRegionPicker && (
            <div className="absolute top-full left-0 mt-2 z-50 bg-white rounded-2xl shadow-xl border border-gray-100 p-3 min-w-[220px]">
              {REGION_GROUPS.map((group) => (
                <div key={group.label} className="mb-2 last:mb-0">
                  <div className="text-[10px] font-semibold text-[#6B6B6B] uppercase tracking-wider px-2 mb-1">{group.label}</div>
                  {group.countries.map((c) => (
                    <button
                      key={c.value}
                      onClick={() => handleRegionChange(c.value)}
                      className={`w-full flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium transition-colors ${
                        region === c.value ? "bg-[#2563EB] text-white" : "text-[#111111] hover:bg-[#F5F5F7]"
                      }`}
                    >
                      {c.flag} {c.label}
                    </button>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Phase 4: Dynamic Region Header */}
      {pendingQuery.current && results && !loading && (
        <div className={`transition-all duration-300 ${regionTransition ? "opacity-0 translate-y-[-8px]" : "opacity-100 translate-y-0"}`}>
          <div className="rounded-2xl px-5 py-3 bg-gradient-to-r from-[#F5F5F7] to-white shadow-sm border border-gray-100/50 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-lg">{activeRegion?.flag}</span>
              <div>
                <span className="text-sm font-semibold text-[#111111]">Displaying Top Winners in {activeRegion?.label}</span>
                <p className="text-[11px] text-[#6B6B6B] mt-0.5">{results.products?.length || 0} products • {isLiveSource ? "Live Markets" : "Database"} • {activeRegion?.flag} {(REGION_GROUPS.flatMap(g => g.countries).find(c => c.value === region)?.label || "").toUpperCase()}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {isLiveSource ? (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium flex items-center gap-1">
                  <Globe size={10} /> Live
                </span>
              ) : (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 font-medium flex items-center gap-1">
                  <Database size={10} /> Local
                </span>
              )}
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="rounded-[24px] p-10 bg-[#F5F5F7] shadow-sm flex flex-col items-center justify-center gap-5">
          <div className="relative">
            <RefreshCw size={32} className="text-[#2563EB] animate-spin" />
            <Globe size={16} className="text-[#6B6B6B] absolute -top-1 -right-1 animate-pulse" />
          </div>
          <div className="text-center">
            <p className="text-base font-semibold text-[#111111]">
              {regionTransition ? `Switching to ${activeRegion?.flag} ${activeRegion?.label}...` : `Analyzing ${activeRegion?.label} Markets...`}
            </p>
            <p className="text-xs text-[#6B6B6B] mt-1.5">Aggregating marketplace data, social signals, and trend intelligence</p>
          </div>
        </div>
      )}

      {results && !loading && (
        <div className={`space-y-4 transition-all duration-300 ${regionTransition ? "opacity-0" : "opacity-100"}`}>
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
              const socialKey = p.id || p.title || "";
              const social = socialScores[socialKey];
              const soc = getSocialBadge(social?.score);
              return (
                <div key={p.id || `live-${i}`} className="rounded-[24px] p-5 bg-[#F5F5F7] shadow-sm hover:shadow-md transition-all duration-200 hover:scale-[1.02] group">
                  {image && (
                    <div className="rounded-xl overflow-hidden mb-3 bg-white h-32 flex items-center justify-center relative">
                      <img src={image} alt={title} className="max-h-full max-w-full object-contain" loading="lazy" onError={(e) => { e.target.style.display = "none" }} />
                      {social && (
                        <div className="absolute top-2 right-2 flex items-center gap-1">
                          {social.tiktokVideos > 0 && (
                            <span className="bg-black/80 text-white text-[9px] px-1.5 py-0.5 rounded-full flex items-center gap-0.5">
                              <Music size={8} /> {social.tiktokVideos}
                            </span>
                          )}
                          {social.facebookAds > 0 && (
                            <span className="bg-blue-600/80 text-white text-[9px] px-1.5 py-0.5 rounded-full">f {social.facebookAds}</span>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-[#111111] line-clamp-2">{title}</div>
                      <div className="flex items-center gap-1.5 mt-1 flex-wrap">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${badge.color}`}>{badge.label}</span>
                        {soc && (
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${soc.color} inline-flex items-center gap-0.5`}>
                            {soc.icon} {soc.label}
                          </span>
                        )}
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
                    {(p.currency || p.region) && (
                      <span className="text-[10px] text-[#6B6B6B] font-medium">{p.currency || ""} {p.region ? p.region.toUpperCase() : ""}</span>
                    )}
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

                  {social && (
                    <div className="mt-2 flex items-center gap-2 text-[10px] text-[#6B6B6B] bg-white/50 rounded-xl px-2 py-1.5">
                      <Zap size={10} className={social.score >= 50 ? "text-yellow-500" : "text-gray-400"} />
                      <span className="font-medium">Social Proof: {social.score}</span>
                      {social.tiktokVideos > 0 && <span className="flex items-center gap-0.5"><Music size={9} /> {social.tiktokVideos}</span>}
                      {social.facebookAds > 0 && <span className="flex items-center gap-0.5">f {social.facebookAds}</span>}
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
                      <div className="flex items-center gap-1">
                        <a href={p.product_url || `https://www.google.com/search?q=${encodeURIComponent(title)}`}
                          target="_blank" rel="noopener noreferrer"
                          onClick={() => setActiveProduct({ id: p.id || title, url: p.product_url, name: title, price, image, category: p.supplier || p.source || "general" })}
                          className="text-xs px-3 py-1.5 rounded-xl bg-white text-[#111111] hover:bg-gray-50 transition-colors flex items-center gap-1 border border-gray-200"
                        >
                          <ExternalLink size={12} /> View Source
                        </a>
                        <button onClick={() => { copySourceUrl(p.product_url, title); setActiveProduct({ id: p.id || title, url: p.product_url, name: title, price, image, category: p.supplier || p.source || "general" }); }}
                          className="text-xs p-1.5 rounded-xl bg-white text-[#6B6B6B] hover:bg-gray-50 hover:text-[#111111] transition-colors border border-gray-200"
                          title="Copy URL for cloning"
                        >
                          <Copy size={12} />
                        </button>
                      </div>
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
