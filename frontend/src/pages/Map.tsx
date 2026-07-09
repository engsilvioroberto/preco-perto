
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPriceComparison } from '../services/api';
import { PriceMap } from '../components/PriceMap';
import { useGeolocation } from '../hooks/useGeolocation';
import type { PriceComparison } from '../types';

// Default location: Belo Horizonte center (used when user denies geolocation)
const DEFAULT_LOCATION = { lat: -19.928, lng: -43.939 };

export const Map = () => {
  const { productId } = useParams<{ productId: string }>();
  const navigate = useNavigate();
  const geo = useGeolocation();
  const [comparison, setComparison] = useState<PriceComparison | null>(null);
  const [loading, setLoading] = useState(true);

  // Use geolocation if available, otherwise fall back to default
  const latitude = geo.latitude ?? DEFAULT_LOCATION.lat;
  const longitude = geo.longitude ?? DEFAULT_LOCATION.lng;
  const geoError = geo.error;

  useEffect(() => {
    if (productId) {
      loadPrices();
    }
  }, [productId, latitude, longitude]);

  const loadPrices = async () => {
    if (!productId) return;

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

  if (loading) {
    return <div className="loading-page">Carregando mapa...</div>;
  }

  if (!comparison || comparison.total_markets === 0) {
    return (
      <div className="empty-page">
        <p>Nenhum dado encontrado</p>
        <button onClick={() => navigate('/')} className="btn-back">← Voltar</button>
      </div>
    );
  }

  return (
    <div className="map-page">
      <header className="map-header">
        <button onClick={() => navigate(`/search/${productId}`)} className="btn-back">←</button>
        <h2>{comparison.product.name}</h2>
      </header>

      {geoError && (
        <div className="location-note">
          📍 Mostrando preços para a região de Belo Horizonte (localização não obtida)
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
