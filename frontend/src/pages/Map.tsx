
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPriceComparison } from '../services/api';
import { PriceMap } from '../components/PriceMap';
import { useGeolocation } from '../hooks/useGeolocation';
import type { PriceComparison } from '../types';

export const Map = () => {
  const { productId } = useParams<{ productId: string }>();
  const navigate = useNavigate();
  const { latitude, longitude } = useGeolocation();
  const [comparison, setComparison] = useState<PriceComparison | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (productId && latitude && longitude) {
      loadPrices();
    }
  }, [productId, latitude, longitude]);

  const loadPrices = async () => {
    if (!productId || !latitude || !longitude) return;

    setLoading(true);
    try {
      const data = await getPriceComparison(productId, latitude, longitude, 10);
      setComparison(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !latitude || !longitude) {
    return <div className="loading-page">Carregando mapa...</div>;
  }

  if (!comparison) {
    return <div className="empty-page">Nenhum dado encontrado</div>;
  }

  return (
    <div className="map-page">
      <header className="map-header">
        <button onClick={() => navigate(`/search/${productId}`)} className="btn-back">←</button>
        <h2>{comparison.product.name}</h2>
      </header>

      <PriceMap
        prices={comparison.prices}
        userLat={latitude}
        userLng={longitude}
      />

      <div className="map-legend">
        <p>{comparison.prices.length} mercados encontrados</p>
      </div>
    </div>
  );
};
