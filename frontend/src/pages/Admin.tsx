import { useState, useEffect, type FormEvent } from 'react';
import { uploadOfferFlyer, createMarket, listMarkets } from '../services/api';
import type { Market, OfferFlyerItem } from '../types';

export const Admin = () => {
  const [tab, setTab] = useState<'flyer' | 'market'>('flyer');
  const [markets, setMarkets] = useState<Market[]>([]);
  useEffect(() => {
    listMarkets()
      .then(setMarkets)
      .catch(() => {});
  }, []);

  return (
    <div className="admin-page">
      <header className="admin-header">
        <h2>Painel Admin</h2>
      </header>

      <div className="admin-tabs">
        <button
          className={tab === 'flyer' ? 'tab-active' : ''}
          onClick={() => setTab('flyer')}
        >
          Jornal de Ofertas
        </button>
        <button
          className={tab === 'market' ? 'tab-active' : ''}
          onClick={() => setTab('market')}
        >
          Novo Mercado
        </button>
      </div>

      {tab === 'flyer' ? (
        <OfferFlyerTab markets={markets} />
      ) : (
        <CreateMarketTab />
      )}
    </div>
  );
};

function OfferFlyerTab({ markets }: { markets: Market[] }) {
  const [file, setFile] = useState<File | null>(null);
  const [marketId, setMarketId] = useState('');
  const [validFrom, setValidFrom] = useState('');
  const [validUntil, setValidUntil] = useState('');
  const [uploading, setUploading] = useState(false);
  const [items, setItems] = useState<OfferFlyerItem[]>([]);
  const [flyerId, setFlyerId] = useState<string | null>(null);

  const handleUpload = async (e: FormEvent) => {
    e.preventDefault();
    if (!file || !marketId || !validFrom || !validUntil) return;

    setUploading(true);
    try {
      const result = await uploadOfferFlyer({
        image: file,
        marketId,
        validFrom,
        validUntil,
      });
      setFlyerId(result.offer_flyer_id);
      setItems(result.items || []);
    } catch {
      alert('Erro ao enviar jornal');
    } finally {
      setUploading(false);
    }
  };

  const handleConfirm = async () => {
    if (!flyerId) return;
    const { confirmOfferFlyerItems } = await import('../services/api');
    try {
      const confirmItems = items.map(item => ({
        item_id: item.id,
        product_id: item.product_id || '',
        is_confirmed: true,
      })).filter(i => i.product_id);

      const result = await confirmOfferFlyerItems(flyerId, confirmItems);
      alert(result.message);
      setFlyerId(null);
      setItems([]);
      setFile(null);
    } catch {
      alert('Erro ao confirmar itens');
    }
  };

  return (
    <div className="admin-section">
      <h3>Upload Jornal de Ofertas</h3>

      {items.length === 0 ? (
        <form onSubmit={handleUpload} className="upload-form">
          <input
            type="file"
            accept="image/*,.pdf"
            onChange={e => setFile(e.target.files?.[0] || null)}
            required
          />
          <select
            value={marketId}
            onChange={e => setMarketId(e.target.value)}
            required
          >
            <option value="">Selecione o mercado</option>
            {markets.map(m => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
          <label>Válido de:
            <input type="date" value={validFrom} onChange={e => setValidFrom(e.target.value)} required />
          </label>
          <label>Válido até:
            <input type="date" value={validUntil} onChange={e => setValidUntil(e.target.value)} required />
          </label>
          <button type="submit" disabled={uploading} className="btn-primary">
            {uploading ? 'Processando OCR...' : 'Enviar Jornal'}
          </button>
        </form>
      ) : (
        <div className="flyer-review">
          <h4>{items.length} itens extraídos</h4>
          <ul className="flyer-items">
            {items.map(item => (
              <li key={item.id} className="flyer-item">
                <div className="item-info">
                  <span className="item-desc">{item.description}</span>
                  <span className="item-price">R$ {item.price.toFixed(2)}</span>
                  {item.confidence && (
                    <span className="item-confidence">
                      Confiança: {item.confidence.toFixed(0)}%
                    </span>
                  )}
                  {item.product_name && (
                    <span className="item-match">→ {item.product_name}</span>
                  )}
                </div>
              </li>
            ))}
          </ul>
          <button onClick={handleConfirm} className="btn-primary">
            Confirmar Itens
          </button>
        </div>
      )}
    </div>
  );
}

function CreateMarketTab() {
  const [name, setName] = useState('');
  const [cnpj, setCnpj] = useState('');
  const [address, setAddress] = useState('');
  const [neighborhood, setNeighborhood] = useState('');
  const [city, setCity] = useState('Ribeirão Preto');
  const [state, setState] = useState('SP');
  const [zipcode, setZipcode] = useState('');
  const [phone, setPhone] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createMarket({ name, cnpj: cnpj || undefined, address, neighborhood: neighborhood || undefined, city, state, zipcode: zipcode || undefined, phone: phone || undefined });
      alert('Mercado cadastrado com sucesso!');
      setName(''); setCnpj(''); setAddress(''); setNeighborhood(''); setZipcode(''); setPhone('');
    } catch {
      alert('Erro ao cadastrar mercado');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="admin-section">
      <h3>Cadastrar Mercado</h3>
      <form onSubmit={handleSubmit} className="upload-form">
        <input placeholder="Nome" value={name} onChange={e => setName(e.target.value)} required />
        <input placeholder="CNPJ" value={cnpj} onChange={e => setCnpj(e.target.value)} />
        <input placeholder="Endereço" value={address} onChange={e => setAddress(e.target.value)} required />
        <input placeholder="Bairro" value={neighborhood} onChange={e => setNeighborhood(e.target.value)} />
        <input placeholder="Cidade" value={city} onChange={e => setCity(e.target.value)} />
        <input placeholder="Estado" value={state} onChange={e => setState(e.target.value)} />
        <input placeholder="CEP" value={zipcode} onChange={e => setZipcode(e.target.value)} />
        <input placeholder="Telefone" value={phone} onChange={e => setPhone(e.target.value)} />
        <button type="submit" disabled={saving} className="btn-primary">
          {saving ? 'Salvando...' : 'Cadastrar'}
        </button>
      </form>
    </div>
  );
}
