
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPriceComparison } from '../services/api';
import { PriceMap } from '../components/PriceMap';
import { useGeolocation } from '../hooks/useGeolocation';
import type { PriceComparison } from '../types';

export const Map = () => {
  const { productId } = useParams<{ productId: string }>();
  const navigate = useNavigate();
  const { latitude: geoLat, longitude: geoLng, error: geoError, loading: geoLoading } = useGeolocation();
  
  const latitude = geoLat !== null ? geoLat : (geoLoading ? null : -21.1767);
  const longitude = geoLng !== null ? geoLng : (geoLoading ? null : -47.8208);

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

      {geoError && (
        <div className="location-warning-banner" style={{ backgroundColor: '#fff3cd', color: '#856404', padding: '10px', textAlign: 'center', fontSize: '14px', borderRadius: '4px', margin: '10px', zIndex: 1000, position: 'relative' }}>
          ⚠️ Usando localização padrão (Ribeirão Preto). Ative o GPS para ver preços na sua região.
        </div>
      )}

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
