import type { MarketPrice } from '../types';

interface PriceListProps {
  prices: MarketPrice[];
  onViewMap: () => void;
}

export const PriceList = ({ prices, onViewMap }: PriceListProps) => {
  if (prices.length === 0) {
    return <div className="empty-state">Nenhum preço encontrado</div>;
  }

  const cheapest = prices[0];

  return (
    <div className="price-list">
      <div className="price-list-header">
        <h3>{prices.length} mercados encontrados</h3>
        <button onClick={onViewMap} className="btn-map">
          🗺️ Ver no mapa
        </button>
      </div>
      
      <ul className="markets-list">
        {prices.map((market, index) => {
          const isCheapest = index === 0;
          const savings = market.price - cheapest.price;
          
          return (
            <li key={market.market_id} className="market-item">
              {isCheapest && <span className="badge cheapest">Mais barato</span>}
              
              <div className="market-info">
                <div className="market-name">{market.market_name}</div>
                <div className="market-address">{market.market_address}</div>
                <div className="market-distance">{market.distance_km} km</div>
              </div>
              
              <div className="market-price">
                <div className="price">R$ {market.price.toFixed(2)}</div>
                {market.is_promotion && market.original_price && (
                  <div className="original-price">
                    R$ {market.original_price.toFixed(2)}
                  </div>
                )}
              </div>
              
              {market.cost_benefit && savings > 0 && (
                <div className="cost-benefit">
                  <div className="savings">
                    Economia: R$ {savings.toFixed(2)}
                  </div>
                  {market.cost_benefit.worth_it_walking && (
                    <span className="badge worth-it">Vale a pena!</span>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
};
