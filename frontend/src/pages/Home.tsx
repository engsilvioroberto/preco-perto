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
      <header className="home-header">
        <h1>🛒 PreçoPerto</h1>
        <p>Compare preços de mercados próximos</p>
      </header>

      {loading && <div className="loading">Obtendo localização...</div>}
      
      {error && (
        <div className="error-message">
          <p>⚠️ {error}</p>
          <p>Ative a localização para ver preços perto de você</p>
        </div>
      )}

      {latitude && longitude && (
        <div className="location-info">
          📍 Localização obtida
        </div>
      )}

      <div className="search-section">
        <h2>Buscar Produto</h2>
        <ProductSearch onSelect={handleProductSelect} />
      </div>

      <div className="quick-actions">
        <button onClick={() => navigate('/scan')} className="action-btn">
          📷 Escanear Nota Fiscal
        </button>
      </div>
    </div>
  );
};
