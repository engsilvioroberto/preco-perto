
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPriceComparison } from '../services/api';
import { PriceList } from '../components/PriceList';
import { useGeolocation } from '../hooks/useGeolocation';
import type { PriceComparison } from '../types';

// Default location: Belo Horizonte center (used when user denies geolocation)
const DEFAULT_LOCATION = { lat: -19.928, lng: -43.939 };

export const Search = () => {
  const { productId } = useParams<{ productId: string }>();
  const navigate = useNavigate();
  const geo = useGeolocation();
  const [comparison, setComparison] = useState<PriceComparison | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Use geolocation if available, otherwise fall back to default
  const latitude = geo.latitude ?? DEFAULT_LOCATION.lat;
  const longitude = geo.longitude ?? DEFAULT_LOCATION.lng;

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
      setError('Erro ao carregar preços');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading-page">Carregando preços...</div>;
  }

  if (error) {
    return <div className="error-page">{error}</div>;
  }

  if (!comparison || comparison.total_markets === 0) {
    return (
      <div className="empty-page">
        <p>Nenhum preço encontrado para este produto.</p>
        <button onClick={() => navigate('/')} className="btn-back">← Voltar</button>
      </div>
    );
  }

  return (
    <div className="search-page">
      <header className="search-header">
        <button onClick={() => navigate('/')} className="btn-back">←</button>
        <h2>{comparison.product.name}</h2>
      </header>

      <div className="price-summary">
        <div className="summary-item">
          <span className="label">Mais barato</span>
          <span className="value">R$ {comparison.cheapest_price.toFixed(2)}</span>
        </div>
        <div className="summary-item">
          <span className="label">Mais caro</span>
          <span className="value">R$ {comparison.most_expensive_price.toFixed(2)}</span>
        </div>
        <div className="summary-item">
          <span className="label">Média</span>
          <span className="value">R$ {comparison.average_price.toFixed(2)}</span>
        </div>
      </div>

      <PriceList
        prices={comparison.prices}
        onViewMap={() => navigate(`/map/${productId}`)}
      />
    </div>
  );
};
