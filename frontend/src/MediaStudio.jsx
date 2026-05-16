import { useEffect, useState } from "react";
import { RefreshCw, Image, Zap } from "lucide-react";
import { useActiveProduct } from "./context/ProductContext";

const CATEGORY_MULTIPLIERS = {
  beauty: 1.2, makeup: 1.15, health: 1.1, home: 0.85, kitchen: 0.8,
  fashion: 0.9, fitness: 1.05, pet: 0.75, baby: 0.7, electronics: 1.5,
  garden: 0.65, general: 1.0,
};

function detectCategory(name = "", category = "") {
  const text = (name + " " + category).toLowerCase();
  for (const [cat] of Object.entries(CATEGORY_MULTIPLIERS)) {
    if (text.includes(cat)) return cat;
  }
  return "general";
}

export default function MediaStudio() {
  const { activeProduct, markSynced } = useActiveProduct();
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated] = useState(null);

  const product = activeProduct;
  const cat = detectCategory(product?.name, product?.category);
  const multiplier = CATEGORY_MULTIPLIERS[cat] || 1.0;

  useEffect(() => {
    if (product?.image) {
      setGenerating(true);
      setGenerated(null);
      const timer = setTimeout(() => {
        setGenerated({
          variations: [
            { id: 1, url: product.image, label: "Base", width: 400, height: 400 },
            { id: 2, url: product.image, label: "Square 1:1", width: 400, height: 400 },
            { id: 3, url: product.image, label: "Story 9:16", width: 360, height: 640 },
          ],
          prompt: `Generate ad creatives for ${product.name || "product"} — category: ${cat}`,
        });
        setGenerating(false);
        if (product.id) markSynced("media", product.id);
      }, 800);
      return () => clearTimeout(timer);
    }
  }, [product?.image, product?.name, product?.id, cat, markSynced]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold text-[#111111] tracking-tight">Media Studio</h1>
        <p className="text-[#6B6B6B] mt-1">AI-powered image and video generation for your active product.</p>
      </div>

      {!product?.id ? (
        <div className="rounded-[24px] p-12 bg-[#F5F5F7] shadow-sm flex flex-col items-center justify-center gap-4">
          <Image size={40} className="text-[#6B6B6B]" />
          <div className="text-center">
            <p className="text-base font-semibold text-[#111111]">No Product Selected</p>
            <p className="text-xs text-[#6B6B6B] mt-1">Search for a product in Product Research, then click View Source to activate it here.</p>
          </div>
        </div>
      ) : (
        <>
          <div className="rounded-[24px] p-6 bg-[#F5F5F7] shadow-sm">
            <div className="flex items-center gap-4 mb-4">
              {product.image && (
                <div className="w-16 h-16 rounded-xl overflow-hidden bg-white shadow-sm shrink-0">
                  <img src={product.image} alt={product.name} className="w-full h-full object-cover" />
                </div>
              )}
              <div>
                <h3 className="text-lg font-semibold text-[#111111]">{product.name}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-[#6B6B6B]">${product.price}</span>
                  <span className="w-1 h-1 rounded-full bg-gray-300" />
                  <span className="text-xs text-[#6B6B6B] capitalize">{cat}</span>
                  <span className="w-1 h-1 rounded-full bg-gray-300" />
                  <span className="text-xs text-[#6B6B6B]">Multiplier: {multiplier}x</span>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-[24px] p-6 bg-[#F5F5F7] shadow-sm">
            <h3 className="text-lg font-semibold text-[#111111] mb-4">AI Generation</h3>
            {generating ? (
              <div className="flex flex-col items-center justify-center py-8 gap-3">
                <RefreshCw size={24} className="text-[#2563EB] animate-spin" />
                <p className="text-sm text-[#6B6B6B]">Generating creatives for {product.name}...</p>
              </div>
            ) : generated ? (
              <div className="space-y-4">
                <div className="text-xs text-[#6B6B6B] bg-white rounded-xl p-3">{generated.prompt}</div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {generated.variations.map((v) => (
                    <div key={v.id} className="rounded-2xl bg-white shadow-sm overflow-hidden">
                      <div className="aspect-square bg-[#F5F5F7] flex items-center justify-center p-4">
                        <img src={v.url} alt={v.label} className="max-h-full max-w-full object-contain" />
                      </div>
                      <div className="px-4 py-2 flex items-center justify-between">
                        <span className="text-xs font-medium text-[#111111]">{v.label}</span>
                        <span className="text-[10px] text-[#6B6B6B]">{v.width}×{v.height}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        </>
      )}
    </div>
  );
}
