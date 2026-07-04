import { useState, useEffect } from 'react';
import type { PriceComparison } from '../types';
import { getPriceComparison } from '../services/api';

export function usePrices(productId: string | null, latitude?: number, longitude?: number) {
  const [comparison, setComparison] = useState<PriceComparison | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!productId || !latitude || !longitude) {
      setComparison(null);
      return;
    }

    const fetchPrices = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getPriceComparison(productId, latitude, longitude);
        setComparison(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao buscar preços');
        setComparison(null);
      } finally {
        setLoading(false);
      }
    };

    fetchPrices();
  }, [productId, latitude, longitude]);

  return { comparison, loading, error };
}
