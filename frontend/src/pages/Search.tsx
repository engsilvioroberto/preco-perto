
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPriceComparison } from '../services/api';
import { PriceList } from '../components/PriceList';
import { useGeolocation } from '../hooks/useGeolocation';
import type { PriceComparison } from '../types';

export const Search = () => {
  const { productId } = useParams<{ productId: string }>();
  const navigate = useNavigate();
  const { latitude: geoLat, longitude: geoLng, error: geoError, loading: geoLoading } = useGeolocation();
  
  const latitude = geoLat !== null ? geoLat : (geoLoading ? null : -21.1767);
  const longitude = geoLng !== null ? geoLng : (geoLoading ? null : -47.8208);

  const [comparison, setComparison] = useState<PriceComparison | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  if (!comparison) {
    return <div className="empty-page">Nenhum dado encontrado</div>;
  }

  return (
    <div className="search-page">
      <header className="search-header">
        <button onClick={() => navigate('/')} className="btn-back">←</button>
        <h2>{comparison.product.name}</h2>
      </header>

      {geoError && (
        <div className="location-warning-banner" style={{ backgroundColor: '#fff3cd', color: '#856404', padding: '10px', textAlign: 'center', fontSize: '14px', borderRadius: '4px', margin: '10px' }}>
          ⚠️ Usando localização padrão (Ribeirão Preto). Ative o GPS para ver preços na sua região.
        </div>
      )}

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
