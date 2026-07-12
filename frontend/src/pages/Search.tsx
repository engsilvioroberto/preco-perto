
import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getPriceComparison } from '../services/api';
import { PriceList } from '../components/PriceList';
import { useGeolocation } from '../hooks/useGeolocation';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import type { PriceComparison } from '../types';

const DEFAULT_LOCATION = { lat: -19.928, lng: -43.939 };

export const Search = () => {
  const { productId } = useParams<{ productId: string }>();
  const navigate = useNavigate();
  const geo = useGeolocation();
  const [comparison, setComparison] = useState<PriceComparison | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const summaryRef = useRef<HTMLDivElement>(null);

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

  // Animate summary cards
  useGSAP(() => {
    if (comparison && summaryRef.current) {
      gsap.from(summaryRef.current.querySelectorAll('.summary-item'), {
        opacity: 0,
        y: 12,
        duration: 0.4,
        stagger: 0.08,
        ease: 'power2.out',
      });
    }
  }, { dependencies: [comparison?.total_markets], scope: summaryRef });

  if (loading) {
    return (
      <div className="loading-page">
        <div className="spinner"></div>
        <p>Carregando preços...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-page">
        <p>⚠️ {error}</p>
        <button onClick={() => navigate('/')} className="btn-primary" style={{ marginTop: 12, maxWidth: 200 }}>
          ← Voltar
        </button>
      </div>
    );
  }

  if (!comparison || comparison.total_markets === 0) {
    return (
      <div className="empty-page">
        <p>Nenhum preço encontrado para este produto.</p>
        <button onClick={() => navigate('/')} className="btn-primary" style={{ marginTop: 12, maxWidth: 200 }}>
          ← Voltar
        </button>
      </div>
    );
  }

  return (
    <div className="search-page">
      <header className="search-header">
        <button onClick={() => navigate('/')} className="btn-back">←</button>
        <h2>{comparison.product.name}</h2>
      </header>

      {geo.error && (
        <div className="location-note">
          📍 Mostrando preços para região de Belo Horizonte
        </div>
      )}

      <div className="price-summary" ref={summaryRef}>
        <div className="summary-item">
          <span className="label">Menor preço</span>
          <span className="value green">R$ {comparison.cheapest_price.toFixed(2)}</span>
        </div>
        <div className="summary-item">
          <span className="label">Preço médio</span>
          <span className="value">R$ {comparison.average_price.toFixed(2)}</span>
        </div>
        <div className="summary-item">
          <span className="label">Maior preço</span>
          <span className="value gold">R$ {comparison.most_expensive_price.toFixed(2)}</span>
        </div>
      </div>

      <PriceList
        prices={comparison.prices}
        onViewMap={() => navigate(`/map/${productId}`)}
      />
    </div>
  );
};
