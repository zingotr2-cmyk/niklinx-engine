import { useState, useEffect, useRef } from "react";

export default function StatCard({ icon: Icon, label, value, prefix = "", suffix = "", trend, trendUp, color = "#2563EB" }) {
  const [display, setDisplay] = useState(0);
  const ref = useRef(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([e]) => {
        if (!e.isIntersecting) return;
        const num = typeof value === "number" ? value : parseFloat(String(value).replace(/[^0-9.-]/g, "")) || 0;
        let cur = 0;
        const step = Math.max(1, Math.ceil(num / 40));
        const t = setInterval(() => {
          cur += step;
          if (cur >= num) { cur = num; clearInterval(t); }
          setDisplay(cur);
        }, 20);
        obs.disconnect();
      },
      { threshold: 0.3 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [value]);

  const fmt = (v) => {
    if (typeof value === "string") return value;
    if (v >= 1_000_000) return (v / 1_000_000).toFixed(1) + "M";
    if (v >= 1_000) return (v / 1_000).toFixed(1) + "K";
    return Math.round(v).toLocaleString();
  };

  return (
    <div ref={ref} className="relative overflow-hidden rounded-[24px] p-6 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg bg-[#F5F5F7] shadow-sm">
      <div className="flex items-start justify-between mb-4">
        <div className="p-2.5 rounded-xl" style={{ backgroundColor: `${color}15` }}>
          <Icon size={20} color={color} />
        </div>
        {trend !== undefined && (
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${trendUp ? "text-green-700 bg-green-50" : "text-red-700 bg-red-50"}`}>
            {trendUp ? "+" : ""}{trend}%
          </span>
        )}
      </div>
      <div className="text-3xl font-semibold text-[#111111] tracking-tight">{prefix}{fmt(display)}{suffix}</div>
      <div className="text-sm text-[#6B6B6B] mt-1">{label}</div>
    </div>
  );
}
