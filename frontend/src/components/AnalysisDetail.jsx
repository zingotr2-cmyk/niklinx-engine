import { useState, useEffect } from "react";
import { TrendingUp, DollarSign, Users, ShoppingCart, Star, ExternalLink, Zap, MessageCircle, Hash, Music, Activity, ArrowLeft } from "lucide-react";
import ProgressRing from "./ProgressRing";

const API = "https://niklinx-engine-v2.onrender.com";
const SCORE_THRESHOLDS = [
  { min: 80, color: "#22c55e", label: "Strong Buy" },
  { min: 50, color: "#f59e0b", label: "Consider" },
  { min: 0, color: "#ef4444", label: "Skip" },
];

function getScoreColor(score) {
  const t = SCORE_THRESHOLDS.find((t) => score >= t.min);
  return t || SCORE_THRESHOLDS[2];
}

export default function AnalysisDetail({ data, product, onBack }) {
  const [socialData, setSocialData] = useState(null);
  const [loadingSocial, setLoadingSocial] = useState(false);

  if (!data) return null;
  const a = data.analysis;
  const p = data.product || product;
  const scoreInfo = getScoreColor(a.winning_score);

  useEffect(() => {
    if (!p?.name) return;
    setLoadingSocial(true);
    fetch(`${API}/api/social/proof`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: p.name, region: "usa", max_results: 5 }),
    })
      .then((r) => r.json())
      .then((d) => setSocialData(d))
      .catch(() => {})
      .finally(() => setLoadingSocial(false));
  }, [p?.name]);

  const socialScore = socialData?.social_proof_score;
  const socialInfo = socialScore >= 85 ? { label: "Viral", color: "#ef4444", icon: "🔥" }
    : socialScore >= 70 ? { label: "Trending", color: "#22c55e", icon: "📈" }
    : socialScore >= 50 ? { label: "Rising", color: "#f59e0b", icon: "⚡" }
    : socialScore >= 30 ? { label: "Emerging", color: "#3b82f6", icon: "🌱" }
    : socialScore != null ? { label: "Normal", color: "#6B6B6B", icon: "💤" }
    : null;

  const showSocial = socialData && socialScore != null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <button onClick={onBack} className="text-sm text-[#6B6B6B] hover:text-[#111111] transition-colors inline-flex items-center gap-1.5"><ArrowLeft size={14} /> Back to results</button>
      </div>

      <div className="rounded-[24px] p-6 bg-[#F5F5F7] shadow-sm">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold text-[#111111]">{p?.name || product?.name}</h2>
            <p className="text-sm text-[#6B6B6B] mt-0.5">{p?.category || product?.category}</p>
          </div>
          <div className="flex items-center gap-2">
            {showSocial && (
              <span className="px-3 py-1 rounded-full text-xs font-semibold text-white shadow-sm flex items-center gap-1"
                style={{ backgroundColor: socialInfo?.color || "#6B6B6B" }}
              >
                {socialInfo?.icon} {socialInfo?.label}
              </span>
            )}
            <span className="px-3 py-1 rounded-full text-xs font-semibold text-white shadow-sm"
              style={{ backgroundColor: scoreInfo.color }}
            >
              {scoreInfo.label}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center justify-center">
            <ProgressRing value={a.winning_score} size={140} strokeWidth={10} label="Winning Score" sublabel={scoreInfo.label} color={scoreInfo.color} />
          </div>

          <div className="md:col-span-2 grid grid-cols-2 gap-3">
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="flex items-center gap-2 mb-1">
                <DollarSign size={14} className="text-green-500" />
                <span className="text-xs text-[#6B6B6B]">Profit Margin</span>
              </div>
              <span className="text-lg font-bold text-[#111111]">{a.profit_margin}%</span>
            </div>
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="flex items-center gap-2 mb-1">
                <Users size={14} className="text-[#2563EB]" />
                <span className="text-xs text-[#6B6B6B]">Competitor Traffic</span>
              </div>
              <span className="text-lg font-bold text-[#111111]">{(a.total_competitor_traffic / 1000000).toFixed(1)}M</span>
            </div>
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="flex items-center gap-2 mb-1">
                <ShoppingCart size={14} className="text-purple-500" />
                <span className="text-xs text-[#6B6B6B]">Competitor Sales</span>
              </div>
              <span className="text-lg font-bold text-[#111111]">{(a.total_competitor_sales / 1000000).toFixed(1)}M</span>
            </div>
            <div className="rounded-2xl p-4 bg-white shadow-sm">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp size={14} className="text-orange-500" />
                <span className="text-xs text-[#6B6B6B]">Competition Level</span>
              </div>
              <span className="text-lg font-bold text-[#111111]">{a.competition_level}</span>
            </div>
          </div>
        </div>

        {showSocial && (
          <div className="mt-4 rounded-2xl p-4 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-100">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Activity size={16} className="text-purple-600" />
                <span className="text-sm font-medium text-purple-800">Social Proof Intelligence</span>
              </div>
              {loadingSocial && <span className="text-[10px] text-[#6B6B6B] animate-pulse">Updating...</span>}
            </div>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <div className="rounded-xl p-3 bg-white/80 shadow-sm text-center">
                <div className="text-lg font-bold text-purple-700">{socialScore}</div>
                <div className="text-[10px] text-[#6B6B6B]">Social Proof</div>
              </div>
              <div className="rounded-xl p-3 bg-white/80 shadow-sm text-center">
                <div className="flex items-center justify-center gap-1 text-lg font-bold text-[#111111]">
                  <Music size={12} /> {socialData?.tiktok_summary?.total_videos || 0}
                </div>
                <div className="text-[10px] text-[#6B6B6B]">TikTok Videos</div>
              </div>
              <div className="rounded-xl p-3 bg-white/80 shadow-sm text-center">
                <div className="text-lg font-bold text-[#111111]">{(socialData?.tiktok_summary?.total_views || 0) >= 1000000 ? `${(socialData.tiktok_summary.total_views / 1000000).toFixed(1)}M` : (socialData?.tiktok_summary?.total_views || 0) >= 1000 ? `${(socialData.tiktok_summary.total_views / 1000).toFixed(1)}K` : socialData?.tiktok_summary?.total_views || 0}</div>
                <div className="text-[10px] text-[#6B6B6B]">Total Views</div>
              </div>
              <div className="rounded-xl p-3 bg-white/80 shadow-sm text-center">
                <div className="text-lg font-bold text-blue-600 f"> {socialData?.facebook_summary?.total_ads || 0}</div>
                <div className="text-[10px] text-[#6B6B6B]">Facebook Ads</div>
              </div>
              <div className="rounded-xl p-3 bg-white/80 shadow-sm text-center">
                <div className="text-lg font-bold text-[#111111] capitalize">{socialData?.facebook_summary?.ad_intensity || "N/A"}</div>
                <div className="text-[10px] text-[#6B6B6B]">Ad Intensity</div>
              </div>
            </div>
          </div>
        )}

        {a.estimated_monthly_profit > 0 && (
          <div className="mt-4 rounded-2xl p-4 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Zap size={16} className="text-green-600" />
                <span className="text-sm font-medium text-green-800">Estimated Monthly Profit</span>
              </div>
              <span className="text-xl font-bold text-green-700">${a.estimated_monthly_profit.toLocaleString()}</span>
            </div>
          </div>
        )}
      </div>

      <div className="rounded-[24px] p-6 bg-[#F5F5F7] shadow-sm">
        <h3 className="text-lg font-semibold text-[#111111] mb-4">Creative Strategy</h3>
        <div className="space-y-3">
          <div className="rounded-2xl p-4 bg-white shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <Hash size={14} className="text-[#2563EB]" />
              <span className="text-xs font-medium text-[#6B6B6B]">TikTok Hook</span>
            </div>
            <p className="text-sm text-[#111111]">"Stop overpaying for {p?.name?.toLowerCase() || "this product"} — we found the hidden supplier price. Here's why dropshippers are keeping this one secret..."</p>
          </div>
          <div className="rounded-2xl p-4 bg-white shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <MessageCircle size={14} className="text-[#2563EB]" />
              <span className="text-xs font-medium text-[#6B6B6B]">Facebook Ad Copy</span>
            </div>
            <p className="text-sm text-[#111111]">Tired of low-quality products that ruin your store's reputation? Our {p?.name?.toLowerCase() || "winning product"} is tested, reviewed by {(p?.reviews || 0).toLocaleString()}+ customers, and sourced directly from vetted suppliers. <strong>Profit margin: {a.profit_margin}%.</strong></p>
          </div>
        </div>
      </div>

      <div className="rounded-[24px] p-6 bg-[#F5F5F7] shadow-sm">
        <h3 className="text-lg font-semibold text-[#111111] mb-4">Source This Product</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <a
            href={`https://www.aliexpress.com/wholesale?SearchText=${encodeURIComponent(p?.name || "")}`}
            target="_blank" rel="noopener noreferrer"
            className="flex items-center justify-between rounded-2xl p-4 bg-white shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center">
                <ShoppingCart size={16} className="text-orange-500" />
              </div>
              <span className="text-sm font-medium text-[#111111]">AliExpress</span>
            </div>
            <ExternalLink size={14} className="text-[#6B6B6B]" />
          </a>
          <a
            href={`https://www.amazon.com/s?k=${encodeURIComponent(p?.name || "")}`}
            target="_blank" rel="noopener noreferrer"
            className="flex items-center justify-between rounded-2xl p-4 bg-white shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-yellow-100 flex items-center justify-center">
                <Star size={16} className="text-yellow-600" />
              </div>
              <span className="text-sm font-medium text-[#111111]">Amazon</span>
            </div>
            <ExternalLink size={14} className="text-[#6B6B6B]" />
          </a>
        </div>
        <p className="text-xs text-[#6B6B6B] mt-3">Search opens in a new tab with pre-filled product name.</p>
      </div>

      {p?.details && (
        <div className="rounded-[24px] p-6 bg-[#F5F5F7] shadow-sm">
          <h3 className="text-lg font-semibold text-[#111111] mb-3">Product Details</h3>
          <pre className="text-sm text-[#6B6B6B] whitespace-pre-wrap font-sans">{typeof p.details === "string" ? p.details : JSON.stringify(p.details, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
