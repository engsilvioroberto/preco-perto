import { useState, useEffect, useRef } from 'react';
import { searchProducts } from '../services/api';
import type { Product } from '../types';

interface ProductSearchProps {
  onSelect: (product: Product) => void;
}

const productEmoji = (name: string): string => {
  const lower = name.toLowerCase();
  if (lower.includes('arroz')) return '🍚';
  if (lower.includes('feijão') || lower.includes('feijao')) return '🥫';
  if (lower.includes('leite')) return '🥛';
  if (lower.includes('café') || lower.includes('cafe')) return '☕';
  if (lower.includes('açúcar') || lower.includes('acucar')) return '🍬';
  if (lower.includes('óleo') || lower.includes('oleo')) return '🫒';
  if (lower.includes('coca') || lower.includes('refri')) return '🥤';
  if (lower.includes('pão') || lower.includes('pao')) return '🍞';
  if (lower.includes('manteiga') || lower.includes('margarina')) return '🧈';
  if (lower.includes('detergente')) return '🧴';
  if (lower.includes('tomate')) return '🍅';
  return '📦';
};

export const ProductSearch = ({ onSelect }: ProductSearchProps) => {
  const [query, setQuery] = useState('');
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (query.length < 2) {
      setProducts([]);
      return;
    }
    setSelected(false);

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

  // Fechar dropdown ao clicar fora
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setProducts([]);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleSelect = (product: Product) => {
    setSelected(true);
    onSelect(product);
  };

  const hasResults = products.length > 0 && query.length >= 2 && !selected;

  return (
    <div className="product-search" ref={wrapperRef} style={{ flex: 1, position: 'relative' }}>
      <input
        type="text"
        placeholder="Buscar produto..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="search-input"
        style={{ border: 'none', padding: '10px 0', background: 'transparent', width: '100%', outline: 'none', fontSize: 15 }}
      />

      {/* Loading indicator inline */}
      {loading && query.length >= 2 && !hasResults && (
        <div style={{ position: 'absolute', top: '100%', left: -16, right: -4, padding: '16px', textAlign: 'center', fontSize: 14, color: 'var(--text-soft)', background: 'white', borderRadius: 12, boxShadow: '0 8px 30px rgba(0,0,0,0.1)', border: '1px solid rgba(0,0,0,0.06)', marginTop: 8, zIndex: 20 }}>
          Buscando...
        </div>
      )}

      {/* Results dropdown */}
      {hasResults && (
        <div style={{ position: 'absolute', top: '100%', left: -16, right: -4, zIndex: 20, background: 'white', borderRadius: 12, boxShadow: '0 8px 30px rgba(0,0,0,0.1)', border: '1px solid rgba(0,0,0,0.06)', marginTop: 8, padding: 8, maxHeight: 320, overflowY: 'auto' }} className="search-dropdown">
          {products.map((product) => (
            <div
              key={product.id}
              onClick={() => handleSelect(product)}
              style={{
                display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px',
                borderRadius: 8, cursor: 'pointer', transition: 'background 0.15s',
              }}
              className="product-search-item"
              onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
            >
              <div style={{ width: 36, height: 36, borderRadius: 8, background: 'var(--bg)', border: '1px solid rgba(0,0,0,0.04)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, flexShrink: 0 }}>
                {productEmoji(product.name)}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 14, fontWeight: 600 }}>{product.name}</div>
                <div style={{ fontSize: 12, color: 'var(--text-soft)', marginTop: 1 }}>
                  {product.brand || product.category || 'Produto'}
                </div>
              </div>
              <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--accent)', background: 'var(--accent-soft)', padding: '2px 8px', borderRadius: 9999, whiteSpace: 'nowrap' }}>
                Ver preços →
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
