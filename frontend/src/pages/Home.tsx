import { useNavigate } from 'react-router-dom';
import { ProductSearch } from '../components/ProductSearch';
import { useGeolocation } from '../hooks/useGeolocation';
import type { Product } from '../types';

export const Home = () => {
  const navigate = useNavigate();
  const { latitude, longitude, error, loading } = useGeolocation();

  const handleProductSelect = (product: Product) => {
    navigate(`/search/${product.id}`);
  };

  return (
    <div className="home-page">
      {/* Hero */}
      <div className="home-hero">
        <div className="hero-badge">
          <span className="dot"></span>
          Economize nas compras
        </div>
        <h1>Preço certo,<br /><span>perto de você</span></h1>
        <p>Compare preços em tempo real entre os mercados da sua região.</p>
      </div>

      {/* Search — auto-busca enquanto digita */}
      <div className="search-section">
        <div className="search-wrapper">
          <span className="search-icon">🔍</span>
          <ProductSearch onSelect={handleProductSelect} />
        </div>
      </div>

      {/* Status messages */}
      <div>
        {loading && <div className="loading">📍 Obtendo localização...</div>}
        {error && (
          <div className="error-message">
            <p>⚠️ {error}</p>
            <p>Usando localização aproximada (BH)</p>
          </div>
        )}
        {latitude && longitude && !error && (
          <div className="location-info">
            📍 Localização obtida
          </div>
        )}
      </div>

      {/* Quick actions */}
      <div className="quick-actions">
        <button onClick={() => navigate('/scan')} className="action-btn">
          <div className="action-icon">📷</div>
          <div className="action-text">
            Escanear Nota Fiscal
            <p>Adicione produtos escaneando sua nota</p>
          </div>
          <div className="action-arrow">→</div>
        </button>
      </div>
    </div>
  );
};
