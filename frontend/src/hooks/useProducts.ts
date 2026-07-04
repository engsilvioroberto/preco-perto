import { useState, useEffect, useCallback } from 'react';
import type { Product } from '../types';
import { searchProducts } from '../services/api';

export function useProducts(query: string, debounceMs: number = 300) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setProducts([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const results = await searchProducts(searchQuery);
      setProducts(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao buscar produtos');
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      search(query);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [query, debounceMs, search]);

  return { products, loading, error };
}
