import type { Market } from '../types';

interface MarketCardProps {
  market: Market;
  onClick?: () => void;
}

export const MarketCard = ({ market, onClick }: MarketCardProps) => {
  return (
    <div className="market-card" onClick={onClick}>
      <div className="market-card-header">
        <h3>{market.name}</h3>
        {market.distance_km !== undefined && (
          <span className="distance">{market.distance_km} km</span>
        )}
      </div>
      <div className="market-card-body">
        <p>{market.address}</p>
        {market.neighborhood && (
          <p className="neighborhood">{market.neighborhood}</p>
        )}
      </div>
      {market.categories && market.categories.length > 0 && (
        <div className="market-card-footer">
          {market.categories.map((cat) => (
            <span key={cat} className="category-tag">{cat}</span>
          ))}
        </div>
      )}
    </div>
  );
};
