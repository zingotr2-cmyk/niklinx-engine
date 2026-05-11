import { useState, useEffect, useRef } from "react";

export default function ProgressRing({ value = 0, size = 120, strokeWidth = 6, label, sublabel, color = "#2563EB" }) {
  const [animated, setAnimated] = useState(0);
  const ref = useRef(null);
  const r = (size - strokeWidth) / 2;
  const c = 2 * Math.PI * r;
  const offset = c - (animated / 100) * c;

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([e]) => {
        if (!e.isIntersecting) return;
        let cur = 0;
        const step = Math.ceil(value / 30);
        const t = setInterval(() => {
          cur += step;
          if (cur >= value) { cur = value; clearInterval(t); }
          setAnimated(cur);
        }, 30);
        obs.disconnect();
      },
      { threshold: 0.3 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [value]);

  return (
    <div ref={ref} className="flex flex-col items-center justify-center relative">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#E5E7EB" strokeWidth={strokeWidth} />
        <circle
          cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={strokeWidth}
          strokeDasharray={c} strokeDashoffset={offset} strokeLinecap="round"
          className="transition-all duration-500 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-semibold text-[#111111]">{animated}%</span>
        {label && <span className="text-xs text-[#6B6B6B] mt-0.5">{label}</span>}
      </div>
      {sublabel && <span className="text-sm text-[#6B6B6B] mt-2">{sublabel}</span>}
    </div>
  );
}
