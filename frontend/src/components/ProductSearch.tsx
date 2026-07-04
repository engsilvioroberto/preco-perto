import { useState, useEffect } from 'react';
import { searchProducts } from '../services/api';
import type { Product } from '../types';

interface ProductSearchProps {
  onSelect: (product: Product) => void;
}

export const ProductSearch = ({ onSelect }: ProductSearchProps) => {
  const [query, setQuery] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (query.length < 2) {
      setProducts([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const results = await searchProducts(query, 10);
        setProducts(results);
      } catch (error) {
        console.error('Erro ao buscar produtos:', error);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="product-search">
      <input
        type="text"
        placeholder="Buscar produto..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="search-input"
      />
      
      {loading && <div className="loading">Buscando...</div>}
      
      {products.length > 0 && (
        <ul className="product-list">
          {products.map((product) => (
            <li
              key={product.id}
              onClick={() => onSelect(product)}
              className="product-item"
            >
              <div className="product-name">{product.name}</div>
              {product.category && (
                <div className="product-category">{product.category}</div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
