import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

export interface Product {
  id: string;
  url: string;
  name: string;
  price: number;
  image: string;
  category: string;
}

export interface AnalyticsData {
  total_orders: number;
  total_revenue: number;
  conversion_rate: number;
  avg_order_value: number;
  top_category: string;
  growth_percentage: number;
  weekly_growth_pct: number;
  monthly_growth_pct: number;
  growth_direction: "up" | "down" | "stable";
  total_traffic: number;
  total_products_analyzed: number;
  review_velocity: number;
  categories: CategoryData[];
  top_products: ProductPerformance[];
  customer_insights: CustomerInsights;
  active_product: ActiveProductData | null;
}

export interface CategoryData {
  name: string;
  product_count: number;
  total_sales: number;
  total_traffic: number;
  market_share: number;
}

export interface ProductPerformance {
  id: string;
  name: string;
  price: number;
  rating: number;
  reviews: number;
  category: string;
  estimated_monthly_sales: number;
  estimated_monthly_traffic: number;
}

export interface CustomerInsights {
  avg_rating: number;
  total_reviews: number;
  avg_reviews_per_product: number;
  repeat_rate: number;
  top_category: string;
}

export interface ActiveProductData {
  id: string;
  name: string;
  price: number;
  category: string;
  projected_orders: number;
  projected_revenue: number;
  competitor_count: number;
  estimated_market_size: number;
  estimated_traffic: number;
  avg_competitor_rating: number;
  profit_margin: number;
}

export interface AnalyticsState {
  data: AnalyticsData | null;
  loading: boolean;
  error: string | null;
  lastUpdated: number | null;
  isStale: boolean;
}

export interface AnalyticsResponse {
  success: boolean;
  data: AnalyticsData;
  meta: {
    product_id: string | null;
    timestamp: string;
    source: string;
  };
}

interface ProductContextType {
  activeProduct: Product | null;
  setActiveProduct: (product: Product | null) => void;
  syncedModules: Record<string, string>;
  markSynced: (moduleName: string, productId: string) => void;
}

const ProductContext = createContext<ProductContextType | null>(null);

export function ProductProvider({ children }: { children: ReactNode }) {
  const [activeProduct, setActiveProductState] = useState<Product | null>(null);
  const [syncedModules, setSyncedModules] = useState<Record<string, string>>({});

  const setActiveProduct = useCallback((product: Product | null) => {
    setActiveProductState(product);
    setSyncedModules({});
  }, []);

  const markSynced = useCallback((moduleName: string, productId: string) => {
    setSyncedModules((prev) => ({ ...prev, [moduleName]: productId }));
  }, []);

  return (
    <ProductContext.Provider value={{ activeProduct, setActiveProduct, syncedModules, markSynced }}>
      {children}
    </ProductContext.Provider>
  );
}

export function useActiveProduct(): ProductContextType {
  const ctx = useContext(ProductContext);
  if (!ctx) {
    throw new Error("useActiveProduct must be used within a <ProductProvider>");
  }
  return ctx;
}
