
export interface Product {
  id: string;
  name: string;
  normalized_name: string;
  category?: string;
  unit?: string;
  quantity?: number;
  brand?: string;
  image_url?: string;
}

export interface Market {
  id: string;
  name: string;
  address: string;
  neighborhood?: string;
  latitude: number;
  longitude: number;
  distance_km?: number;
  opening_hours?: Record<string, any>;
  categories?: string[];
}

export interface Price {
  id: string;
  product_id: string;
  market_id: string;
  price: number;
  original_price?: number;
  is_promotion: boolean;
  promotion_ends_at?: string;
  source: string;
  captured_at: string;
}

export interface MarketPrice {
  market_id: string;
  market_name: string;
  market_address: string;
  market_neighborhood?: string;
  market_latitude: number;
  market_longitude: number;
  price: number;
  original_price?: number;
  is_promotion: boolean;
  promotion_ends_at?: string;
  distance_km: number;
  captured_at: string;
  source: string;
  cost_benefit?: {
    savings_vs_most_expensive: number;
    most_expensive_price: number;
    most_expensive_market: string;
    transport_cost_walking: number;
    transport_cost_car: number;
    transport_cost_bus: number;
    worth_it_walking: boolean;
    worth_it_car: boolean;
    worth_it_bus: boolean;
  };
}

export interface PriceComparison {
  product: Product;
  prices: MarketPrice[];
  cheapest_price: number;
  most_expensive_price: number;
  average_price: number;
  total_markets: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
  is_admin: boolean;
}
