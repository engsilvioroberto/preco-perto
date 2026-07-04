import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import type { MarketPrice } from '../types';
import 'leaflet/dist/leaflet.css';

interface PriceMapProps {
  prices: MarketPrice[];
  userLat: number;
  userLng: number;
}

export const PriceMap = ({ prices, userLat, userLng }: PriceMapProps) => {
  return (
    <MapContainer
      center={[userLat, userLng]}
      zoom={13}
      style={{ height: '400px', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />
      
      {prices.map((market) => (
        <Marker
          key={market.market_id}
          position={[market.market_latitude, market.market_longitude]}
        >
          <Popup>
            <div className="market-popup">
              <h4>{market.market_name}</h4>
              <p className="popup-price">R$ {market.price.toFixed(2)}</p>
              <p className="popup-distance">{market.distance_km} km</p>
              {market.cost_benefit?.worth_it_walking && (
                <p className="popup-worth">✓ Vale a pena!</p>
              )}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};
