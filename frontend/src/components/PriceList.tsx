import { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import type { MarketPrice } from '../types';

interface PriceListProps {
  prices: MarketPrice[];
  onViewMap: () => void;
}

export const PriceList = ({ prices, onViewMap }: PriceListProps) => {
  const listRef = useRef<HTMLDivElement>(null);

  // Animate market cards on mount
  useGSAP(() => {
    if (listRef.current) {
      gsap.from(listRef.current.querySelectorAll('.market-item'), {
        opacity: 0,
        y: 16,
        duration: 0.4,
        stagger: 0.08,
        ease: 'power2.out',
      });
    }
  }, { dependencies: [prices.length], scope: listRef });

  if (prices.length === 0) {
    return <div className="empty-page">Nenhum preço encontrado</div>;
  }

  const cheapest = prices[0];
  const mostExpensive = prices[prices.length - 1];

  return (
    <div className="price-list">
      <div className="price-list-header">
        <h3>{prices.length} mercados encontrados</h3>
        <button onClick={onViewMap} className="btn-map">
          🗺️ Mapa
        </button>
      </div>

      <div className="markets-list" ref={listRef}>
        {prices.map((market, index) => {
          const isCheapest = index === 0;
          const savings = market.price - cheapest.price;
          const diffPercent = mostExpensive.price > 0
            ? Math.round(((market.price - cheapest.price) / cheapest.price) * 100)
            : 0;

          return (
            <div key={market.market_id} className="market-item">
              <div className="market-top">
                <div>
                  <div className="market-name">{market.market_name}</div>
                  <div className="market-address">{market.market_address}</div>
                </div>
                <div className="market-price-col">
                  <div className={`price ${isCheapest ? 'green' : ''}`}>
                    R$ {market.price.toFixed(2)}
                  </div>
                  {isCheapest && <span className="badge cheapest">💰 Melhor preço</span>}
                  {!isCheapest && diffPercent > 0 && (
                    <span className="badge worth-it">📈 +{diffPercent}%</span>
                  )}
                </div>
              </div>

              <div className="market-distance">
                <span>📍 {market.distance_km.toFixed(1)} km</span>
                {market.is_promotion && market.original_price && (
                  <>
                    <span className="savings">
                      🔥 De <s style={{color:'var(--text-muted)'}}>R$ {market.original_price.toFixed(2)}</s>
                    </span>
                  </>
                )}
                {!isCheapest && savings > 0 && (
                  <span className="savings" style={{ marginLeft: 'auto' }}>
                    Economia de R$ {Math.abs(savings).toFixed(2)}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
