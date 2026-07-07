import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ReceiptScanner } from '../components/ReceiptScanner';
import { useGeolocation } from '../hooks/useGeolocation';
import { extractText, parseReceiptText } from '../services/ocr';
import { lookupMarketByCnpj, uploadReceipt, getNearbyMarkets } from '../services/api';
import type { ParsedReceiptItem, Market, ReceiptUploadResponse } from '../types';

type ScanStage = 'idle' | 'ocr_processing' | 'resolving_market' | 'reviewing' | 'submitting' | 'done' | 'error';

export const Scan = () => {
  const navigate = useNavigate();
  const { latitude, longitude } = useGeolocation();

  const [stage, setStage] = useState<ScanStage>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [ocrText, setOcrText] = useState('');
  const [cnpj, setCnpj] = useState<string | null>(null);
  const [items, setItems] = useState<ParsedReceiptItem[]>([]);
  const [resolvedMarket, setResolvedMarket] = useState<Market | null>(null);
  const [nearbyMarkets, setNearbyMarkets] = useState<Market[]>([]);
  const [result, setResult] = useState<ReceiptUploadResponse | null>(null);

  const handleCapture = async (imageDataUrl: string) => {
    setCapturedImage(imageDataUrl);
    setStage('ocr_processing');
    setErrorMessage(null);

    try {
      const text = await extractText(imageDataUrl);
      setOcrText(text);
      const parsed = parseReceiptText(text);
      setCnpj(parsed.cnpj);
      setItems(parsed.items);

      setStage('resolving_market');

      if (parsed.cnpj) {
        const market = await lookupMarketByCnpj(parsed.cnpj);
        if (market) {
          setResolvedMarket(market);
          setStage('reviewing');
          return;
        }
      }

      if (latitude !== null && longitude !== null) {
        const nearby = await getNearbyMarkets(latitude, longitude, 10);
        setNearbyMarkets(nearby);
      }
      setStage('reviewing');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Erro ao processar a nota fiscal');
      setStage('error');
    }
  };

  const updateItem = (index: number, updates: Partial<ParsedReceiptItem>) => {
    setItems((prev) => prev.map((item, i) => (i === index ? { ...item, ...updates } : item)));
  };

  const handleSubmit = async () => {
    if (!resolvedMarket || !capturedImage) return;

    setStage('submitting');
    setErrorMessage(null);

    try {
      const includedItems = items.filter((item) => item.include);
      const imageBlob = await (await fetch(capturedImage)).blob();

      const response = await uploadReceipt({
        image: imageBlob,
        marketId: resolvedMarket.id,
        items: includedItems.map(({ description, price }) => ({ description, price })),
        cnpj: cnpj ?? undefined,
        ocrText,
        latitude: latitude ?? undefined,
        longitude: longitude ?? undefined,
      });

      setResult(response);
      setStage('done');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Erro ao enviar a nota fiscal');
      setStage('error');
    }
  };

  const reset = () => {
    setStage('idle');
    setCapturedImage(null);
    setOcrText('');
    setCnpj(null);
    setItems([]);
    setResolvedMarket(null);
    setNearbyMarkets([]);
    setResult(null);
    setErrorMessage(null);
  };

  return (
    <div className="scan-page">
      <header className="scan-header">
        <button onClick={() => navigate('/')} className="btn-back">←</button>
        <h2>Escanear Nota Fiscal</h2>
      </header>

      {stage === 'idle' && <ReceiptScanner onCapture={handleCapture} />}

      {(stage === 'ocr_processing' || stage === 'resolving_market') && (
        <div className="processing-overlay">
          <div className="spinner"></div>
          <p>{stage === 'ocr_processing' ? 'Lendo nota fiscal...' : 'Identificando mercado...'}</p>
        </div>
      )}

      {stage === 'reviewing' && (
        <div className="result-container">
          <h3>Produtos Extraídos</h3>

          {!resolvedMarket && (
            <div className="market-selector">
              <label htmlFor="market-select">Não identifiquei o mercado pelo CNPJ. Selecione:</label>
              <select
                id="market-select"
                defaultValue=""
                onChange={(e) => {
                  const market = nearbyMarkets.find((m) => m.id === e.target.value);
                  setResolvedMarket(market ?? null);
                }}
              >
                <option value="" disabled>Escolha um mercado</option>
                {nearbyMarkets.map((market) => (
                  <option key={market.id} value={market.id}>{market.name}</option>
                ))}
              </select>
            </div>
          )}

          {resolvedMarket && <p className="resolved-market">Mercado: {resolvedMarket.name}</p>}

          {items.length === 0 && <p>Nenhum item reconhecido. Tente uma foto mais nítida.</p>}

          <ul className="extracted-items">
            {items.map((item, index) => (
              <li key={index} className="extracted-item review-item">
                <input
                  type="checkbox"
                  checked={item.include}
                  onChange={(e) => updateItem(index, { include: e.target.checked })}
                />
                <input
                  type="text"
                  value={item.description}
                  onChange={(e) => updateItem(index, { description: e.target.value })}
                />
                <input
                  type="number"
                  step="0.01"
                  value={item.price}
                  onChange={(e) => updateItem(index, { price: parseFloat(e.target.value) || 0 })}
                />
              </li>
            ))}
          </ul>

          <button
            className="btn-confirm"
            onClick={handleSubmit}
            disabled={!resolvedMarket || items.every((item) => !item.include)}
          >
            Confirmar e Enviar
          </button>
        </div>
      )}

      {stage === 'submitting' && (
        <div className="processing-overlay">
          <div className="spinner"></div>
          <p>Enviando nota fiscal...</p>
        </div>
      )}

      {stage === 'done' && result && (
        <div className="result-container">
          <h3>Nota fiscal processada!</h3>
          <p>{result.products_created} produto(s) novo(s) criado(s)</p>
          <p>{result.prices_created} preço(s) registrado(s)</p>
          <button className="btn-primary" onClick={reset}>Escanear outra nota</button>
        </div>
      )}

      {stage === 'error' && (
        <div className="result-container">
          <p className="error-message">{errorMessage}</p>
          <button className="btn-secondary" onClick={reset}>Tentar novamente</button>
        </div>
      )}
    </div>
  );
};
