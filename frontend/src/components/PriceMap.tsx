import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import type { MarketPrice } from '../types';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet marker icon under Vite bundling
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

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

      {prices.map((market) => {
        const cb = market.cost_benefit;
        const savings = cb ? cb.savings_vs_most_expensive : 0;

        return (
          <Marker
            key={market.market_id}
            position={[market.market_latitude, market.market_longitude]}
          >
            <Popup>
              <div className="market-popup">
                <h4>{market.market_name}</h4>
                <p className="popup-price">R$ {market.price.toFixed(2)}</p>
                <p className="popup-distance">{market.distance_km} km</p>
                {market.is_stale && (
                  <p className="popup-stale">
                    Preço de {new Date(market.captured_at).toLocaleDateString('pt-BR')}
                  </p>
                )}
                {cb && (
                  <>
                    {savings > 0 && (
                      <p className="popup-savings">
                        Economia: R$ {savings.toFixed(2)}
                      </p>
                    )}
                    <p className="popup-worth">
                      🚶 {cb.worth_it_walking ? 'Vale a pena a pé' : 'A pé não compensa'}
                    </p>
                    <p className="popup-worth">
                      🚗 {cb.worth_it_car ? 'Vale a pena de carro' : 'De carro não compensa'}
                    </p>
                  </>
                )}
              </div>
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
};
